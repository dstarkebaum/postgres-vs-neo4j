#!/bin/bash

# start a loop to record the %RAM and %CPU usage of posgres every 10 seconds
while true; do ps -u postgres -o pid -o %mem -o %cpu -o cputime -o etime -o command --width 200 >> postgres_ps.log; sleep 10; done

# Record the exact RAM usage in bytes every 10 seconds
ps_mem -p $(pgrep -d, postgres) -t -w 10 | while read line; do echo $(date +"%T") $line; done >> [PID]_mem.log
