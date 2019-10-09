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
  python3-numpy=1:1.13.3-2ubuntu1 \
  python3-pandas=0.22.0-4 \
  python3-venv=3.6.7-1~18.04

# Install Java Runtime 8 (as a dependency)
sudo apt-get --yes install openjdk-8-jdk

# Instaling neo4j in ubuntu 18.04:
# neo4j is not automatically included in the apt database, so we need to add it
sudo wget --no-check-certificate -O - https://debian.neo4j.org/neotechnology.gpg.key | sudo apt-key add -
sudo echo 'deb http://debian.neo4j.org/repo stable/' | sudo tee /etc/apt/sources.list.d/neo4j.list
sudo apt-get --yes update

sudo apt-get --yes install neo4j #==3.5.11

# download Graph algorithm and APOC plugins into /var/lib/neo4j/plugins
wget https://s3-eu-west-1.amazonaws.com/com.neo4j.graphalgorithms.dist/neo4j-graph-algorithms-3.5.11.0-standalone.zip;
sudo -u neo4j unzip -d /var/lib/neo4j/plugins neo4j-graph-algorithms-3.5.11.0-standalone.zip
sudo -u neo4j wget https://github.com/neo4j-contrib/neo4j-apoc-procedures/releases/download/3.5.0.5/apoc-3.5.0.5-all.jar -P /var/lib/neo4j/plugins

# download and install ps_mem.py to monitor RAM usage
wget https://raw.githubusercontent.com/pixelb/ps_mem/master/ps_mem.py
sudo install ps_mem.py /usr/local/bin/ps_mem
rm ps_mem.py

sudo -u ubuntu sh -c 'yes | pip3 install wheel'
sudo -u ubuntu sh -c 'yes | pip3 install py2neo boto3'


cd /home/ubuntu
sudo -u ubuntu git clone https://github.com/dstarkebaum/postgres-vs-neo4j.git

# replace the neo4j configuration file
sudo -u neo4j cp /etc/neo4j/neo4j.conf /home/ubuntu/neo4j.conf_bak
sudo -u neo4j cp /home/ubuntu/postgres-vs-sql/config/neo4j.conf /etc/neo4j/neo4j.conf

# See neo4j installation page for more details:
# https://neo4j.com/docs/operations-manual/current/installation/linux/debian/

# start neo4j service
#service neo4j status
