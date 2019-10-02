#!/bin/bash
#export PSQL_HOST=10.0.0.14
export start_time=$SECONDS

# clear out the data directories if present
rm -rf data/neo4j
rm -rf data/s2-corpus

python3 create_neo4j_headers.py

function make_csv {
  echo "$((SECONDS-start_time)): Downloading $1.gz from S3..."
  aws s3 cp s3://data-atsume-arxiv/open-corpus/2019-09-17/$1.gz data/s2-corpus/$1.gz

  echo "$((SECONDS-start_time)): Unzipping $1.gz"
  gunzip -f data/s2-corpus/$1.gz

  echo "$((SECONDS-start_time)): Converting $1 JSON to Neo4j CSV tables"
  python3 parse_json_to_csv_neo4j.py $1

}

# There are 176 "s2-corpus-xxx" files in S3 which need to be unzipped, parsed, and loaded into the database
for i in {000..176}
do
  mkdir data/neo4j
  mkdir data/s2-corpus

  make_csv "s2-corpus-$i"

  cd data/neo4j

  for f in "papers" "is_cited_by" "cites" "authors" "has_author" "is_author_of"
  do
    echo "$((SECONDS-start_time)): zipping $f.csv"
    gzip $f.csv
    echo "$((SECONDS-start_time)): uploading $f.csv.gz to S3"
    aws s3 cp $f.csv.gz s3://data-atsume-arxiv/open-corpus/2019-09-17/neo4j/$1/$f.csv.gz
  done

  cd ../..

  rm -r data/s2-corpus
  rm -r data/neo4j

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
