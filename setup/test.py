from setup import neo4j_utils
from setup import postgres_utils
from setup import credentials


graph = neo4j_connect()
get_authors = '''
MATCH (a:Author) return a.name
'''

authors = neo4j_utils.verbose_query(graph,get_authors)
