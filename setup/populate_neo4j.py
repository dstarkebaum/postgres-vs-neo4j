import subprocess
import argparse
import pathlib
import os
from contextlib import ExitStack
import time
from datetime import datetime
from . import parse_json as parse_json
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


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('path',type=str,
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
    print(os.getcwd())


    # create a dictionary of path names
    files = {t : path_list(
                t,
                args.path,
                args.prefix,
                args.suffix,
                args.start,
                args.end,
                args.compress
            ) for t in tables}

    missing_file = False
    for file in files:
        if not os.path.exists(file):
            missing_file = True
            print('Missing: ' + file)

    if missing_file:
        download_and_extract_json(
            path='data/s2-corpus',
            prefix=args.prefix,
            output=args.path,
            start=args.start,
            end=args.end,
            compress=args.compress)

    import_csv(files)


# Download a single zipped json from S3
def download_from_s3(num,path='data/s2-corpus',prefix='s2-corpus',bucket='data-atsume-arxiv'):

    source_file = 'open-corpus/2019-09-17/{prefix}-{num}.gz'.format(
            prefix=prefix,num=num)
    destination = '{path}/{prefix}-{num}.gz'.format(
            prefix=prefix,num=num)

    s3 = boto3.client('s3')
    start_time = time.perf_counter()
    print('Downloading '+source_file + ' to ' + destination)
    s3.download_file(
            bucket,
            source_file,
            destination
            )
    print('Completed download in ' + str(time.perf_counter()-start_time)+'s')

def delete_json(filename):
    subprocess.call([ 'rm', '-r', filename ])

def download_and_extract_json(
        path='data/s2-corpus',
        prefix='s2-corpus',
        output='data/csv',
        start=0,
        end=0,
        compress=True):
    for i in range(start,stop+1):
        download_from_s3(i)
        parse_json('{dir}/{pre}-{num}'.format(
                    dir=path,
                    pre=prefix,
                    num=str(i).zfill(3)),
                output,
                make_int=False,
                unique=True,
                neo4j=True,
                compress=compress
                )
        delete_json('{path}/{prefix}-{num}.gz'.format(
                prefix=prefix,num=i))

#def parse_json(corpus_path, output_dir, make_int=False,unique=False,neo4j=False,compress=False):

def path_list(table,path,prefix,suffix,start,end,compress):
    if compress:
        suffix=suffix+'.gz'

    return ['{dir}/{pre}-{num}-{tab}{suf}'.format(
                dir=path,
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
        timer.write(','.join([
                datetime.now().strftime("%m/%d/%Y,%H:%M:%S"),
                str(len(files['papers'])),
                str(time.perf_counter()-start_time)
        ]))


if __name__ == "__main__":
    main()
