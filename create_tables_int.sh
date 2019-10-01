#!/bin/bash

# Create tables
#psql -c "CREATE TABLE papers (id VARCHAR(40) PRIMARY KEY, title TEXT, year SMALLINT, doi TEXT);"
#psql -c "CREATE TABLE inCits (id VARCHAR(40), inCit_id VARCHAR(40), PRIMARY KEY (id, inCit_id));"
psql -c "CREATE TABLE papers (id NUMERIC, title TEXT, year SMALLINT, doi TEXT);"
psql -c "CREATE TABLE inCits (id NUMERIC, inCit_id NUMERIC);"
#id VARCHAR(40) REFERENCES papers(id),
#inCit_id VARCHAR(40) REFERENCES papers(id),
#psql -c "CREATE TABLE outCits (id VARCHAR(40), outCit_id VARCHAR(40),PRIMARY KEY (id,outCit_id));"
psql -c "CREATE TABLE outCits (id NUMERIC, outCit_id NUMERIC);"
#psql -c "CREATE TABLE authors (ser SERIAL PRIMARY KEY, id INTEGER, name TEXT);"
#outCit_id VARCHAR(40) REFERENCES papers(id),
#psql -c "CREATE TABLE paper_authors (ser SERIAL PRIMARY KEY, paper_id VARCHAR(40),author_id INTEGER);"
psql -c "CREATE TABLE authors (id INTEGER, name TEXT);"
psql -c "CREATE TABLE paper_authors (paper_id NUMERIC,author_id INTEGER);"
