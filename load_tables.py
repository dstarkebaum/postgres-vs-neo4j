#!/usr/bin/env python2.7

import psycopg2
import os

papers_csv = os.path.abspath(r"data/csv/papers.csv")
inCit_csv = os.path.abspath(r"data/csv/inCit.csv")
outCit_csv = os.path.abspath(r"data/csv/outCit.csv")
authors_csv = os.path.abspath(r"data/csv/authors.csv")
paper_authors_csv = os.path.abspath(r"data/csv/paper_authors.csv")


def create_tables(cursor):
    cursor.execute('''
        CREATE TABLE papers (
        id VARCHAR(40) PRIMARY KEY,
        title TEXT,
        year SMALLINT,
        doi TEXT
        );''')

    cursor.execute('''
        CREATE TABLE inCits (
        id VARCHAR(40),
        inCit_id VARCHAR(40),
        PRIMARY KEY (id,inCit_id)
        );''')
        #id VARCHAR(40) REFERENCES papers(id),
        #inCit_id VARCHAR(40) REFERENCES papers(id),

    cursor.execute('''
        CREATE TABLE outCits (
        id VARCHAR(40) REFERENCES papers(id),
        outCit_id VARCHAR(40),
        PRIMARY KEY (id,outCit_id)
        );''')
        #outCit_id VARCHAR(40) REFERENCES papers(id),

    cursor.execute('''
        CREATE TABLE temp_authors (
        ser SERIAL PRIMARY KEY,
        id INTEGER,
        name TEXT
        );''')

    cursor.execute('''
        CREATE TABLE paper_authors (
        ser SERIAL PRIMARY KEY,
        paper_id VARCHAR(40),
        author_id INTEGER
        );''')
        #paper_id VARCHAR(40) REFERENCES papers(id),
        #author_id INTEGER REFERENCES authors(id),
        #PRIMARY KEY (paper_id,author_id)

def load_csv(file,table,headers,cursor):
    delimiter = '|'
    cursor.execute("""
        COPY {table}({headers}) FROM '{file}' DELIMITER '{delimiter}' CSV HEADER;
    """.format(file=file,delimiter=delimiter,table=table, headers=','.join(headers)))

def main():
    #pw = input('enter database password for david: ')
    # options for tables include:
    # dbname=postgres user=postgres
    # dbname=ubuntu user=postgres
    #conn = psycopg2.connect("host=localhost dbname=david user=david password=david")
    #conn = psycopg2.connect("dbname=postgres user=postgres")

    #TODO: Modify this to connect over network from one EC2 instance to another
    conn = psycopg2.connect("host=localhost dbname=david user=david password=david")
    cursor = conn.cursor()


    #create_tables(cursor)
    #papers_header = 'id,title,year,doi'
    #inCit_header = 'id,inCit_id'
    #outCit_header = 'id,outCit_id'
    #authors_header = 'id,name'
    #paper_authors_header = 'paper_id,author_id'
    #author_papers_header = 'author_id,paper_id'
    load_csv(papers_csv,'papers',['id','title','year','doi'],cursor)
    load_csv(inCit_csv,'inCits',['id','inCit_id'],cursor)
    load_csv(outCit_csv,'outCits',['id','outCit_id'],cursor)
    load_csv(authors_csv,'temp_authors',['id','name'],cursor)
    load_csv(paper_authors_csv,'paper_authors',['paper_id','author_id'],cursor)

    # TODO: Create index on authors and paper_authors and remove duplicate rows



    conn.commit()

if __name__ == "__main__":
    main()
