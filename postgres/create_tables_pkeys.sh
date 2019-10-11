#!/bin/bash

psql -c "CREATE TABLE papers (id NUMERIC PRIMARY KEY, title TEXT, year SMALLINT, doi TEXT);"
psql -c "CREATE TABLE is_cited_by (id NUMERIC, inCit_id NUMERIC);"
psql -c "CREATE TABLE cites (id NUMERIC, outCit_id NUMERIC);"
psql -c "CREATE TABLE authors (id INTEGER PRIMARY KEY, name TEXT);"
psql -c "CREATE TABLE has_author (paper_id NUMERIC, author_id INTEGER);"
