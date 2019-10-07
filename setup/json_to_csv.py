import json
import os
import time
import sys
import csv
import argparse
import gzip
from contextlib import ExitStack

# EX: To parse one json file into a set of compressed csv files for neo4j, try this:
# python3 parse_json.py data/s2-corpus/s2-corpus-001 --unique --neo4j --compress


# global variables are frowned upon... probably there is a better way for this...
# delimiter for CSV files
d = '|'
tables = ['papers', 'is_cited_by', 'cites', 'authors', 'has_author']#, 'is_author_of']

# eliminate newlines, quotations, delimiters, and extra white space
def clean(text):
    return text.replace(d,'').replace('\n','').replace('"','').replace("'",'').strip()
# turn a list into a CSV row
def format(list):
    return d.join(list)+'\n'
# generate a path string from a single file name

def to_secs(time):
    return "{:0.4f}".format(time)

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('json_src',
            help='Filename (including path) of the json file to parse')
    parser.add_argument('-i,','--int',help='convert id from hex to int',
            action='store_true')
    parser.add_argument('--unique',help='make each csv file unique by including the json_src name',
            action='store_true')
    parser.add_argument('--neo4j',help='Include :TYPE and :LABEL for Neo4j',
            action='store_true')
    parser.add_argument('--compress',help='gzip output files',
            action='store_true')
    parser.add_argument('-p','--path',type=str,default='data/csv',
            help='relative path to store the output csv files')
    return parser.parse_args()

def main():
    args = parse_args()
    corpus_path = os.getcwd()+'/'+args.json_src
    # Input File (1.5GB JSON)
    #src_file = os.path.basename(corpus_path)
    make_int=args.int
    output_dir = args.path

    parse_json(corpus_path,
            args.path,
            make_int=args.int,
            unique=args.unique,
            neo4j=args.neo4j,
            compress=args.compress
            )

'''
Combine output_dir, table_name, and src_file name into a complete (absolute) path string
of the form:
/absolute/path/to/output_dir/table_name.csv
if unique=True, the name of the json src file is also included:
/absolute/path/to/output_dir/src_file-table_name.csv
'''
def path(table_name, output_dir, src_file, unique=False,compress=False):
    filename = ''

    if unique:
        filename = src_file+"-"+table_name+'.csv'
    else:
        filename = table_name+'.csv'
    if compress:
        filename = filename+'.gz'
    return(os.path.join(os.getcwd(),output_dir,filename))

def write_headers(files):
    files['papers'].write(format(['id:ID(Paper)','title','year:INT','doi',':LABEL']))
    files['is_cited_by'].write(format(['id:START_ID(Paper)','is_cited_by_id:END_ID(Paper)',':TYPE']))
    files['cites'].write(format(['id:START_ID(Paper)','cites_id:END_ID(Paper)',':TYPE']))
    files['authors'].write(format(['id:ID(Author)','name',':LABEL']))
    files['has_author'].write(format(['paper_id:START_ID(Paper)','author_id:END_ID(Author)',':TYPE']))
    #files['is_author_of'].write(format(['author_id:START_ID(Author)','paper_id:END_ID(Paper)',':TYPE']))

def parse_json(
        corpus_path,
        output_dir,
        make_int=False,
        unique=False,
        neo4j=False,
        compress=False
        ):

    print("Parsing: "+corpus_path)
    print('Exporting to ' + output_dir)

    if make_int:
        print('Storing ids as big integers ~ Order(10^49)')
    if unique:
        print('Creating unique filenames like: '+os.path.basename(corpus_path)+'-[table_name].csv')
    if compress:
        print('Compressing outpus files with gzip')



    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    # Print status to STDOUT

    compressed_input = (corpus_path.split('.')[-1] == 'gz')

    src_file = os.path.basename(corpus_path)
    if compressed_input:
        # remove '.gz'
        src_file = src_file[:-3]


    output_files = {t:path(t,output_dir,src_file,unique,compress) for t in tables}

    start_time = time.perf_counter()
    print("Start time: "+time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))

    # keep a count of the number of records parsed
    count = 0

    with ExitStack() as stack:
        json_in = None
        if compressed_input:
            json_in = stack.enter_context(gzip.open(corpus_path,'rt'))
        else:
            json_in = stack.enter_context(open(corpus_path,'rt'))

        files = {}
        if compress:
            files = {t : stack.enter_context(gzip.open(output_files[t],'wt')) for t in tables}
        else:
            files = { t : stack.enter_context(open(output_files[t],'w')) for t in tables}

        if neo4j:
            write_headers(files)
        # Parse each line of JSON, and write the appropriate fields
        # to each csv table
        for line in json_in:

            #stop after 10000 rows for testing
            if 10000 == count:
                break

            # test with 100 lines to start
            if count in [100, 1000, 10000, 100000, 500000]:
                print(str(count)+" records parsed after "+to_secs(time.perf_counter() - start_time)+" seconds")
            count = count + 1

            js_line = json.loads(line)

            id = clean(js_line['id'])
            if make_int:
                id = str(int(id,16))
            title = clean(js_line['title'])
            doi = clean(js_line['doi'])

            #abstract = clean(js_line['paperAbstract'])

            # Note: js_line['s2Url'] is redundant
            # It can be generated by: https://semanticscholar.org/paper/'id'

            # some entries seem to be missing a year, so just use an empty string
            try:
                year = clean(str(js_line['year']))
            except KeyError:
                year = ''

            paper_record = [id,title,year,doi]#, abstract]
            if neo4j:
                paper_record.append(':Paper')
            files['papers'].write(format(paper_record))

            # each JSON row conains a list of citations and authors
            is_cited_by_list = js_line['inCitations']
            cites_list = js_line['outCitations']
            authors_list = js_line['authors']


            # inCitations and outCitations need to go to their own tables
            for cit in is_cited_by_list:
                cit=clean(cit)
                if make_int:
                    cit = str(int(cit,16))
                row = [id,cit]
                if neo4j:
                    row = [id,cit,':IS_CITED_BY']
                files['is_cited_by'].write(format(row))
            for cit in cites_list:
                if make_int:
                    cit = str(int(cit,16))
                cit=clean(cit)
                row = [id,cit]
                if neo4j:
                    row = [id,cit,':CITES']
                files['cites'].write(format([id,cit]))

            author_set = set()

            for author in authors_list:
                # Some papers have no authors.
                # If there are no authors for a paper, skip to the next one
                if 0 == len(author['ids']):
                    continue

                # js_line['authors'] has a format like:
                # [{"name":"Huseyin Demirbilek","ids":["4800055"]},{"name":"Serhan Küpeli","ids":["5942490"]}]
                # So apparently each name can be associated with multiple ids
                # We are only insterested in the first one, which should be unique
                author_id = clean(author['ids'][0])
                author_name = clean(author['name'])

                if author_id not in author_set:
                    author_set.add(author_id)
                    author_row = [author_id,author_name]
                    has_author_row = [id,author_id]
                    #is_author_of_row = [author_id,id]

                    if neo4j:
                        author_row = [author_id,author_name,':Author']
                        has_author_row = [id,author_id,'HAS_AUTHOR']
                    #    is_author_of_row = [author_id,id,'IS_AUTHOR_OF']

                    files['authors'].write(format(author_row))
                    files['has_author'].write(format(has_author_row))
                    #files['is_author_of'].write(format(is_author_of_row))

    print(str(count)+" records written to csv after "+to_secs(time.perf_counter() - start_time)+" seconds")

if __name__=="__main__":
    main()
