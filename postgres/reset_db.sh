#!/bin/bash

# Tear down and rebuild database from scratch
sudo -u postgres psql -c "DROP DATABASE $USER;"
sudo -u postgres psql -c "DROP ROLE $USER;"

sudo -u postgres psql -c "CREATE ROLE $USER SUPERUSER LOGIN PASSWORD '$USER';"
sudo -u postgres psql -c "CREATE DATABASE $USER OWNER $USER;"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $USER TO $USER;"
