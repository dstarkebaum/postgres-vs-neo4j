import sys
import csv
import time

start_time = time.time()
file = sys.argv[1]
count = 0
with open(file,'r') as in_file, open(file+'_ddup','w') as out_file:
    csv_reader = csv.reader(in_file,delimiter='|')
    seen = set() # set for fast O(1) amortized lookup
    for row in csv_reader:
        count = count + 1
        id = row[0]
        if id not in seen:
            seen.add(id)
            out_file.write('|'.join(row)+'\n')


    print('Original file had ' + str(count) + ' rows. ' + str(count - len(seen)) + ' rows were removed.')
    print('Final set has: '+str(len(seen)) + ' rows.')
    print('Process took: %.2f s' % (time.time() - start_time))
