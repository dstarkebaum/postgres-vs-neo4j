import gzip
import pathlib
import os

#p = pathlib.Path(os.getcwd())
#print(p.parent)
print(os.path.abspath(__file__))
#with gzip.open('temp.txt.gz','wt') as gz_file:
#    for i in range(10):
#        gz_file.write(','.join([str(i*i) for i in range(10)]) + '\n')

#with gzip.open('temp.txt.gz','rt') as gz_file:
#    for line in gz_file:
#        print(line,end='')
