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

'''
Decorator to handle database connections.
'''
def with_connection(f):
    def with_connection_(*args, **kwargs):
        return_value = None
        # or use a pool, or a factory function...
        graph = py2neo.Graph(
                host=HOST,
                user=USER,
                password=PASSWORD,
                port=PORT,
                scheme=SCHEME,
                secure=SECURE,
                max_connections=MAX_CONNECTIONS
                )

        return_value = f(graph, *args, **kwargs)
        return return_value

    return with_connection_

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

def total_size(database):
    return database.store_file_sizes['TotalStoreSize']

def make_index(graph,label,properties):
    graph.shema.create_index(label,properties)

@with_connection
def make_all_indexes(graph):

    make_index(graph,':Author','id')
    make_index(graph,':Paper','id')
    make_index(graph,':CITES','id')
    make_index(graph,':Author','id')
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


# def load_nodes_from_csv(transaction,filename,label):
#     q1='''
#             LOAD CSV WITH HEADERS FROM {filename} AS row
#             MERGE (l:{label} { id: row.id }
#             ON CREATE SET p.title = CASE trim(row.title) WHEN "" THEN null ELSE row.title END
#         '''
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


if __name__ == "__main__":
    main()
