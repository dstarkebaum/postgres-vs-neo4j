#!/bin/bash
export SERVER_HOST = 10.0.0.9
#aws s3 cp s3://data-atsume-arxiv/open-corpus/2019-09-17/s2-corpus-000.gz data/s2-corpus/s2-corpus-000.gz
#gunzip data/s2-corpus/s2-corpus-000.gz

function make_csv {
  echo "Downloading $1.gz from S3..."
  aws s3 cp s3://data-atsume-arxiv/open-corpus/2019-09-17/$1.gz data/s2-corpus/$1.gz
  echo "Unzipping $1.gz"
  gunzip -f data/s2-corpus/$1.gz
  echo "Converting $1 JSON to CSV tables"
  python3 parse_json_to_csv.py $1
}

function load_csv {
  #psql -h '10.0.0.5' -d ubuntu -U ubuntu -c \
  #psql -h 'localhost' -d david -U david -c "\copy ${1} (${2}) from $(pwd)/data/csv/${1}.csv with delimiter as '|'"
  echo "Copying $(pwd)/data/csv/${1}.csv into $USER: ${1}(${2}) at $SERVER_HOST"
  psql -h "${SERVER_HOST}" -d $USER -U $USER -c "\copy ${1}(${2}) FROM $(pwd)/data/csv/${1}.csv WITH (FORMAT CSV, HEADER, DELIMITER '|')"
  #echo "Deleting duplicates in the authors table based on authors.id"
  #psql -h 'localhost' -d $USER -U $USER -c "DELETE FROM authors a USING authors b WHERE a.ser < b.ser AND a.id = b.id"
  #echo "Deleting duplicates in the author_papers table"
  #psql -h 'localhost' -d $USER -U $USER -c "DELETE FROM paper_authors a USING paper_authors b WHERE a.ser < b.ser AND a.paper_id = b.paper_id AND a.author_id = b.author_id"
  #echo "Transferring table $1 from local to main database at 10.0.0.9 (PostgreSQL server on private subnet)"
  #psql -h 'localhost' -d $USER -U $USER -c "\copy ${1} TO stdout" | psql -h 10.0.0.9 -U ubuntu ubuntu -c "\copy ${1} from stdin"
}
#users (id, email, first_name, last_name)

for i in {001..001}
do
  make_csv "s2-corpus-$i"
  load_csv "papers" "id, title, year, doi"
  load_csv "inCits" "id, inCit_id"
  load_csv "outCits" "id, outCit_id"
  load_csv "authors" "id, name"
  load_csv "paper_authors" "paper_id, author_id"
  echo "clearing data folder"
  rm -r data/*
done

#papers_csv = r"data/csv/papers.csv"
#inCit_csv = r"data/csv/inCits.csv"
#outCit_csv = r"data/csv/outCits.csv"
#authors_csv = r"data/csv/authors.csv"
#paper_authors_csv = r"data/csv/paper_authors.csv"
#author_papers_csv = r"data/csv/author_papers.csv"

#load_csv(papers_csv,'papers',['id','title','year','doi'],cursor)
#load_csv(inCit_csv,'inCits',['id','inCit_id'],cursor)
#load_csv(outCit_csv,'outCits',['id','outCit_id'],cursor)
#load_csv(authors_csv,'temp_authors',['id','name'],cursor)
#load_csv(paper_authors_csv,'paper_authors',['paper_id','author_id'],cursor)

#psql -c "CREATE TABLE papers (id VARCHAR(40) PRIMARY KEY, title TEXT, year SMALLINT, doi TEXT);"
#psql -c "CREATE TABLE inCits (id VARCHAR(40),inCit_id VARCHAR(40),PRIMARY KEY (id,inCit_id));"
#id VARCHAR(40) REFERENCES papers(id),
#inCit_id VARCHAR(40) REFERENCES papers(id),
#psql -c "CREATE TABLE outCits (id VARCHAR(40) REFERENCES papers(id),outCit_id VARCHAR(40),PRIMARY KEY (id,outCit_id));"
#outCit_id VARCHAR(40) REFERENCES papers(id),
#psql -c "CREATE TABLE temp_authors (ser SERIAL PRIMARY KEY,id INTEGER,name TEXT);"
#psql -c "CREATE TABLE paper_authors (ser SERIAL PRIMARY KEY,paper_id VARCHAR(40),author_id INTEGER);"
