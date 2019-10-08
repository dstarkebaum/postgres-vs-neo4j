#!/usr/bin/env python2.7

import psycopg2
import os
import time
#from setup import host_config
#def main(host='localhost',database='ubuntu',user='ubuntu',password='ubuntu'):
host_config = {
    HOST='localhost',
    DATABASE='ubuntu',
    USER='ubuntu',
    PASSWORD='ubuntu'
    }

#Decorator to handle database connections.
def with_connection(f):
    def with_connection_(*args, **kwargs):
        # or use a pool, or a factory function...
        connection = psycopg2.connect('''
                host={h} dbname={db} user={u} password={pw}
                '''.format(
                        h=host_config.HOST,
                        db=host_config.DATABASE,
                        u=host_config.USER,
                        pw=host_config.PASSWORD)
                )
        try:
            return_value = f(connection, *args, **kwargs)
        except Exception:
            connection.rollback()
            print(f.__name__+" failed!")
            raise
        else:
            connection.commit() # or maybe not
            print(f.__name__+" success!")
        finally:
            connection.close()

        return return_value

    return with_connection_

@with_connection
def remove_duplicates(connection,table,columns):
    cursor = connection.cursor()
    start=time.perf_counter()
    # build up combined conditions from multiple columns
    conditions = ''.join(
            [' AND a.{c} = b.{c}'.format(c=col) for col in columns]
            )
    cursor.execute('''
            DELETE FROM {t} a USING {t} b
            WHERE a.ctid < b.ctid
            '''.format(t=table) + conditions + ';'
            )
    print(str(time.perf_counter()-start) + " s to remove duplicates " +
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

    gi=''
    if gin:
        if (gin_type=='trigram' or gin_type=='trgm'):
            gi=' USING GIN({c} gin_trgm_ops)'.format(c=columns[0])
        elif (gin_type=='vector' or gin_type=='tsvector' or gin_type=='vec'):
            gi=' USING GIN(to_tsvector("simple",{c}))'.format(c=columns[0])
        else:
            print("Ignoring invalid gin_type: " + gin_type)

    cursor.execute('''
            {e}{a}CREATE {u}INDEX {i} ON {t}({c}){g};
            '''.format(e=exp,a=ana,u=uni,t=table,c=cols,i=index,g=gi)
            )

    print(str(time.perf_counter()-start) +
            "s to create index on " +
            "{t}({c})".format(t=table,c=','.join(columns))
            )
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

    cursor.execute('''
    {e}{a}ALTER TABLE {t} ADD PRIMARY KEY USING INDEX {i};
    '''.format(e=exp,a=ana,t=table,i=index)
    )
    print(str(time.perf_counter()-start) +
            "s to set primary key on " +
            "{i}".format(i=index)
            )


def load_csv(file,table,headers,cursor):
    delimiter = '|'
    heads = ','.join(headers)
    cursor.execute("""
            COPY {t}({h}) FROM '{f}' DELIMITER '{d}' CSV HEADER;
            """.format(f=file,d=delimiter,t=table,h=heads)
            )

def main():

    index = create_index('authors',['id'],unique=True,primary=True,explain=True)
    remove_duplicates('authors',['id'],explain=True)
    set_primary_key('authors',index)
    create_index(cur,'papers',['id'],unique=True,primary=True)
    create_index(cur,'paper_authors',['author_id'])
    create_index(cur,'paper_authors',['paper_id'])

    remove_duplicates(cur,'incits',['id','incit_id'])
    remove_duplicates(cur,'outcits',['id','outcit_id'])

    create_index(cur,'incits',['id'])
    create_index(cur,'outcits',['id'])

    create_index(cur,'authors',['name'],gin=True)
    create_index(cur,'papers',['title'],gin=True,gin_type='vector')



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

    # TODO: Create index on authors and paper_authors and remove duplicate rows
    # get list of tables and columns in schema
    #'''select table_schema, table_name, column_name
    #from information_schema.columns
    #where table_schema not in ('pg_catalog','information_schema')
    #order by 1,2,3


if __name__ == "__main__":
    main()
