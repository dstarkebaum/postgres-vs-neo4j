#!/usr/bin/env python2.7

import psycopg2
import os
import time
import subprocess
import logging

logger = logging.getLogger(__name__)

#from setup import host_config
#def main(host='localhost',database='ubuntu',user='ubuntu',password='ubuntu'):

# host_config = {
#     'HOST':'localhost',
#     'DATABASE':'ubuntu',
#     'USER':'ubuntu',
#     'PASSWORD':'ubuntu'
#     }

host_config = {
    'HOST':'localhost',
    'DATABASE':'david',
    'USER':'david',
    'PASSWORD':'david'
    }

headers = {}
headers['papers'] = ('id','title','year','doi')
headers['is_cited_by'] = ('id','incit_id')
headers['cites'] = ('id','outcit_id')
headers['authors'] = ('id','name')
headers['has_author'] = ('paper_id','author_id')


#Decorator to handle database connections.
def with_connection(f):
    def with_connection_(*args, **kwargs):
        # or use a pool, or a factory function...
        connection = psycopg2.connect('''
                host={h} dbname={db} user={u} password={pw}
                '''.format(
                        h=host_config['HOST'],
                        db=host_config['DATABASE'],
                        u=host_config['USER'],
                        pw=host_config['PASSWORD'])
                )
        try:
            return_value = f(connection, *args, **kwargs)
        except Exception:
            connection.rollback()
            logger.info(f.__name__+" failed!")
            raise
        else:
            connection.commit() # or maybe not
            logger.info(f.__name__+" success!")
        finally:
            connection.close()

        return return_value

    return with_connection_


def verbose_query(cursor, query):
    start=time.perf_counter()
    logger.info(cursor.mogrify(query).decode('utf-8'))
    try:
        cursor.execute(query)
        for record in cursor:
            logger.info(str(record))
    except (psycopg2.ProgrammingError, psycopg2.errors.DuplicateTable) as error:
        logger.info(error)

    logger.info("Execution time: "+str(time.perf_counter()-start))


@with_connection
def vacuum_table(connection,table,analyze=True,verbose=True):
    cursor=connection.cursor()
    connection.set_session(autocommit=True)
    ana=''
    if analyze:
        ana=', ANALYZE'
    verb=''
    if verbose:
        verb=', VERBOSE'
    query='''
        VACUUM(FULL{a}{v}) {t}
    '''.format(a=ana,v=verb,t=table)

    verbose_query(cursor,query)
    connection.set_session(autocommit=False)


@with_connection
def remove_duplicates_faster(connection,table,columns):
    cursor = connection.cursor()
    start=time.perf_counter()
    # build up combined conditions from multiple columns
    conditions = ''.join(
            [' AND a.{c} = b.{c}'.format(c=col) for col in columns]
            )
    query = '''
            DELETE FROM {t} a USING {t} b
            WHERE a.ctid < b.ctid
            '''.format(t=table) + conditions + ';'

    verbose_query(cursor, query)

    logger.info(str(time.perf_counter()-start) + " s to remove duplicates " +
            "from {t}({c})".format(t=table,c=','.join(columns))
            )


@with_connection
def remove_duplicates_faster(connection,table,column):
    cursor = connection.cursor()
    start=time.perf_counter()
    # build up combined conditions from multiple columns
    query = '''
        DELETE FROM {t} a USING (
            SELECT MIN(ctid) as ctid, {c}
                FROM {t}
                GROUP BY {c} HAVING COUNT(*) > 1
        ) b
        WHERE a.{c} = b.{c}
        AND a.ctid <> b.ctid;
    '''.format(t=table,c=column)

    verbose_query(cursor, query)

    logger.info(str(time.perf_counter()-start) + " s to remove duplicates " +
            "from {t}({c})".format(t=table,c=','.join(columns))
            )



