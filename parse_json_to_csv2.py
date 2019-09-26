#import pandas as pd
#import itertools as it
import json
import os
import time

# Input File (100GB JSON)
#sample_path = r"data/s2-sample/sample-S2-records"
corpus_path = r"data/s2-corpus/s2-corpus-000"

# output files (csv)
papers_csv = r"data/csv/papers.csv"
inCit_csv = r"data/csv/inCit.csv"
outCit_csv = r"data/csv/outCit.csv"
authors_csv = r"data/csv/authors.csv"
paper_authors_csv = r"data/csv/paper_authors.csv"
author_papers_csv = r"data/csv/author_papers.csv"

d = '|'

def clean(text):
    return text.replace(d,'').replace('\n','').replace('"','').strip()
def format(list):
    return d.join(list)+'\n'

#remove any existing files
for file in [papers_csv,inCit_csv,outCit_csv, authors_csv, paper_authors_csv]:
    if os.path.exists(file):
        os.remove(file)



# collect a set of author ids (as int)
# to make sure duplicates are not written into authors_csv
#author_ids = []

start_time = time.time()
# keep a count of the number of records parsed
count = 0
# open all of the output files as "append"
# so that additional write calls to not delete what is already written
# OOPS! Since I used "with open", the files are never closed!
# So there is no danger of overwriting during script execution...
with open(corpus_path, 'r') as json_in, \
        open(papers_csv, 'a+') as papers_out, \
        open(inCit_csv,'a+') as inCit_out, \
        open(outCit_csv,'a+') as outCit_out, \
        open(authors_csv,'a+') as authors_out, \
        open(paper_authors_csv,'a+') as paper_authors_out, \
        open(author_papers_csv,'a+') as author_papers_out:


    # write the headers to each csv file
    papers_header = ['id','title','year','doi']
    inCit_header = ['id','inCit_id']
    outCit_header = ['id','outCit_id']
    authors_header = ['id','name']
    paper_authors_header = ['paper_id','author_id']
    author_papers_header = ['author_id','paper_id']

    papers_out.write(format(papers_header))
    inCit_out.write(format(inCit_header))
    outCit_out.write(format(outCit_header))
    authors_out.write(format(authors_header))
    paper_authors_out.write(format(paper_authors_header))
    author_papers_out.write(format(author_papers_header))


    # Parse each line of JSON, and write the appropriate fields
    # to each csv table
    for line in json_in:
        if 10000 == count:
            break

        # test with 100 lines to start
        if count in [100, 1000, 10000, 100000, 500000]:
            print(str(count)+" records parsed after "+str(time.time() - start_time)+" seconds")

        #    break
        js_line = json.loads(line)
        count = count + 1
        idNum = clean(js_line['id'])
        title = clean(js_line['title'])
        doi = clean(js_line['doi'])

        # some entries seem to be missing a year
        # so just use an empty string
        try:
            year = clean(str(js_line['year']))
        except KeyError:
            year = ''


        paper_record = [idNum,title,year,doi]
        #js_line['s2Url']-> https://semanticscholar.org/paper/'id'
        #out_1.write(idNum+'\n')
        inCits = js_line['inCitations']
        outCits = js_line['outCitations']
        authors = js_line['authors']

        papers_out.write(format(paper_record))

        # inCitations and outCitations need to go to their own tables
        for cit in inCits:
            inCit_out.write(format([idNum,cit]))
        for cit in outCits:
            outCit_out.write(format([idNum,cit]))

        # we want to make sure duplicate authors are not saved
        # so we keep track of all of the author_ids in memory
        for author in authors:
            # If there are no authors for a paper, skip to the next one
            if 0 == len(author['ids']):
                continue
            #elif (',' in author['name']):
            #    print(idNum+', '+str(author['ids'])+', '+str(author['name']))
            #print(author['ids'][0])
            #author_id_int = int(author['ids'][0])
            author_id = clean(author['ids'][0])
            # remove any stray commas from author names
            author_name = clean(author['name'])
            paper_authors_out.write(format([idNum,author_id]))
            author_papers_out.write(format([author_id,idNum]))
            #paper_authors_out.write(idNum+','+str(author_id_int)+'\n')
            #if not author_id_int in author_ids:
                #author_ids.append(author_id_int)
            authors_out.write(format([author_id,author_name]))
            #authors_out.write(str(author_id_int)+','+author['name']+'\n')

        #print(js_line['id'])

print(str(count)+" records written to csv after "+str(time.time() - start_time)+" seconds")
