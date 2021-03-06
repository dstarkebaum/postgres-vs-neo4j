import os

# create directory if needed
if not os.path.exists('data/neo4j'):
    os.makedirs('data/neo4j')

# write header files to csv
d = '|'
def format(list):
    return d.join(list)+'\n'
def path(file):
    return(os.getcwd()+"/data/neo4j/"+file)

papers_header = path("papers_header.csv")
is_cited_by_header = path("is_cited_by_header.csv")
cites_header = path("cites_header.csv")

authors_header = path("authors_header.csv")
has_author_header = path("has_author_header.csv")
is_author_of_header = path("is_author_of_header.csv")

with open(papers_header, 'w') as papers_out:
    papers_out.write(format(['id:ID(Paper)','title','year:INT','doi',':LABEL']))

with open(is_cited_by_header,'w') as is_cited_by_out:
    is_cited_by_out.write(format(['id:START_ID(Paper)','is_cited_by_id:END_ID(PAPER)',':TYPE']))

with open(cites_header,'w') as cites_out:
    cites_out.write(format(['id:START_ID(Paper)','cites_id:END_ID(Paper)',':TYPE']))

with open(authors_header,'w') as authors_out:
    authors_out.write(format(['id:ID(Author)','name',':LABEL']))

with open(has_author_header,'w') as has_author_out:
    has_author_out.write(format(['paper_id:START_ID(Paper)','author_id:END_ID(Author)',':TYPE']))

with open(is_author_of_header,'w') as is_author_of_out:
    is_author_of_out.write(format(['author_id:START_ID(Author)','paper_id:END_ID(Paper)',':TYPE']))

#if not os.path.exists(papers_header):
#if not os.path.exists(is_cited_by_header):
#if not os.path.exists(cites_header):
#if not os.path.exists(authors_header):
#if not os.path.exists(has_author_header):
#if not os.path.exists(is_author_of_header):
