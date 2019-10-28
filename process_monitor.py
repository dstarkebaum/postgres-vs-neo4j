#!/usr/bin/python
import argparse
import subprocess as sub
from datetime import datetime
import time

def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('process',type=str,
            help='the name of the process to track')
    parser.add_argument('-o','--output',type=str,default='',
            help='filename of the log')
    parser.add_argument('-s','--sleep',type=int,default=10,
            help='sleep time per cycle, in seconds')

    return parser.parse_args()

# Determine the list of process ID's (PID) that belong to processes
# by a given name
def get_pids(process):
    try:
        output = sub.check_output(['pgrep','-f', process]).split(b'\n')
        pidlist = [ x.decode('utf-8') for x in output]

    except sub.CalledProcessError:
        pidlist = []
    #print 'list of PIDs = ' + ', '.join(str(e) for e in pidlist)
    return pidlist


# use the python script "ps_mem" to determine the exact about of RAM
# being used by a given process in Bytes.
def get_raw_mem(pid):
    try:
        #print(pid)
        mem = sub.check_output(['sudo','ps_mem', '-p', pid, '-t']).decode('utf-8')
    except sub.CalledProcessError:
        mem = '-1'
    return mem

# Start an ongoing process that tracks RAM usage
# of any processes with a given name "process"
# and stores the results to a logfile.
# Continues indefinitely until the process dies.
def monitor_process(process,output='',sleep=10):
    if len(output)==0:
        output = '{p}_mem.log'.format(p=process)
    print(output)
    quit=False

    with open(output, 'a', buffering=1) as f:
        while not quit:

            pids = get_pids(process)

            if 0 == len(pids):
                quit=True
                print('Process '+ process + ' no longer exists!' )
                return None

            msg = datetime.now().strftime("%m/%d/%Y,%H:%M:%S") + \
                    " "+pids[0]+" "+str(get_raw_mem(pids[0]))
            #print(msg)
            f.write(msg+'\n')

            time.sleep(sleep)


def main():
    args = parse_args()
    #sub.Popen(['pgrep', args.process])
        #sudo pgrep -f neo4j
    monitor_process(args.process, args.output, args.sleep)

if __name__ == "__main__":
    main()
