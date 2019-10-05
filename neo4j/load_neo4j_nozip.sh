#!/bin/bash

export start_time=$SECONDS

# neo4j settings can be adjusted here of needed:
# sudo nano /etc/neo4j/neo4j.conf

aws s3 sync s3://data-atsume-arxiv/open-corpus/2019-09-17/neo4j data/neo4j

# use glob to find all files like "data/neo4j/s2-corpus-001_papers.csv"
# then store the results in a comma-separated string to pass to neo4j-admin
papers="data/neo4j/papers_header.csv,`echo data/neo4j/*papers.csv | tr ' ' ','`"
cites="data/neo4j/cites_header.csv,`echo data/neo4j/*cites.csv | tr ' ' ','`"
is_cited_by="data/neo4j/is_cited_by_header.csv,`echo data/neo4j/*is_cited_by.csv | tr ' ' ','`"

authors="data/neo4j/authors_header.csv,`echo data/neo4j/*authors.csv | tr ' ' ','`"
is_author_of="data/neo4j/is_author_of_header.csv,`echo data/neo4j/*is_author_of.csv | tr ' ' ','`"
has_author="data/neo4j/has_author_header.csv,`echo data/neo4j/*has_author.csv | tr ' ' ','`"

#echo $papers
#echo $cites
#echo $is_cited_by
#echo $authors
#echo $is_author_of
#echo $has_author
echo "$((SECONDS-start_time)): Importing zipped files into Neo4j"
neo4j-admin import --ignore-duplicate-nodes --ignore-missing-nodes --delimiter="|" \
  --nodes:Paper="$papers"  \
  --nodes:Author="$authors" \
  --relationships:CITES="$cites"  \
  --relationships:IS_CITED_BY="$is_cited_by" \
  --relationships:HAS_AUTHOR="$has_author" \
  --relationships:IS_AUTHOR_OF="$is_author_of"
