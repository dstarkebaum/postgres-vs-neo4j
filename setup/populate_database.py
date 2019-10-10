import subprocess
import argparse
import pathlib
import os
from contextlib import ExitStack
import time
from datetime import datetime
from setup import json_to_csv
from setup import postgres_utils
from setup import neo4j_utils
import boto3


tables = ['papers', 'is_cited_by', 'cites', 'authors', 'has_author']#, 'is_author_of']

def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('corpus_path',type=str,default='data/s2-corpus',
            help='Directory to store the json corpus')
    parser.add_argument('csv_path',type=str,default='data/csv',
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


    return parser.parse_args()

def main():
    args = parse_args()
    populate_database(
        args.corpus_path,
        args.csv_path,
        args.prefix,
        args.suffix,
        args.start,
        args.end,
        args.compress,
        arg.engine
    )


# DEPRACATED: redundant with json_to_csv.absolute_path
def csv_filename(table,directory,prefix,suffix,number,compress):
    if compress:
        suffix=suffix+'.gz'
    # return a formatted file name
    return '{dir}/{pre}-{num}-{tab}{suf}'.format(
                dir=directory,
                pre=prefix,
                num=str(number).zfill(3),
                tab=table,
                suf=suffix)

# Main method of this module
def populate_database(
        corpus_path='data/s2-corpus',
        csv_path='data/csv',
        prefix='s2-corpus',
        suffix='.csv',
        start=0,
        end=0,
        compress=True,
        engine='neo4j',
        testing=True,
        cache=True):

    print(os.getcwd())

    # create a dictionary of path names
    #        {t : path_list(
    #            t, csv_path, prefix, suffix, start, end, compress
    #        ) for t in tables }

    #missing_file = False

    # loop through the list of normalized tables in our database
    collection_of_files = {}
    for i in range(start, end+1):

        files = download_and_extract_json(
            corpus_path=corpus_path,
            prefix=prefix,
            csv_path=csv_path,
            file_num=i,
            compress=compress,
            testing=testing,
            cache=cache)

        if not cache and 'neo4j' == engine:
            print('Neo4j with no cache: Processing files one at a time')
            print('WARNING: Many relations will be missing because')
            print('they will not be created if one of the nodes is missing')
            neo4j_utils.cypher_import(files)

        elif 'psql' == engine:
            postgres_utils.psql_import(files)

        if cache:
            collection_of_files[i]=files
        else:
            for f in files:
                delete_file(files[f])
    if cache and 'neo4j' == engine:

        for i in range(start, end+1):
            neo4j_utils.make_nodes(collection_of_files[i])

        neo4j_utils.make_all_indexes()

        for i in range(start, end+1):
            neo4j_utils.make_relations(collection_of_files[i])

        neo4j_utils.delete_duplicate_relationships()

    #     else:
    #         for table in files:
    #             dict_of_csv_files[table]
    #
    # if 'neo4j-admin' == engine:
    #     neo4j_utils.admin_import(dict_of_csv_files)


            #file = csv_filename(t, csv_path, prefix, suffix, i, compress)
            #if not os.path.exists(file):
            #    missing_file = True
            #    print('Missing: ' + file)
            #else:
            #    print(file + ' exists already')
    #if missing_file:
    #    print('compress = ' + str(compress))




# load_csv "papers" "id, title, year, doi"
# load_csv "inCits" "id, inCit_id"
# load_csv "outCits" "id, outCit_id"
# load_csv "authors" "id, name"
# load_csv "paper_authors" "paper_id, author_id"

def download_and_extract_json(
        corpus_path='data/s2-corpus',
        prefix='s2-corpus',
        csv_path='data/csv',
        file_num=0,
        compress=True,
        testing=True,
        cache=True,
        engine='neo4j'):

    json_s3 = 'open-corpus/2019-09-17/{prefix}-{num}.gz'.format(
            prefix=prefix,
            num=str(file_num).zfill(3)
            )

    json_local = '{path}/{prefix}-{num}.gz'.format(
            path=corpus_path,
            prefix=prefix,
            num=str(file_num).zfill(3)
            )

    download_from_s3(json_s3, json_local)

    use_admin_headers = False
    if 'neo4j-admin' == engine:
        use_admin_headers = True

    csv_files = json_to_csv.parse_json(
            json_local,
            csv_path,
            make_int=False,
            unique=True,
            neo4j=use_admin_headers,
            compress=compress,
            testing=testing
            )
    if not cache:
        delete_file(json_local)
    # return the list of filenames for futher processing!
    return csv_files


# Download a single zipped json from S3
def download_from_s3(source, destination):

    s3 = boto3.client('s3')
    bucket = 'data-atsume-arxiv'
    if os.path.exists(destination):
        print(destination + ' already exists')
    else:
        start_time = time.perf_counter()
        print('Downloading from '+ source + ' to ' + destination)
        ensure_dir(destination)
        s3.download_file(bucket, source, destination)
        print('Completed download in ' + str(time.perf_counter()-start_time)+'s')


def ensure_dir(file_path):
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)

def delete_file(filename):
    subprocess.call([ 'rm', '-r', filename ])

#def parse_json(corpus_path, output_dir, make_int=False,unique=False,neo4j=False,compress=False):

if __name__ == "__main__":
    main()
