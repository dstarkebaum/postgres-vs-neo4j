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
git=1:2.17.1-1ubuntu0.4 \
awscli=1.14.44-1ubuntu1

# install python tools
sudo apt-get --yes install \
  python3-dev=3.6.7-1~18.04 \
  python3-pip=9.0.1-2.3~ubuntu1.18.04.1 \
  python3-pandas=0.22.0-4 \
  python3-venv=3.6.7-1~18.04

# get PostgreSQL development library for psycopg2
sudo apt-get --yes install \
  libpq-dev=10.10-0ubuntu0.18.04.1

sudo apt-get --yes install \
    nginx=1.14.0-0ubuntu1.6

cd /home/ubuntu
sudo -u ubuntu git clone https://github.com/dstarkebaum/postgres-vs-neo4j.git
#sudo -u ubuntu git python3 -m venv dash
#sudo -u ubuntu source dash/bin/activate
sudo -u ubuntu sh -c 'yes | pip3 install wheel'
sudo -u ubuntu sh -c 'yes | pip3 install dash py2neo psycopg2 gunicorn boto3 sqlalchemy'
#sudo -u ubuntu sh -c 'yes | pip3 install dash==1.3.1, py2neo==4.3.0, psycopg2==2.8.3, gunicorn==19.9.0, boto3==1.9.243'

# Next, configure NGINX sites:
sudo rm /etc/nginx/sites-enabled/default
sudo touch /etc/nginx/sites-available/application
sudo ln -s /etc/nginx/sites-available/application /etc/nginx/sites-enabled/application
sudo cp /home/ubuntu/postgres-vs-neo4j/aws/nginx/application /etc/nginx/sites-enabled/application
# nano /etc/nginx/sites-available/
sudo /etc/init.d/nginx restart

# Finally, navigate to the folder containing your dash app
# Identify the module name (python file... also be sure to include __init__.py!)
# and the variable inside the module that points to the Flask Server
# NOTE: if you are using Dash only, you can access the flask server by:
# app = Dash()
# server = app.server <-- This is the flask app
# then call: gunicorn my_python_file:flask_app_variable_name
cd /home/ubuntu/postgres-vs-neo4j/dash
sudo -u ubuntu gunicorn dash_app:server

# See neo4j installation page for more details:
# https://neo4j.com/docs/operations-manual/current/installation/linux/debian/

# start neo4j service
#service neo4j status
