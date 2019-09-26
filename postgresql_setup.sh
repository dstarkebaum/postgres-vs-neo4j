#!/bin/bash

# ami-06f2f779464715dc5 == Ubuntu Server 18.04 LTS (HVM), SSD Volume Type (64-bit x86)

#============= within EC2 instance =====================
# update Ubuntu packages
sudo apt-get update && sudo apt-get upgrade

# install postgresql
#sudo apt-get --yes --force-yes install ssh rsync openjdk-8-jdk scala python-dev python-pip python-numpy python-scipy python-pandas gfortran git supervisor ruby bc
# install general utilities
sudo apt-get --yes install ssh rsync git supervisor bc
# install python tools
sudo apt-get --yes python-dev python-pip python-numpy python-scipy python-pandas ipython
# install PostgreSQL (assuming version 10)
sudo apt-get --yes install postgresql postgresql-server-dev-10 libpq-dev
# install airflow
sudo apt-get --yes install libmysqlclient-dev

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
sudo -u postgres psql -c "CREATE ROLE $USER WITH LOGIN CREATEDB CREATEROLE PASSWORD $USER;"
sudo -u postgres psql -c "CREATE DATABASE $USER OWNER $USER;"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $USER TO $USER;"

# NOTE: The default password will be set to the username (ubuntu)
# but it is recommended that you setup your own
# password after logging in for the first time with:
# psql
# ubuntu=>\password


# install python packages
sudo pip install nose seaborn boto scikit-learn psygopg2


# edit the PostgreSQL config files
sudo nano /etc/postgresql/10/main/pg_hba.conf
sudo nano /etc/postgresql/10/main/postgresql.conf

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
