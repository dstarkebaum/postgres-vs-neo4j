#!/bin/bash

# ami-06f2f779464715dc5 == Ubuntu Server 18.04 LTS (HVM), SSD Volume Type (64-bit x86)

#============= within EC2 instance =====================
# update Ubuntu packages
sudo apt-get --yes update && sudo apt-get --yes upgrade

# NOTE: Installation logs can eb found in:
# nano /var/log/apt/term.log


# install postgresql
#sudo apt-get --yes --force-yes install ssh rsync openjdk-8-jdk scala python-dev python-pip python-numpy python-scipy python-pandas gfortran git supervisor ruby bc
# install general utilities
sudo apt-get --yes install ssh rsync git supervisor bc
# install python tools
# This installs python 2.7 tools:
#sudo apt-get --yes install python-dev python-pip python-numpy python-scipy python-pandas ipython
# But we really want to use python3 tools:
sudo apt-get --yes install python-dev python3-pip python3-numpy python3-scipy python3-pandas ipython3
# install PostgreSQL (assuming version 10)
sudo apt-get --yes install postgresql postgresql-server-dev-10 libpq-dev
# install airflow
#sudo apt-get --yes install libmysqlclient-dev

# check the PostgreSQL version
psql -V


# In this case, we are using the program createdb (through bash)
# and createuser (also through bash)
#sudo -u postgres createdb $USER
#sudo -u postgres createuser $USER



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

# NOTE: The default password will be set to the username (ubuntu)
# but it is recommended that you setup your own
# password after logging in for the first time with:
# psql
# ubuntu=>\password


# install python packages
pip3 install nose seaborn boto scikit-learn psycopg2 apache-airflow


# edit the PostgreSQL config files
# do this manually with:
# sudo nano /etc/postgresql/10/main/pg_hba.conf
# or automatically using bash piping!
# Start a terminal as root, printf a string and append-pipe it to the config file:
sudo sh -c 'printf "# Allow connections over AWS VPC within private subnet\n" >> /etc/postgresql/10/main/pg_hba.conf'
sudo sh -c 'printf "host\tall\t\tall\t\t10.0.0.0/28\t\tmd5\n" >> /etc/postgresql/10/main/pg_hba.conf'
sudo sh -c 'printf "# Allow connections from Insight\n" >> /etc/postgresql/10/main/pg_hba.conf'
sudo sh -c 'printf "host\tall\t\tall\t\t67.171.25.72/32\t\tmd5\n" >> /etc/postgresql/10/main/pg_hba.conf'
# sudo nano /etc/postgresql/10/main/postgresql.conf

# restart PostgreSQL service with updated settings
sudo /etc/init.d/postgresql restart
# check for running postgres cluster
pg_lsclusters
# create a PostgreSQL history file for logging
touch .psql_history
sudo -u postgres -i
sudo -u postgres createuser --superuser $USER
sudo -u postgres createdb $USER

# setup airflow
export AIRFLOW_HOME=~/airflow
sudo pip install 'apache-airflow[postgres]'
# The latest version of marshmallow-sqlalchemy does not support Python 2.7
# and the [postgres] collection does not recognize this,
# so we need to manually roll back to the last version supporting Python 2.7
sudo pip uninstall marshmallow-sqlalchemy
sudo pip install marshmallow-sqlalchemy==0.18.0
