#!/bin/bash

# Create tables
psql -c "CREATE TABLE papers (id NUMERIC, title TEXT, year SMALLINT, doi TEXT);"
psql -c "CREATE TABLE is_cited_by (id NUMERIC, incit_id NUMERIC);"
psql -c "CREATE TABLE cites (id NUMERIC, outcit_id NUMERIC);"
psql -c "CREATE TABLE authors (id INTEGER, name TEXT);"
psql -c "CREATE TABLE has_author (paper_id NUMERIC,author_id INTEGER);"
