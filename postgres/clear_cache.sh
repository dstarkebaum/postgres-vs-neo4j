#!/usr/bin/sudo bash

# Stop the postgres database
sudo service postgresql stop
sync

# clear the Linux memory cache to reset database query performance
echo 3 > /proc/sys/vm/drop_caches

# Tehn restart the database
suco service postgresql start
