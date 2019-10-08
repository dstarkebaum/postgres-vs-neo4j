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

# Install Java Runtime 8 (as a dependency)
sudo apt-get --yes install openjdk-8-jdk

# Instaling neo4j in ubuntu 18.04:
# neo4j is not automatically included in the apt database, so we need to add it
sudo wget --no-check-certificate -O - https://debian.neo4j.org/neotechnology.gpg.key | sudo apt-key add -
sudo echo 'deb http://debian.neo4j.org/repo stable/' | sudo tee /etc/apt/sources.list.d/neo4j.list
sudo apt-get --yes update

sudo apt-get --yes install neo4j==3.5.11

# download Graph algorithm and APOC plugins into /var/lib/neo4j/plugins
wget https://s3-eu-west-1.amazonaws.com/com.neo4j.graphalgorithms.dist/neo4j-graph-algorithms-3.5.11.0-standalone.zip;
sudo -u neo4j unzip -d /var/lib/neo4j/plugins neo4j-graph-algorithms-3.5.11.0-standalone.zip
sudo -u neo4j wget https://github.com/neo4j-contrib/neo4j-apoc-procedures/releases/download/3.5.0.5/apoc-3.5.0.5-all.jar -P /var/lib/neo4j/plugins

sudo -u neo4j cp neo4j.conf /etc/neo4j/neo4j.conf

#git clone https://github.com/dstarkebaum/dstarkebaum.github.io.git


# See neo4j installation page for more details:
# https://neo4j.com/docs/operations-manual/current/installation/linux/debian/

# start neo4j service
#service neo4j status
