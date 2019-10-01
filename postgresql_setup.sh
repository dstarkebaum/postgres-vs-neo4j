#!/bin/bash

# ami-06f2f779464715dc5 == Ubuntu Server 18.04 LTS (HVM), SSD Volume Type (64-bit x86)

# NOTE: Installation logs can eb found in:
# nano /var/log/apt/term.log

#============= within EC2 instance =====================
# update Ubuntu packages
sudo apt-get --yes update && sudo apt-get --yes upgrade

# install general utilities
sudo apt-get --yes install \
ssh=1:7.6p1-4ubuntu0.3 \
rsync=3.1.2-2.1ubuntu1 \
git=1:2.17.1-1ubuntu0.4 \
supervisor=3.3.1-1.1 \
bc=1.07.1-2 \
awscli=1.14.44-1ubuntu1

# install python tools
sudo apt-get --yes install \
  python3-dev=3.6.7-1~18.04 \
  python3-pip=9.0.1-2.3~ubuntu1.18.04.1 \
  python3-numpy=1:1.13.3-2ubuntu1 \
  python3-scipy=0.19.1-2ubuntu1 \
  python3-pandas=0.22.0-4 \
  ipython3=5.5.0-1

# install PostgreSQL (assuming version 10)
sudo apt-get --yes install \
  postgresql=10+190 \
  postgresql-server-dev-10=10.10-0ubuntu0.18.04.1 \
  libpq-dev=10.10-0ubuntu0.18.04.1

# install python packages
pip3 install nose seaborn boto scikit-learn psycopg2 apache-airflow

# create a PostgreSQL history file for logging
touch ~/.psql_history

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



# Edit the PostgreSQL config files to enable access to DB over VPC and from Insight office
# You can do this manually with:
# sudo nano /etc/postgresql/10/main/pg_hba.conf
# or automatically using bash piping!
# --> Start a terminal as root, printf a string and append-pipe it to the config file:
#sudo sh -c 'printf "# Allow connections over AWS VPC within private subnet\n" >> /etc/postgresql/10/main/pg_hba.conf'
#sudo sh -c 'printf "host\tall\t\tall\t\t10.0.0.0/28\t\tmd5\n" >> /etc/postgresql/10/main/pg_hba.conf'
#sudo sh -c 'printf "# Allow connections from Insight\n" >> /etc/postgresql/10/main/pg_hba.conf'
#sudo sh -c 'printf "host\tall\t\tall\t\t67.171.25.72/32\t\tmd5\n" >> /etc/postgresql/10/main/pg_hba.conf'
#sudo sh -c 'printf "# Allow connections from Home\n" >> /etc/postgresql/10/main/pg_hba.conf'
#sudo sh -c 'printf "host\tall\t\tall\t\t73.225.252.191/32\t\tmd5\n" >> /etc/postgresql/10/main/pg_hba.conf'

# You will also need to update postgreqql.conf to listen to the correct IP-addresses
# The simplest way is to replace "localhost" with "*",
# though it is best to use "a,list,of,IP,addresses"
# sudo nano /etc/postgresql/10/main/postgresql.conf

git clone https://github.com/dstarkebaum/dstarkebaum.github.io.git

sudo cp ~/dstarkebaum.github.io/pg_hba.conf /etc/postgresql/10/main/pg_hba.conf
sudo cp ~/dstarkebaum.github.io/postgresql.conf /etc/postgresql/10/main/postgresql.conf

# Once all of the settigs are correct, then restart the sql service
sudo /etc/init.d/postgresql restart

# Check status of database with:
# pg_lsclusters

# setup airflow
#export AIRFLOW_HOME=~/airflow
#sudo pip install 'apache-airflow[postgres]'
# The latest version of marshmallow-sqlalchemy does not support Python 2.7
# and the [postgres] collection does not recognize this,
# so we need to manually roll back to the last version supporting Python 2.7
#sudo pip uninstall marshmallow-sqlalchemy
#sudo pip install marshmallow-sqlalchemy==0.18.0
