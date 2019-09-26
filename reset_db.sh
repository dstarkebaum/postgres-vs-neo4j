#!/bin/bash

# Tear down and rebuild database from scratch
sudo -u postgres psql -c "DROP DATABASE $USER;"
sudo -u postgres psql -c "DROP ROLE $USER;"

sudo -u postgres psql -c "CREATE ROLE $USER SUPERUSER LOGIN PASSWORD '$USER';"
#sudo -u postgres psql -c "CREATE ROLE $USER WITH LOGIN CREATEDB CREATEROLE PASSWORD $USER;"
sudo -u postgres psql -c "CREATE DATABASE $USER OWNER $USER;"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $USER TO $USER;"

# Create tables
psql -c "CREATE TABLE papers (id VARCHAR(40) PRIMARY KEY, title TEXT, year SMALLINT, doi TEXT);"
psql -c "CREATE TABLE inCits (id VARCHAR(40),inCit_id VARCHAR(40),PRIMARY KEY (id,inCit_id));"
#id VARCHAR(40) REFERENCES papers(id),
#inCit_id VARCHAR(40) REFERENCES papers(id),
psql -c "CREATE TABLE outCits (id VARCHAR(40) REFERENCES papers(id),outCit_id VARCHAR(40),PRIMARY KEY (id,outCit_id));"
#outCit_id VARCHAR(40) REFERENCES papers(id),
psql -c "CREATE TABLE temp_authors (ser SERIAL PRIMARY KEY,id INTEGER,name TEXT);"
psql -c "CREATE TABLE paper_authors (ser SERIAL PRIMARY KEY,paper_id VARCHAR(40),author_id INTEGER);"

#python3 load_tables.py
