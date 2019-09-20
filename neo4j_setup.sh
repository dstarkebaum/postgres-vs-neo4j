#!/bin/bash

#============= within EC2 instance =====================
# Instaling neo4j in ubuntu 18.04:
# neo4j is not automatically included in the apt database, so we need to add it
sudo wget --no-check-certificate -O - https://debian.neo4j.org/neotechnology.gpg.key | sudo apt-key add -
sudo echo 'deb http://debian.neo4j.org/repo stable/' | sudo tee /etc/apt/sources.list.d/neo4j.list
sudo apt update

# NOTE: this should also install Java Runtime 8 (as a dependency)
sudo apt install neo4j

# See neo4j installation page for more details:
# https://neo4j.com/docs/operations-manual/current/installation/linux/debian/

# start neo4j service
service neo4j status
