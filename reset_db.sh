#!/bin/bash

# Must be executed as user "postgres"
# Tear down and rebuild database from scratch
sudo -u postgres psql -c "DROP DATABASE $USER;"
sudo -u postgres psql -c "DROP ROLE $USER;"

sudo -u postgres psql -c "CREATE ROLE $USER SUPERUSER LOGIN PASSWORD '$USER';"
#sudo -u postgres psql -c "CREATE ROLE $USER WITH LOGIN CREATEDB CREATEROLE PASSWORD $USER;"
sudo -u postgres psql -c "CREATE DATABASE $USER OWNER $USER;"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $USER TO $USER;"

# Create tables
sh create_tables.sh

# https://chrisjean.com/view-csv-data-from-the-command-line/
# Use a combination of the cat, column, and less commands
# to render CSV data into a nice table and quickly navigated.
#cat file.csv | sed -e 's/,,/, ,/g' | column -s, -t | less -#5 -N -S

#python3 load_tables.py
