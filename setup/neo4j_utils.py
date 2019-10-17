import subprocess
import argparse
import pathlib
import os
from contextlib import ExitStack
import time
from datetime import datetime
import py2neo
import logging
from setup import credentials
# setup logging

logger = logging.getLogger(__name__)

#default connection parameters


neo4j_headers = {}
neo4j_headers['papers'] = ['id:ID(Paper)','title','year:INT','doi',':LABEL']
neo4j_headers['is_cited_by'] = ['id:START_ID(Paper)','is_cited_by_id:END_ID(Paper)',':TYPE']
neo4j_headers['cites'] = ['id:START_ID(Paper)','cites_id:END_ID(Paper)',':TYPE']
neo4j_headers['authors'] = ['id:ID(Author)','name',':LABEL']
neo4j_headers['has_author'] = ['paper_id:START_ID(Paper)','author_id:END_ID(Author)',':TYPE']


tables = ['papers', 'is_cited_by', 'cites', 'authors', 'has_author']#, 'is_author_of']

def start_connection(database='local'):
    graph = py2neo.Graph(
            user=credentials.neo4j[database]['user'],
            password=credentials.neo4j[database]['pass'],
            host=credentials.neo4j[database]['host'],
            )
        # auth=AUTH,
        # user=USER,
        # password=PASSWORD,
        # port=PORT,
        # scheme=SCHEME
        # #secure=SECURE,
        # #max_connections=MAX_CONNECTIONS
        # )
    return graph



#Decorator to handle database connections.
# def with_connection(f):
#     def with_connection_(*args, **kwargs):
#         return_value = None
#         # or use a pool, or a factory function...
#         graph = py2neo.Graph(
#                 host=HOST,
#                 user=USER,
#                 password=PASSWORD,
#                 port=PORT,
#                 scheme=SCHEME,
#                 secure=SECURE,
#                 max_connections=MAX_CONNECTIONS
#                 )
#
#         return_value = f(graph, *args, **kwargs)
#         return return_value
#
#     return with_connection_
#
# def safe_commit(f):
#     def safe_commit_(*args, **kwargs):
#
#
#         transaction = graph.begin(autocommit=False)
#         try:
#             return_value = f(transaction, *args, **kwargs)
#         except Exception:
#             transaction.rollback()
#             print(f.__name__+" failed!")
#             raise
#         else:
#             transaction.commit() # or maybe not
#             print(f.__name__+" success!")
#         return return_value
#
#     return safe_commit_
#
# @with_connection

# This import loads one group of files at a time

def make_nodes(files):
    cypher = make_cypher_queries(files)

    graph = start_connection()

    if 'papers' in files:
        verbose_query(graph,cypher['papers'])
    if 'authors' in files:
        verbose_query(graph,cypher['authors'])


def make_relations(files):

    cypher = make_cypher_queries(files)

    graph = start_connection()

    if 'cites' in files:
        verbose_query(graph,cypher['cites'])
    if 'is_cited_by' in files:
        verbose_query(graph,cypher['is_cited_by'])
    if 'has_author' in files:
        verbose_query(graph,cypher['has_author'])

def cypher_import(files):

    cypher = make_cypher_queries(files)

    #graph = start_connection()
    graph = make_all_indexes()

    # make nodes
    if 'papers' in files:
        verbose_query(graph,cypher['papers'])
    if 'authors' in files:
        verbose_query(graph,cypher['authors'])

    # make relations
    if 'cites' in files:
        verbose_query(graph,cypher['cites'])
    if 'is_cited_by' in files:
        verbose_query(graph,cypher['is_cited_by'])
    if 'has_author' in files:
        verbose_query(graph,cypher['has_author'])
     # or maybe not


def make_cypher_queries(
        files,
        period=0,
        rows=0
    ):
    cypher = {}
    periodic_commit = ''

    if period > 0:
        periodic_commit = 'USING PERIODIC COMMIT {p}'.format(p=period)

    row_limit = ''
    if rows > 0:
        row_limit = 'WITH row limit {r}'.format(r=rows)


