#!/usr/bin/sudo bash

sudo service postgresql stop
sync
echo 3 > /proc/sys/vm/drop_caches
suco service postgresql start
