import py2neo

graph = py2neo.Graph()

base = 'file:///data/neo4j-unzipped/s2-corpus-'
numFiles = 176
nodes = {
        'authors': ['id:ID', 'name'],
        'papers': ['id:ID', 'title', 'year:INT', 'doi']
        }

relations = {
        'has_author': ['paper_id:START_ID', 'author_id:END_ID', ':TYPE'],
        'is_author_of': ['author_id:START_ID', 'paper_id:END_ID'],
        'cites': ['id:START_ID', 'cites_id:END_ID', ':TYPE'],
        'is_cited_by': ['id:START_ID', 'cited_by_id:END_ID', ':TYPE']
        }

for i in range(numFiles):


'''
LOAD CSV FROM 'file:///data/neo4j-unzipped/s2-corpus-000-has_author.csv' AS row
MATCH (p:Paper {id: row[0]})
MATCH (a:Author {id: row[1]})
MERGE (p)-[r:HAS_AUTHOR]->(a)
RETURN count(*);
'''

if __name__=="__main__":
    main(sys.argv[1:])
