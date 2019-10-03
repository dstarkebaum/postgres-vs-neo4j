
#!/bin/bash
#export PSQL_HOST=10.0.0.9
start_time=$SECONDS
let elapsed=$SECONDS-start_time
echo "Deleting duplicates in the papers table based on papers.id"
psql -h 'localhost' -d $USER -U $USER -c "DELETE FROM papers a USING papers b WHERE a.ser < b.ser AND a.id = b.id"

let delta=$SECONDS-elapsed
let elapsed=$SECONDS-start_time
echo "${elapsed}:(+${delta}) Creating index on paper_id, and make primary key"
psql -h 'localhost' -d $USER -U $USER -c "CREATE INDEX index_paper_id ON papers(id);"
psql -h 'localhost' -d $USER -U $USER -c "ALTER TABLE paper ADD PRIMARY KEY USING INDEX index_paper_id;"

let delta=$SECONDS-elapsed
let elapsed=$SECONDS-start_time
echo "Deleting duplicates in the authors table based on authors.id"
psql -h 'localhost' -d $USER -U $USER -c "DELETE FROM authors a USING authors b WHERE a.ser < b.ser AND a.id = b.id"

let delta=$SECONDS-elapsed
let elapsed=$SECONDS-start_time
echo "${elapsed}:(+${delta}) Creating index on author_id, and make primary key"
psql -h 'localhost' -d $USER -U $USER -c "CREATE INDEX index_author_id ON authors(id);"

let delta=$SECONDS-elapsed
let elapsed=$SECONDS-start_time
echo "${elapsed}:(+${delta}) Creating index on author_id, and make primary key"
psql -h 'localhost' -d $USER -U $USER -c "CREATE INDEX index_author_id ON authors(id);"

#echo "Transferring table $1 from local to main database at 10.0.0.9 (PostgreSQL server on private subnet)"
#psql -h 'localhost' -d $USER -U $USER -c "\copy ${1} TO stdout" | psql -h 10.0.0.9 -U ubuntu ubuntu -c "\copy ${1} from stdin"
