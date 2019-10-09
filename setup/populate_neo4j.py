import subprocess
import argparse
import pathlib
import os
from contextlib import ExitStack
import time
from datetime import datetime
from setup import json_to_csv
from setup import postgres_utils
import boto3


# NOTE: This script must be run as sudo (or as user neo4j)
# It will not work if your database is already populated and/or running
# Start by checking: neo4j status
# If it is running:
# sudo neo4j stop
# Then delete (or backup) the current database:
# sudo rm -r /var/lib/neo4j/data/databases/graph.db

# Ex: import just one set of compressed csv files in data/csv/s2-corpus-001-[table].csv.gz:
# sudo python3 neo4j/neo4j_import.py data/csv --compress --start 1 --end 1

# If you have any troubles with importing, check the logfiles:
# nano /var/log/neo4j/neo4j.log
# Also, check the logfiles for this script at:
# nano logs/import_csv.stderr
# nano logs/import_csv.stdout
# nano logs/import_csv.timer

# Once everything is complete, you may need to start neo4j using systemctl:
# sudo systemctl start neo4j

tables = ['papers', 'is_cited_by', 'cites', 'authors', 'has_author']#, 'is_author_of']

neo4j_headers = {}
neo4j_headers['papers'] = ['id:ID(Paper)','title','year:INT','doi',':LABEL']
neo4j_headers['is_cited_by'] = ['id:START_ID(Paper)','is_cited_by_id:END_ID(Paper)',':TYPE']
neo4j_headers['cites'] = ['id:START_ID(Paper)','cites_id:END_ID(Paper)',':TYPE']
neo4j_headers['authors'] = ['id:ID(Author)','name',':LABEL']
neo4j_headers['has_author'] = ['paper_id:START_ID(Paper)','author_id:END_ID(Author)',':TYPE']


host_config = {
    'HOST':'localhost',
    'DATABASE':'ubuntu',
    'USER':'ubuntu',
    'PASSWORD':'ubuntu'
    }


def ensure_dir(file_path):
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)

def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('corpus_path',type=str,
            help='Directory of the json corpus')
    parser.add_argument('csv_path',type=str,
            help='Directory of the parsed csv files')
    parser.add_argument('--start',type=int,default=0,
            help='file number to start with')
    parser.add_argument('--end',type=int,default=0,
            help='file number to start with')
    parser.add_argument('--prefix',type=str,default='s2-corpus',
            help='filename prefix for csv files')
    parser.add_argument('--suffix',type=str,default='.csv',
            help='filename suffix for csv files')
    parser.add_argument('--compress', action='store_true',
            help='choose if the source file is compressed (gz)')

    return parser.parse_args()

def main():
    args = parse_args()
    populate_neo4j(
        args.corpus_path,
        args.csv_path,
        args.prefix,
        args.suffix,
        args.start,
        args.end,
        args.compress
    )

def populate_database(
        corpus_path='data/s2-corpus',
        csv_path='data/csv',
        prefix='s2-corpus',
        suffix='.csv',
        start=0,
        end=0,
        compress=True,
        engine='neo4j'):

    print(os.getcwd())


    # create a dictionary of path names
    csv_files = {t : path_list(
                t, csv_path, prefix, suffix, start, end, compress
            ) for t in tables}

    missing_file = False
    for table in csv_files:
        for file in csv_files[table]:
            if not os.path.exists(file):
                missing_file = True
                print('Missing: ' + file)
            else:
                print(file + ' exists already')

    if missing_file:
        print('compress = ' + str(compress))

        download_and_extract_json(
            corpus_path=corpus_path,
            prefix=prefix,
            csv_path=csv_path,
            start=start,
            end=end,
            compress=compress)
    if engine == 'neo4j':
        import_csv(csv_files)
    else:
        import_postgres(csv_files)

def import_portgres(csv_files):
    for table in csv_files:
        subprocess.call([
                'psql',
                '-h', host_config['HOST'],
                '-d', host_config['DATABASE'],
                '-U', host_config['USER'],
                '-c',   """
                        \\copy {table}({headers})
                        FROM {file}
                        WITH (FORMAT CSV, HEADER, DELIMITER '|')
                        """.format(table=table,file=csv_files[table])

# load_csv "papers" "id, title, year, doi"
# load_csv "inCits" "id, inCit_id"
# load_csv "outCits" "id, outCit_id"
# load_csv "authors" "id, name"
# load_csv "paper_authors" "paper_id, author_id"


    ])



