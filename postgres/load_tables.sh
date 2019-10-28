#!/bin/bash

export start_time=$SECONDS

function make_csv {
  echo "$((SECONDS-start_time)): Downloading $1.gz from S3..."
  aws s3 cp s3://data-atsume-arxiv/open-corpus/2019-09-17/$1.gz data/s2-corpus/$1.gz
  echo "$((SECONDS-start_time)): Unzipping $1.gz"
  gunzip -f data/s2-corpus/$1.gz
  echo "$((SECONDS-start_time)): Converting $1 JSON to CSV tables"
  python3 parse_json_to_csv.py $1
}

function load_csv {
  echo "$((SECONDS-start_time)): Copying $(pwd)/data/csv/${1}.csv into $USER: ${1}(${2}) at $PSQL_HOST"
  psql -h "$PSQL_HOST" -d $USER -U $USER -c "\copy ${1}(${2}) FROM $(pwd)/data/csv/${1}.csv WITH (FORMAT CSV, HEADER, DELIMITER '|')"

  #echo "Deleting duplicates in the authors table based on authors.id"
  #psql -h "$PSQL_HOST" -d $USER -U $USER -c "DELETE FROM authors a USING authors b WHERE a.ser < b.ser AND a.id = b.id"
  #echo "Deleting duplicates in the author_papers table"
  #psql -h "$PSQL_HOST" -d $USER -U $USER -c "DELETE FROM paper_authors a USING paper_authors b WHERE a.ser < b.ser AND a.paper_id = b.paper_id AND a.author_id = b.author_id"
}

# loop through all json documents, parse them into csv files, and load them into the postgres database
for i in {000..176}
do
  make_csv "s2-corpus-$i"
  load_csv "papers" "id, title, year, doi"
  load_csv "inCits" "id, inCit_id"
  load_csv "outCits" "id, outCit_id"
  load_csv "authors" "id, name"
  load_csv "paper_authors" "paper_id, author_id"
  echo "$((SECONDS-start_time)): clearing data folder"
  rm -r data/*
done
