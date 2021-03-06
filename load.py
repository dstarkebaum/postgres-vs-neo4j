

import src.db_utils.populate_database as pop
import src.db_utils.postgres_utils as pgu

import os
import argparse

username = os.path.split(os.path.expanduser('~'))[-1]

def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('--s3_bucket',type=str,default='data-atsume-arxiv',
            help='The name of the S3 bucket where your JSON files are stored')
    parser.add_argument('--s3_path',type=str,default='open-corpus/2019-09-17',
            help='The subdirectory within your S3 bucket where the JSON files are stored')
    parser.add_argument('--corpus_path',type=str,default='data/s2-corpus',
            help='Directory to store the json corpus')
    parser.add_argument('--csv_path',type=str,default='data/csv',
            help='Directory to store the parsed csv files')
    parser.add_argument('--prefix',type=str,default='s2-corpus',
            help='filename prefix for csv files')
    parser.add_argument('--suffix',type=str,default='.csv',
            help='filename suffix for csv files')
    parser.add_argument('--start',type=int,default=0,
            help='file number to start with')
    parser.add_argument('--end',type=int,default=0,
            help='file number to end with (max=176)')
    parser.add_argument('--compress', action='store_true',
            help='choose if the source file is compressed (gz)')
    parser.add_argument('--engine',type=str,default='neo4j',
            help='choose database: postgres, psql, neo4j, or neo4j-admin')
    parser.add_argument('--easy',type=str,default='',
            help='choose: clean-post, test-post, test-neo4j, test-neo4j-admin, post, or neo4j for auto config')


    return parser.parse_args()

def main():
    args = parse_args()
    if args.easy == 'test-neo4j':

        # Be sure to clear out any previous database before you begin:
        # sudo rm -r /var/lib/neo4j/data/databases/graph.db

        pop.populate_database(
                #corpus_path='data/s2-corpus',
                #csv_path='data/csv',
                #prefix='s2-corpus',
                #suffix='.csv',
                start=0,
                end=1,
                compress=False,
                engine='neo4j',
                testing=True,
                cache=True,
                #use_previous=True,
                )
    elif args.easy == 'test-neo4j-admin':

        pop.populate_database(
                start=0,
                end=1,
                compress=False,
                engine='neo4j-admin',
                testing=True,
                cache=True,
                )
    elif args.easy == 'test-post':

        pop.populate_database(
                start=0,
                end=1,
                compress=False,
                engine='psql',
                make_int=True,
                testing=True,
                cache=True,
                database='local',
                )
        pgu.create_all_indexes(database='local')
        pgu.cleanup_database(database='local')

    elif args.easy == 'make-neo4j':

        pop.populate_database(
                start=0,
                end=176,
                compress=False,
                engine='neo4j',
                testing=False,
                cache=True)
    elif args.easy == 'neo4j-admin':

        pop.populate_database(
                start=0,
                end=176,
                compress=False,
                engine='neo4j-admin',
                testing=False,
                cache=True,
                )

    elif args.easy == 'make-post':

        pop.populate_database(
                start=0,
                end=2,
                compress=False,
                engine='psql',
                make_int=True,
                cache=True,
                #use_previous=True,
                testing=False,
                database='local'
                )
        pgu.create_all_indexes(database='local')
        pgu.cleanup_database(database='local')

    elif args.easy == 'clean-post':
        pgu.create_all_indexes(database='local')
        pgu.cleanup_database(database='local')
    else:
        # use all provided parameters
        pop.populate_database(
            corpus_path=args.corpus_path,
            csv_path=args.csv_path,
            prefix=args.prefix,
            suffix=args.suffix,
            start=args.start,
            end=args.end,
            compress=args.compress,
            engine=args.engine,
            make_int=args.make_int,
            cache=args.cache,
            use_previous=args.use_previous,
            database='local',
            s3_bucket=args.s3_bucket,
            s3_path=args.s3_path,
            )
            
        if 'postgres' == args.engine or 'psql' == args.engine:
            pgu.create_all_indexes(database='local')
            pgu.cleanup_database(database='local')




if __name__ == "__main__":
    main()
