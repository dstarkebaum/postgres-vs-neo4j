import subprocess
import argparse
import pathlib
import os
from contextlib import ExitStack
import time
from datetime import datetime
import py2neo
#default connection parameters

HOST='localhost',
USER='neo4j',
PASSWORD='password',
PORT=7687,
SCHEME='bolt',
SECURE=False,
MAX_CONNECTIONS=40

neo4j_headers = {}
neo4j_headers['papers'] = ['id:ID(Paper)','title','year:INT','doi',':LABEL']
neo4j_headers['is_cited_by'] = ['id:START_ID(Paper)','is_cited_by_id:END_ID(Paper)',':TYPE']
neo4j_headers['cites'] = ['id:START_ID(Paper)','cites_id:END_ID(Paper)',':TYPE']
neo4j_headers['authors'] = ['id:ID(Author)','name',':LABEL']
neo4j_headers['has_author'] = ['paper_id:START_ID(Paper)','author_id:END_ID(Author)',':TYPE']


tables = ['papers', 'is_cited_by', 'cites', 'authors', 'has_author']#, 'is_author_of']

def start_connection():
    graph = py2neo.Graph(
        host=HOST,
        user=USER,
        password=PASSWORD,
        port=PORT,
        scheme=SCHEME,
        secure=SECURE,
        max_connections=MAX_CONNECTIONS
        )
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


def verbose_query(graph, query):
    start=time.perf_counter()
    print(query)

    transation = graph.begin(autocommit=False)

    try:
        return_value = f(transaction, *args, **kwargs)
    except Exception as e:
        transaction.rollback()
        print(e)
        return None
    else:
        transaction.commit() # or maybe not
    return return_value

    cursor = graph.run(query):
    print("Execution time: "+str(time.perf_counter()-start))


def total_size(database):
    return database.store_file_sizes['TotalStoreSize']


def make_index(graph,label,properties):
    start=time.perf_counter()
    print("Making index on :"+label+' ('+','.join(properties)+')')

    graph.shema.create_index(label,properties)

    print("Execution time: "+str(time.perf_counter()-start))

#make_index(graph,label,property):
#    query='''CREATE INDEX ON :{l}({p})'''.format(l=label,p=property)


def make_all_indexes(graph):

    make_index(graph,':Author',['id(Author)'])
    make_index(graph,':Paper',['id(Paper)'])
#tables = ['papers', 'is_cited_by', 'cites', 'authors', 'has_author']#, 'is_author_of']


def delete_duplicate_relationships(transaction):
    transaction.run('''
            MATCH (a)-[r]->(b)
            WITH a, b, COLLECT(r) AS rr
            WHERE SIZE(rr) > 1
            WITH rr
            LIMIT 100000
            FOREACH (r IN TAIL(rr) | DELETE r);
            ''')

def make_cypher_queries(
        files,
        period=500,
        rows=100
    ):
    cypher = {}
    periodic_commit = ''

    if period > 0:
        periodic_commit = 'USING PERIODIC COMMIT {p}'.format(p=period)

    row_limit = ''
    if rows > 0:
        row_limit = 'WITH row limit {r}'.format(r=rows)


    cypher['constraints']='''
        CREATE CONSTRAINT ON (p:Paper) ASSERT p.id(Paper) IS UNIQUE;
        CREATE CONSTRAINT ON (a:Author) ASSERT a.id(Author) IS UNIQUE;
    '''

    cypher['paper']='''
        {per}
        LOAD CSV WITH HEADERS FROM "{filename}" AS row
        {with}
        MERGE (p:Paper {{ id(Paper):row[0] }}
        ON CREATE SET p.title = CASE trim(row.title) WHEN "" THEN null ELSE row.title END
        ON CREATE SET p.title = CASE trim(row.year) WHEN "" THEN null ELSE row.year END
        ON CREATE SET p.title = CASE trim(row.doi) WHEN "" THEN null ELSE row.doi END
    '''.format(per=periodic_commit,with=row_limit,filename=files['papers'])

    cypher['author']='''
        {per}
        LOAD CSV WITH HEADERS FROM "{filename}" AS row
        {with}
        MERGE (a:Author {{ id(Author):row[0] }}
        ON CREATE SET a.name = CASE trim(row.name) WHEN "" THEN null ELSE row.name END
    '''.format(per=periodic_commit,with=row_limit,filename=files['authors'])

    cypher['cites']='''
        {per}
        LOAD CSV WITH HEADERS FROM "{filename}" AS row
        {with}
        MATCH (p1:Paper {{id(Paper):row[0]}}),(p2:Paper {{id(Paper):row[1]}})
        MERGE (p1)->[:CITES]-(p2)
    '''.format(per=periodic_commit,with=row_limit,filename=files['cites'])

    cypher['is_cited_by']='''
        {per}
        LOAD CSV WITH HEADERS FROM "{filename}" AS row
        {with}
        MATCH (p1:Paper {{id(Paper):row[0]}}),(p2:Paper {{id(Paper):row[1]}})
        MERGE (p1)->[:IS_CITED_BY]-(p2)
    '''.format(per=periodic_commit,with=row_limit,filename=files['is_cited_by'])

    cypher['has_author']='''
        {per}
        LOAD CSV WITH HEADERS FROM "{filename}" AS row
        {with}
        MATCH (p:Paper {{id(Paper):row[0]}}),(a:Author {{id(Author):row[1]}})
        MERGE (p1)->[:HAS_AUTHOR]-(p2)
    '''.format(per=periodic_commit,with=row_limit,filename=files['is_cited_by'])

    return cypher

# This import loads one group of files at a time
def cypher_import(files):

    cypher = make_cypher_queries(files):

    for query in cypher:
        verbose_query(query)


# This import requires a complete dictionary of files all at once
# stored locally on disk, and is likely to run out of RAM for large imports
def admin_import(dict_of_csv_files):
    start_time = time.perf_counter()

    with ExitStack() as stack:
        stdout_log = stack.enter_context(open('logs/import_csv.stdout','w'))
        stderr_log = stack.enter_context(open('logs/import_csv.stderr','w'))
        timer = stack.enter_context(open('logs/import_csv.timer','a+'))
        stdout_log.write(datetime.now().strftime("%m/%d/%Y,%H:%M:%S")+
                ' Starting neo4j-admin import\n')
        stdout_log.write('Papers: '+ ','.join(dict_of_csv_files['papers'])+'\n')
        stdout_log.write('Authors: '+ ','.join(dict_of_csv_files['authors'])+'\n')
        stdout_log.write('CITES: '+ ','.join(dict_of_csv_files['cites'])+'\n')
        stdout_log.write('IS_CITED_BY: '+ ','.join(dict_of_csv_files['is_cited_by'])+'\n')
        stdout_log.write('HAS_AUTHOR: '+ ','.join(dict_of_csv_files['has_author'])+'\n')
        #stdout_log.write('IS_AUTHOR_OF: '+ ','.join(files['is_author_of'])+'\n')

        stderr_log.write(datetime.now().strftime("%m/%d/%Y,%H:%M:%S")+
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

        print(' 'join(bash_commands))
        subprocess.call(
                bash_commands,
                stdout=stdout_log,
                stderr=stderr_log
                )

        timer.write(','.join([
                    datetime.now().strftime("%m/%d/%Y,%H:%M:%S"),
                    str(len(dict_of_csv_files['papers'])),
                    str(time.perf_counter()-start_time)
                    ])+'\n'
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
