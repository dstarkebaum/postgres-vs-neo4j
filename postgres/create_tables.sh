#!/bin/bash

# Create tables
psql -c "CREATE TABLE papers (id VARCHAR(40), title TEXT, year SMALLINT, doi TEXT);"
psql -c "CREATE TABLE is_cited_by (id VARCHAR(40), inCit_id VARCHAR(40));"
psql -c "CREATE TABLE cites (id VARCHAR(40), outCit_id VARCHAR(40));"
psql -c "CREATE TABLE authors (id INTEGER, name TEXT);"
psql -c "CREATE TABLE has_author (paper_id VARCHAR(40),author_id INTEGER);"