#    cypher['constraints']='''
#        CREATE CONSTRAINT ON (p:Paper) ASSERT p.id(Paper) IS UNIQUE;
#        CREATE CONSTRAINT ON (a:Author) ASSERT a.id(Author) IS UNIQUE;
#    '''

    if 'papers' in files:
        cypher['papers']='''
            {per}
            LOAD CSV WITH HEADERS FROM "{filename}" AS row
            FIELDTERMINATOR "|"
            {lim}
            MERGE (p:Paper {{ id:row.id }})
            ON CREATE SET p.title = CASE trim(row.title) WHEN "" THEN null ELSE row.title END
            ON CREATE SET p.year = CASE trim(row.year) WHEN "" THEN null ELSE row.year END
            ON CREATE SET p.doi = CASE trim(row.doi) WHEN "" THEN null ELSE row.doi END
        '''.format(per=periodic_commit,lim=row_limit,filename='file://'+files['papers'])

    if 'authors' in files:
        cypher['authors']='''
            {per}
            LOAD CSV WITH HEADERS FROM "{filename}" AS row
            FIELDTERMINATOR "|"
            {lim}
            MERGE (a:Author {{ id:row.id }})
            ON CREATE SET a.name = CASE trim(row.name) WHEN "" THEN null ELSE row.name END
        '''.format(per=periodic_commit,lim=row_limit,filename='file://'+files['authors'])

    if 'cites' in files:
        cypher['cites']='''
            {per}
            LOAD CSV WITH HEADERS FROM "{filename}" AS row
            FIELDTERMINATOR "|"
            {lim}
            MATCH (p1:Paper {{id:row.id}}),(p2:Paper {{id:row.outcit_id}})
            MERGE (p1)-[:CITES]->(p2)
        '''.format(per=periodic_commit,lim=row_limit,filename='file://'+files['cites'])

    if 'is_cited_by' in files:
        cypher['is_cited_by']='''
            {per}
            LOAD CSV WITH HEADERS FROM "{filename}" AS row
            FIELDTERMINATOR "|"
            {lim}
            MATCH (p1:Paper {{id:row.id}}),(p2:Paper {{id:row.incit_id}})
            MERGE (p1)-[:IS_CITED_BY]->(p2)
        '''.format(per=periodic_commit,lim=row_limit,filename='file://'+files['is_cited_by'])


    if 'has_author' in files:
        cypher['has_author']='''
            {per}
            LOAD CSV WITH HEADERS FROM "{filename}" AS row
            FIELDTERMINATOR "|"
            {lim}
            MATCH (p:Paper {{id:row.paper_id}}),(a:Author {{id:row.author_id}})
            MERGE (p)-[:HAS_AUTHOR]->(a)
        '''.format(per=periodic_commit,lim=row_limit,filename='file://'+files['has_author'])

    return cypher



def return_query(graph, query):

    start=time.perf_counter()
    logger.info(query)
    transaction = graph.begin(autocommit=False)

    try:
        cursor = transaction.run(query)
    except Exception as e:
        transaction.rollback()
        logger.info(e)
        return None
    finally:
        transaction.commit() # or maybe not
        logger.info("Execution time: "+str(time.perf_counter()-start))

    return dict(
            time = (time.perf_counter()-start),
            results = [record.values() for record in cursor]
            )

def verbose_query(graph, query):

    start=time.perf_counter()

    logger.info(query)
    transaction = graph.begin(autocommit=False)
    try:
        cursor = transaction.run(query)
    except Exception as e:
        transaction.rollback()
        logger.info(e)
        return None
    finally:
        transaction.commit() # or maybe not
        stats = cursor.stats()
        for key in stats:
            logger.info(key + ": "+ str(stats[key]))
        logger.info("Execution time: "+str(time.perf_counter()-start))

    return cursor


def total_size(database):
    return database.store_file_sizes['TotalStoreSize']


def make_index(graph,label,property):
    start=time.perf_counter()
    logger.info("Making index on :"+label+' ('+property+')')

    graph.schema.create_uniqueness_constraint(label,property)
    #graph.schema.create_index(label,property)

    logger.info("Execution time: "+str(time.perf_counter()-start))

#make_index(graph,label,property):
#    query='''CREATE INDEX ON :{l}({p})'''.format(l=label,p=property)


def make_all_indexes():
    graph = start_connection()
    make_index(graph,'Author','id')
    make_index(graph,'Paper','id')
    return graph
#tables = ['papers', 'is_cited_by', 'cites', 'authors', 'has_author']#, 'is_author_of']


def delete_duplicate_relationships():
    graph = start_connection()
    # Gather all of the relations between nodes
    # collect the relations that have the same source and destination nodes
    # then for any collection bigger than size(1):
    # delete all but the first entry in each collection
    query = '''
            MATCH (a)-[r]->(b)
            WITH a, b, COLLECT(r) AS relations
            WHERE SIZE(relations) > 1
            WITH relations
            FOREACH (r IN TAIL(relations) | DELETE r);
            '''
    verbose_query(graph,query)

def log_subprocess_output(pipe):
    for line in iter(pipe.readline, b''): # b'\n'-separated lines
        logger.info('subprocess: %r', line)

