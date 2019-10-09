while true; do ps -u neo4j -o pid -o %mem -o %cpu -o cputime -o etime -o command --width 200 >> postgres_ps.log; sleep 10; done
ps_mem -p $(pgrep -d, postgres) -t -w 1 | while read line; do echo $(date +"%T") $line; done >> [PID]_mem.log


#nohup sudo ps_mem -p $(pgrep -d, postgres) -t -w 1 | while read line; do echo $(date +"%T") $line; done >> postgres_mem.log &

#ps -o pid,user,%mem,command ax | grep postgres | sort -b -k3 -r
# ps -o pid,user,%mem,command ax | grep postgres | sort -b -k3 -r
