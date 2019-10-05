#!/bin/bash

# Create tables
psql -c "CREATE TABLE papers (id NUMERIC, title TEXT, year SMALLINT, doi TEXT);"
psql -c "CREATE TABLE inCits (id NUMERIC, inCit_id NUMERIC);"
psql -c "CREATE TABLE outCits (id NUMERIC, outCit_id NUMERIC);"
psql -c "CREATE TABLE authors (id INTEGER, name TEXT);"
psql -c "CREATE TABLE paper_authors (paper_id NUMERIC,author_id INTEGER);"
