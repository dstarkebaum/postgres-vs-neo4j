#!/bin/bash

# ami-06f2f779464715dc5 == Ubuntu Server 18.04 LTS (HVM), SSD Volume Type (64-bit x86)

# NOTE: Installation logs can eb found in:
# nano /var/log/apt/term.log

#============= within EC2 instance =====================
# update Ubuntu packages
sudo apt-get --yes update && sudo apt-get --yes upgrade

# install general utilities
sudo apt-get --yes install ssh rsync git supervisor bc
# install python tools
sudo apt-get --yes install python3-dev python3-pip python3-numpy python3-scipy python3-pandas ipython3
# install PostgreSQL (assuming version 10)
sudo apt-get --yes install postgresql postgresql-server-dev-10 libpq-dev

# install python packages
pip3 install nose seaborn boto scikit-learn psycopg2 apache-airflow

# create a PostgreSQL history file for logging
touch .psql_history

# Create a new user/role (ubuntu) with default password (ubuntu)
# This user can login, create new databases, and create new roles
# PostgreSQL requires each user to have it own default database (ubuntu)
# Then we grant that user (ubuntu) full access to add/delete tables
#
# NOTE: "sudo -u postgres" temporarily assumes the username 'postgres',
# which is the default SUPERUSER for PostgreSQL (full access)
# We can then execute SQL commands as 'postgres' using 'psql -c'
sudo -u postgres psql -c "CREATE ROLE $USER WITH LOGIN CREATEDB CREATEROLE PASSWORD '$USER';"
sudo -u postgres psql -c "CREATE DATABASE $USER OWNER $USER;"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $USER TO $USER;"

# Edit the PostgreSQL config files to enable access to DB over VPC and from Insight office
# You can do this manually with:
# sudo nano /etc/postgresql/10/main/pg_hba.conf
# or automatically using bash piping!
# --> Start a terminal as root, printf a string and append-pipe it to the config file:
sudo sh -c 'printf "# Allow connections over AWS VPC within private subnet\n" >> /etc/postgresql/10/main/pg_hba.conf'
sudo sh -c 'printf "host\tall\t\tall\t\t10.0.0.0/28\t\tmd5\n" >> /etc/postgresql/10/main/pg_hba.conf'
sudo sh -c 'printf "# Allow connections from Insight\n" >> /etc/postgresql/10/main/pg_hba.conf'
sudo sh -c 'printf "host\tall\t\tall\t\t67.171.25.72/32\t\tmd5\n" >> /etc/postgresql/10/main/pg_hba.conf'
# sudo nano /etc/postgresql/10/main/postgresql.conf

# NOTE: The default password will be set to the username (ubuntu)
# but it is recommended that you setup your own
# password after logging in for the first time with:
# psql
# ubuntu=>\password