# Download a single zipped json from S3
def download_from_s3(
        i=0,
        corpus_path='data/s2-corpus',
        prefix='s2-corpus',
        bucket='data-atsume-arxiv'):

    source = 'open-corpus/2019-09-17/{prefix}-{num}.gz'.format(
            prefix=prefix,
            num=str(i).zfill(3)
            )

    destination = '{path}/{prefix}-{num}.gz'.format(
            path=corpus_path,
            prefix=prefix,
            num=str(i).zfill(3)
            )

    s3 = boto3.client('s3')

    if not os.path.exists(destination):
        start_time = time.perf_counter()
        print('Downloading from '+ source + ' to ' + destination)
        ensure_dir(destination)
        s3.download_file(bucket, source, destination)
        print('Completed download in ' + str(time.perf_counter()-start_time)+'s')
    else:
        print(destination + ' already exists')


def delete_json(filename):
    subprocess.call([ 'rm', '-r', filename ])

def download_and_extract_json(
        corpus_path='data/s2-corpus',
        prefix='s2-corpus',
        csv_path='data/csv',
        start=0,
        end=0,
        compress=True):

    suffix = ''
    if compress:
        suffix = '.gz'

    for i in range(start,end+1):

        download_from_s3(i)
        start=time.perf_counter()

        print('compress = ' + str(compress))
        padded_i = str(i).zfill(3)
        json_to_csv.parse_json(
                '{dir}/{pre}-{num}{suf}'.format(
                    dir=corpus_path,
                    pre=prefix,
                    num=padded_i,
                    suf=suffix
                    ),
                csv_path,
                make_int=False,
                unique=True,
                neo4j=True,
                compress=compress
                )

        #delete_json('{dir}/{prefix}-{num}{suf}'.format(
        #        dir=corpus_path,
        #        prefix=prefix,
        #        num=padded_i,
        #        suf=suffix
        #        ))

#def parse_json(corpus_path, output_dir, make_int=False,unique=False,neo4j=False,compress=False):

def path_list(table,csv_path,prefix,suffix,start,end,compress):
    if compress:
        suffix=suffix+'.gz'

    return ['{dir}/{pre}-{num}-{tab}{suf}'.format(
                dir=csv_path,
                pre=prefix,
                num=str(i).zfill(3),
                tab=table,
                suf=suffix
                )
            for i in range(start, end+1) ]


def import_csv(files):
    start_time = time.perf_counter()

    with ExitStack() as stack:
        stdout_log = stack.enter_context(open('logs/import_csv.stdout','w'))
        stderr_log = stack.enter_context(open('logs/import_csv.stderr','w'))
        timer = stack.enter_context(open('logs/import_csv.timer','a+'))
        stdout_log.write(datetime.now().strftime("%m/%d/%Y,%H:%M:%S")+
                ' Starting neo4j-admin import\n')
        stdout_log.write('Papers: '+ ','.join(files['papers'])+'\n')
        stdout_log.write('Authors: '+ ','.join(files['authors'])+'\n')
        stdout_log.write('CITES: '+ ','.join(files['cites'])+'\n')
        stdout_log.write('IS_CITED_BY: '+ ','.join(files['is_cited_by'])+'\n')
        stdout_log.write('HAS_AUTHOR: '+ ','.join(files['has_author'])+'\n')
        #stdout_log.write('IS_AUTHOR_OF: '+ ','.join(files['is_author_of'])+'\n')

        stderr_log.write(datetime.now().strftime("%m/%d/%Y,%H:%M:%S")+
                ' Starting neo4j-admin import')
        neo4j_admin_import(files,stdout_log,stderr_log)
        timer.write(','.join([
                    datetime.now().strftime("%m/%d/%Y,%H:%M:%S"),
                    str(len(files['papers'])),
                    str(time.perf_counter()-start_time)
                    ])+'\n'
                )


def neo4j_admin_import(files, stdout_log,stderr_log):
    subprocess.call([
                'neo4j-admin',
                'import',
                '--ignore-duplicate-nodes',
                '--ignore-missing-nodes',
                '--delimiter',
                '|',
                '--report-file=logs/neo4j.report',
                '--nodes:Paper',
                ','.join(files['papers']),
                '--nodes:Author',
                ','.join(files['authors']),
                '--relationships:CITES',
                ','.join(files['cites']),
                '--relationships:IS_CITED_BY',
                ','.join(files['is_cited_by']),
                '--relationships:HAS_AUTHOR',
                ','.join(files['has_author'])
                #'--relationships:IS_AUTHOR_OF',
                #','.join(files['is_author_of'])
            ],
            stdout=stdout_log,
            stderr=stderr_log
    )


if __name__ == "__main__":
    main()
