#!/bin/bash


# Edit the PostgreSQL config files to enable access to DB over VPC and from Insight office
# You can do this manually with:
# sudo nano /etc/postgresql/10/main/pg_hba.conf
# or automatically using bash piping!
# --> Start a terminal as root, printf a string and append-pipe it to the config file:
printf "# Allow connections over AWS VPC within private subnet\n" >> /etc/postgresql/10/main/pg_hba.conf
printf "host\tall\t\tall\t\t10.0.0.0/28\t\tmd5\n" >> /etc/postgresql/10/main/pg_hba.conf
printf "# Allow connections from Insight\n" >> /etc/postgresql/10/main/pg_hba.conf
printf "host\tall\t\tall\t\t67.171.25.72/32\t\tmd5\n" >> /etc/postgresql/10/main/pg_hba.conf
