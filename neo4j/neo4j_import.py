import subprocess
import argparse
import pathlib
import os
from contextlib import ExitStack
import time
from datetime import datetime
#default connection parameters

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
            help='filename prefix for csv files')
    parser.add_argument('--compress', action='store_true',
            help='choose if the source file is compressed (gz)')

    return parser.parse_args()

def main():
    args = parse_args()
    print(os.getcwd())
    files = {t : path_list(t,args.path,args.prefix,args.suffix,args.start,args.end,args.compress) for t in tables}
    import_csv(files)

def path_list(table,path,prefix,suffix,start,end,compress):
    if compress:
        suffix=suffix+'.gz'
    return ['{dir}/{pre}-{num}-{tab}{suf}'.format(
            dir=path,
            pre=prefix,
            num=str(x).zfill(3),
            tab=table,
            suf=suffix)
            for x in range(start,end+1)]


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