@with_connection
def create_index(
        connection,
        table,
        columns,
        unique=False,
        primary=False,
        gin=False,
        gin_type='trigram',
        explain=False,
        analyze=False
        ):

    cursor = connection.cursor()
    start=time.perf_counter()

    cols=''

    # https://hashrocket.com/blog/posts/exploring-postgres-gin-index
    # CREATE INDEX table_index ON table USING gin (first_name gin_trgm_ops, last_name gin_trgm_ops);
    gi=''
    if gin:
        gi=' USING GIN'
        gin_cols = []
        for col in columns:
            if ('trigram'==gin_type or 'trgm'==gin_type):
                gin_cols.append('{c} gin_trgm_ops'.format(c=col))
            elif ('vector'==gin_type or 'vec'==gin_type):
                gin_cols.append("to_tsvector('simple', {c})".format(c=col))
            else:
                logger.info("Ignoring invalid gin_type: " + gin_type)
        cols = ', '.join(gin_cols)
    else:
        cols = ', '.join(columns)

    index= 'index_{t}_{c_o_l}'.format(
            t=table,c_o_l='_'.join(columns)
            )

    exp=''
    if explain:
        exp='EXPLAIN '

    ana=''
    if analyze:
        ana='ANALYZE '

    uni=''
    if unique:
        uni='UNIQUE '

    query = '''
            {e}{a}CREATE {u}INDEX {i} ON {t}{g} ({c});
            '''.format(e=exp,a=ana,u=uni,t=table,c=cols,i=index,g=gi)

    verbose_query(cursor, query)

    #print(str(time.perf_counter()-start) +
    #        "s to create index on " +
    #        "{t}({c})".format(t=table,c=','.join(columns))
    #        )
    return index
    #if unique and primary:
    #    set_primary_key(table,index)

@with_connection
def set_primary_key(
        connection,
        table,
        index,
        explain=False,
        analyze=False
        ):
    cursor = connection.cursor()

    start=time.perf_counter()
    exp=''
    if explain:
        exp='EXPLAIN '

    ana=''
    if analyze:
        ana='ANALYZE '

    query='''
    {e}{a}ALTER TABLE {t} ADD PRIMARY KEY USING INDEX {i};
    '''.format(e=exp,a=ana,t=table,i=index)

    verbose_query(cursor, query)

    logger.info(str(time.perf_counter()-start) +
            "s to set primary key on " +
            "{i}".format(i=index)
            )


def load_csv(file,table,headers,cursor):
    delimiter = '|'
    heads = ','.join(headers)

    query = """
            COPY {t}({h}) FROM '{f}' DELIMITER '{d}' CSV HEADER;
            """.format(f=file,d=delimiter,t=table,h=heads)

    verbose_query(cursor, query)


def cleanup_database():
    remove_duplicates_faster('authors','id')#,explain=True)
    #set_primary_key('authors',index)
    remove_duplicates_faster('papers','id')#,explain=True)
    #set_primary_key('papers',index)
    #remove_duplicates('incits',['id','incit_id'])
    #remove_duplicates('outcits',['id','outcit_id'])
    vacuum_table('authors')
    vacuum_table('papers')
    vacuum_table('outcits')
    vacuum_table('incits')
    vacuum_table('has_author')

def creat_all_indexes():

    # TODO --> DONE: Create index on authors and paper_authors and remove duplicate rows
    # get list of tables and columns in schema
    #'''select table_schema, table_name, column_name
    #from information_schema.columns
    #where table_schema not in ('pg_catalog','information_schema')
    #order by 1,2,3


    index = create_index('authors',['id'])#,unique=True,primary=True)#,explain=True)

    create_index('papers',['id'])#,unique=True,primary=True)
    create_index('paper_authors',['author_id'])
    create_index('paper_authors',['paper_id'])


    create_index('incits',['id'])
    create_index('outcits',['id'])

    create_index('authors',['name'],gin=True)
    create_index('papers',['title'],gin=True,gin_type='vector')




def psql_import(csv_files):
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
                        """.format(table=table,file=csv_files[table], headers=", ".join(headers[table]))
        ])


#def load_tables():

    #pw = input('enter database password for david: ')
    # options for tables include:
    # dbname=postgres user=postgres
    # dbname=ubuntu user=postgres
    #conn = psycopg2.connect("host=localhost dbname=david user=david password=david")
    #conn = psycopg2.connect("dbname=postgres user=postgres")
    #host=10.0.0.5
    #TODO: Modify this to connect over network from one EC2 instance to another
    #conn = psycopg2.connect("host=localhost dbname=david user=david password=david")

    #create_tables(cursor)
    #papers_header = 'id,title,year,doi'
    #inCit_header = 'id,inCit_id'
    #outCit_header = 'id,outCit_id'
    #authors_header = 'id,name'
    #paper_authors_header = 'paper_id,author_id'
    #author_papers_header = 'author_id,paper_id'
    #load_csv(papers_csv,'papers',['id','title','year','doi'],cursor)
    #load_csv(inCit_csv,'inCits',['id','inCit_id'],cursor)
    #load_csv(outCit_csv,'outCits',['id','outCit_id'],cursor)
    #load_csv(authors_csv,'temp_authors',['id','name'],cursor)
    #load_csv(paper_authors_csv,'paper_authors',['paper_id','author_id'],cursor)

def main():
    pass

if __name__ == "__main__":
    main()
