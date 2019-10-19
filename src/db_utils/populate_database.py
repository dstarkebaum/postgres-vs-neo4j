import subprocess
import pathlib
import os
from contextlib import ExitStack
import time
from datetime import datetime
from . import json_to_csv
from . import postgres_utils
from . import neo4j_utils
#from setup import logger_config as log
import boto3

import logging
import sys
from datetime import datetime, timedelta

# setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# converter = lambda x, y: (
#     datetime.utcnow() - timedelta (
#         hours=7 if time.localtime().tm_isdst else 6)
#     ).timetuple()
# logging.Formatter.converter = converter

# make a handler that exports to a file
handler = logging.FileHandler('populate_database.log')
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(message)s')
handler.setFormatter(formatter)
# then add it to the logger
logger.addHandler(handler)

# log unhandled exceptions
def handle_unhandled_exception(exc_type, exc_value, exc_traceback):
    """Handler for unhandled exceptions that will write to the logs"""
    if issubclass(exc_type, KeyboardInterrupt):
        # if it's a ctl-C call the default excepthook saved at __excepthook__
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logger.critical("Unhandled exception", exc_info=(exc_type, exc_value, exc_traceback))

# tell the python interpreter to use my own exception handler (so it can be logged)
sys.excepthook = handle_unhandled_exception

json_to_csv.logger.addHandler(handler)
postgres_utils.logger.addHandler(handler)
neo4j_utils.logger.addHandler(handler)
#json_to_csv.logger.setLevel(logging.INFO)
#postgres_utils.logger.setLevel(logging.INFO)
#neo4j_utils.logger.setLevel(logging.INFO)

tables = ['papers', 'is_cited_by', 'cites', 'authors', 'has_author']#, 'is_author_of']


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
        make_int=False,
        cache=True,
        use_previous=False,
        database='local'):

    logger.info(os.getcwd())

    # loop through the list of normalized tables in our database
    collection_of_files = {}
    for i in range(start, end+1):

        files = {}
        if use_previous:

            json_local = '{path}/{prefix}-{num}.gz'.format(
                    path=corpus_path,
                    prefix=prefix,
                    num=str(i).zfill(3)
            )

            files = {t : json_to_csv.absolute_path(
                    t, csv_path, json_local, unique=True, compress=compress
                    ) for t in tables}
        else:
            files = download_and_extract_json(
                corpus_path=corpus_path,
                prefix=prefix,
                csv_path=csv_path,
                file_num=i,
                compress=compress,
                make_int=make_int,
                testing=testing,
                cache=cache,
                engine=engine,
            )

        if not cache and 'neo4j' == engine:
            logger.warning('Neo4j with no cache: Processing files one at a time')
            logger.warning('WARNING: Many relations will be missing because')
            logger.warning('they will not be created if one of the nodes is missing')
            neo4j_utils.cypher_import(files)

        elif 'psql' == engine:
            postgres_utils.psql_import(files, database)

        if cache:
            collection_of_files[i]=files
        else:
            for f in files:
                delete_file(files[f])
    if cache and 'neo4j' == engine:

        neo4j_utils.make_all_indexes()

        for i in range(start, end+1):
            neo4j_utils.make_nodes(collection_of_files[i])

        for i in range(start, end+1):
            neo4j_utils.make_relations(collection_of_files[i])

        neo4j_utils.delete_duplicate_relationships()

    if cache and 'neo4j-admin' == engine:
        headers = json_to_csv.make_neo4j_headers(corpus_path, csv_path)
        for i in range(start, end+1):
            print(collection_of_files[i])
        neo4j_utils.admin_import(collection_of_files, headers)

    #     else:
    #         for table in files:
    #             dict_of_csv_files[table]
    #


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
        make_int=False,
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
            make_int=make_int,
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

    if os.path.exists(destination):
        logger.info(destination + ' already exists')
    else:
        start_time = time.perf_counter()
        logger.info('Downloading from '+ source + ' to ' + destination)
        ensure_dir(destination)
        s3 = boto3.client('s3')
        bucket = 'data-atsume-arxiv'
        s3.download_file(bucket, source, destination)
        logger.info('Completed download in ' + str(time.perf_counter()-start_time)+'s')


def ensure_dir(file_path):
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)

def delete_file(filename):
    subprocess.call([ 'rm', '-r', filename ])

#def parse_json(corpus_path, output_dir, make_int=False,unique=False,neo4j=False,compress=False):
