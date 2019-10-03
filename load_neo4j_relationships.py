import py2neo

graph = py2neo.Graph()

'''
LOAD CSV FROM 'file:///data/ne4j-unzipped/s2-corpus-000-has_author.csv' AS row
MATCH (p:Paper {id: row[0]})
MATCH (a:Author {id: row[1]})
MERGE (p)-[r:HAS_AUTHOR]->(a)
RETURN count(*);
'''

if __name__=="__main__":
    main(sys.argv[1:])
