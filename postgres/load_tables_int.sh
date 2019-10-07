#!/bin/bash
export PSQL_HOST=10.0.0.14
export start_time=$SECONDS

# clear out the data directories if present
rm -rf data/csv
rm -rf data/s2-corpus
mkdir data/csv
mkdir data/s2-corpus

function make_csv {
  echo "$((SECONDS-start_time)): Downloading $1.gz from S3..."
  aws s3 cp s3://data-atsume-arxiv/open-corpus/2019-09-17/$1.gz data/s2-corpus/$1.gz
  echo "$((SECONDS-start_time)): Unzipping $1.gz"
  gunzip -f data/s2-corpus/$1.gz
  echo "$((SECONDS-start_time)): Converting $1 JSON to CSV tables"
  python3 parse_json_to_csv_int.py $1
}

function load_csv {
  echo "$((SECONDS-start_time)): Copying $(pwd)/data/csv/${1}.csv into $USER: ${1}(${2}) at $PSQL_HOST"

  #psql -h 'host_name_or_ip' -d database_name -U user_name -c "SQL query"
  # SQL query: "\copy table_name(list,of,column,names) FROM absolute/path/to/local/csv WITH (OPTIONS)"
  psql -h "$PSQL_HOST" -d $USER -U $USER -c "\copy ${1}(${2}) FROM $(pwd)/data/csv/${1}.csv WITH (FORMAT CSV, HEADER, DELIMITER '|')"

}

# There are 176 "s2-corpus-xxx" files in S3 which need to be unzipped, parsed, and loaded into the database
for i in {000..000}
do
  make_csv "s2-corpus-$i"
  load_csv "papers" "id, title, year, doi"
  load_csv "inCits" "id, inCit_id"
  load_csv "outCits" "id, outCit_id"
  load_csv "authors" "id, name"
  load_csv "paper_authors" "paper_id, author_id"
  echo "$((SECONDS-start_time)): clearing data folder"
  rm -r data/csv
  rm -r data/s2-corpus
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