# This import requires a complete dictionary of files all at once
# stored locally on disk, and is likely to run out of RAM for large imports
def admin_import(dict_of_csv_files):
    start_time = time.perf_counter()

    with ExitStack() as stack:
        stdout_log = stack.enter_context(open('logs/import_csv.stdout','w'))
        stderr_log = stack.enter_context(open('logs/import_csv.stderr','w'))
        timer = stack.enter_context(open('logs/import_csv.timer','a+'))
        logger.info(datetime.now().strftime("%m/%d/%Y,%H:%M:%S")+
                ' Starting neo4j-admin import\n')
        logger.info('Papers: '+ ','.join(dict_of_csv_files['papers'])+'\n')
        logger.info('Authors: '+ ','.join(dict_of_csv_files['authors'])+'\n')
        logger.info('CITES: '+ ','.join(dict_of_csv_files['cites'])+'\n')
        logger.info('IS_CITED_BY: '+ ','.join(dict_of_csv_files['is_cited_by'])+'\n')
        logger.info('HAS_AUTHOR: '+ ','.join(dict_of_csv_files['has_author'])+'\n')
        #stdout_log.write('IS_AUTHOR_OF: '+ ','.join(files['is_author_of'])+'\n')

        logger.info(datetime.now().strftime("%m/%d/%Y,%H:%M:%S")+
                ' Starting neo4j-admin import')

        bash_commands= [
                    'neo4j-admin',
                    'import',
                    '--ignore-duplicate-nodes',
                    '--ignore-missing-nodes',
                    '--delimiter', '|',
                    '--report-file=logs/neo4j.report',
                    '--nodes:Paper', ','.join(dict_of_csv_files['papers']),
                    '--nodes:Author', ','.join(dict_of_csv_files['authors']),
                    '--relationships:CITES', ','.join(dict_of_csv_files['cites']),
                    '--relationships:IS_CITED_BY', ','.join(dict_of_csv_files['is_cited_by']),
                    '--relationships:HAS_AUTHOR', ','.join(dict_of_csv_files['has_author'])
                    #'--relationships:IS_AUTHOR_OF',
                    #','.join(files['is_author_of'])
                    ]

        logger.info(' '.join(bash_commands))

        pipe = subprocess.call(
                bash_commands,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                )

        log_subprocess_output(pipe)

        logger.info(
                "Number of files: "+str(len(dict_of_csv_files['papers']))+\
                ", processing time: "+str(time.perf_counter()-start_time)
                )

# def find_largest_groups():
#     q1='''
#     CALL algo.unionFind('', '',
#             {write:true, partitionProperty:"partition"}
#         ) YIELD nodes RETURN *
#     '''
#     q2='''
#     // call unionFind procedure
#     CALL algo.unionFind.stream('', '', {})
#     YIELD nodeId,setId
#     // groupBy setId, storing all node ids of the same set id into a list
#     WITH setId, collect(nodeId) as nodes
#     // order by the size of nodes list descending
#     ORDER BY size(nodes) DESC
#     LIMIT 3 // limiting to 3
#     RETURN setId, nodes
#     '''

#// call unionFind procedure
#CALL algo.unionFind.stream('', '', {})
#YIELD nodeId,setId
#// groupBy setId, storing all node ids of the same set id into a list
#WITH setId, collect(nodeId) as nodes
#// order by the size of nodes list descending
#ORDER BY size(nodes) DESC
#LIMIT 3 // limiting to 3
#RETURN setId, nodes

# neo4j_headers['papers'] = ['id:ID(Paper)','title','year:INT','doi',':LABEL']
# neo4j_headers['is_cited_by'] = ['id:START_ID(Paper)','is_cited_by_id:END_ID(Paper)',':TYPE']
# neo4j_headers['cites'] = ['id:START_ID(Paper)','cites_id:END_ID(Paper)',':TYPE']
# neo4j_headers['authors'] = ['id:ID(Author)','name',':LABEL']
# neo4j_headers['has_author'] = ['paper_id:START_ID(Paper)','author_id:END_ID(Author)',':TYPE']

    # create_index('papers',['id'],unique=True,primary=True)
    # create_index('paper_authors',['author_id'])
    # create_index('paper_authors',['paper_id'])
    #
    # remove_duplicates('incits',['id','incit_id'])
    # remove_duplicates('outcits',['id','outcit_id'])
    #
    # create_index('incits',['id'])
    # create_index('outcits',['id'])
    #
    # create_index('authors',['name'],gin=True)
    # create_index('papers',['title'],gin=True,gin_type='vector')


#     q2='''
#             MATCH (a:{start_label})-[r:{rel_type}]->(b:{end_label})
#             WHERE a.id = line["START_ID"]
#             AND b.id = line["END_ID"]
#
#             WITH collect(f) AS rels
#             WHERE size(rels) > 1
#             UNWIND tail(rels) as t
#             DELETE t
#         '''


# DEPRACATED: redundant with json_to_csv.absolute_path
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
    pass
#    args = parse_args()
#    print(os.getcwd())
#    files = {t : path_list(t,args.path,args.prefix,args.suffix,args.start,args.end,args.compress) for t in tables}
#    import_csv(files)

if __name__ == "__main__":
    main()
