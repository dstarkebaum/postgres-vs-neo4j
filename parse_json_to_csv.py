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
    papers_header = ['paper_id','title','year','doi']
    inCit_header = ['paper_id','in_citation']
    outCit_header = ['paper_id','out_citation']
    authors_header = ['author_id','author_name']
    paper_authors_header = ['paper_id','author_id']
    author_papers_header = ['author_id','paper_id']

    papers_out.write(','.join(papers_header)+'\n')
    inCit_out.write(','.join(inCit_header)+'\n')
    outCit_out.write(','.join(outCit_header)+'\n')
    authors_out.write(','.join(authors_header)+'\n')
    paper_authors_out.write(','.join(paper_authors_header)+'\n')
    author_papers_out.write(','.join(author_papers_header)+'\n')


    # Parse each line of JSON, and write the appropriate fields
    # to each csv table
    for line in json_in:
        # test with 100 lines to start
        if count in [100, 1000, 10000, 100000, 500000]:
            print(str(count)+" records parsed after "+str(time.time() - start_time)+" seconds")
        #    break
        js_line = json.loads(line)
        count = count + 1
        idNum = js_line['id']
        title = js_line['title'].strip()
        doi =

        # some entries seem to be missing a year
        # so just use an empty string
        try:
            year = str(js_line['year'])
        except KeyError:
            year = ''


        paper_record = [
                idNum,
                title,
                year,
                #js_line['s2Url'],
                # -> https://semanticscholar.org/paper/'id'
                js_line['doi']
                ]
        #out_1.write(idNum+'\n')
        inCits = js_line['inCitations']
        outCits = js_line['outCitations']
        authors = js_line['authors']

        papers_out.write(','.join(paper_record)+'\n')

        # inCitations and outCitations need to go to their own tables
        for cit in inCits:
            inCit_out.write(idNum+','+cit+'\n')
        for cit in outCits:
            outCit_out.write(idNum+','+cit+'\n')

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
            author_id = author['ids'][0].strip()
            # remove any stray commas from author names
            author_name = author['name'].strip()#.replace(',','')
            paper_authors_out.write(idNum+','+author_id+'\n')
            author_papers_out.write(author_id+','+idNum+'\n')
            #paper_authors_out.write(idNum+','+str(author_id_int)+'\n')
            #if not author_id_int in author_ids:
                #author_ids.append(author_id_int)
            authors_out.write(str(author_id)+','+author_name+'\n')
            #authors_out.write(str(author_id_int)+','+author['name']+'\n')

        #print(js_line['id'])

print(str(count)+" records written to csv after "+str(time.time() - start_time)+" seconds")
