import os
import time
from datetime import datetime
import logging
from contextlib import ExitStack

from . import credentials
from . import postgres_utils as pgu
from . import neo4j_utils as n4u

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# make a handler that exports to a file
handler = logging.FileHandler('benchmarks'+datetime.now().strftime("_%Y%m%d_%H%M%S")+'.log')
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# log unhandled exceptions
def handle_unhandled_exception(exc_type, exc_value, exc_traceback):
    """Handler for unhandled exceptions that will write to the logs"""
    if issubclass(exc_type, KeyboardInterrupt):
        # if it's a ctl-C call the default excepthook saved at __excepthook__
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logger.critical("Unhandled exception", exc_info=(exc_type, exc_value, exc_traceback))

tests = [
        {
        'desc':"Find names and ids of the first 10 authors with names like 'x'",

        'neo4j':'''
MATCH (a:Author)
WHERE a.name =~ '.*Altman.*'
RETURN a.name, a.id;
LIMIT 10;
                ''',
        'post':'''
SELECT name, id
FROM authors
WHERE name ILIKE '%Altman%'
LIMIT 10;
                ''',


        },{
        'desc':"Find titles and ids of the first 10 papers with titles like 'x'",


        'neo4j':'''
MATCH (p:Paper)
WHERE p.title =~ '.*'%Preferred reporting items for systematic reviews%'.*'
RETURN p.title, p.id
LIMIT 10;
                ''',
        'post':'''
SELECT title, id FROM papers
WHERE title ILIKE '%Preferred reporting items for systematic reviews%'
LIMIT 10;
                ''',

        },{
        'desc':"Count all papers by an author with id 'x'",

        'neo4j':'''
MATCH (p:Paper)-[:HAS_AUTHOR]->(a:Author)
WHERE a.id = "144117798"
RETURN count(p);
                ''',
        'post':'''
SELECT count(paper_id)
FROM has_author
WHERE has_author.author_id = 144117798;
                ''',

        },{
        'desc':"Find the titles and ids of the first 10 papers by an author with id 'x'",


        'neo4j':'''
MATCH (p:Paper)-[:HAS_AUTHOR]->(a:Author)
WHERE a.id = "144117798"
RETURN p.title, p.id
LIMIT 10;
                ''',
        'post':'''
SELECT papers.title, papers.id
FROM papers
JOIN has_author ON
  has_author.paper_id = papers.id
WHERE has_author.author_id = 144117798
LIMIT 10;
                ''',
        },{
        'desc':"Count all papers that cite a paper with id 'x'",

        'neo4j':'''
MATCH (citing:Paper)-[:CITES]->(cited:Paper)
WHERE cited.id = "fbb11a841893d4b68fa2173226285ded4f7b04d6"
RETURN count(citing);
                ''',
        'post':'''
SELECT count(incit_id)
FROM is_cited_by
WHERE is_cited_by.id = 1436906225246299354080717389136457570294446097622;
                ''',

        },{
        'desc':"Find the titles and ids of the first 10 papers that cite a paper with id 'x'",


        'neo4j':'''
MATCH (citing:Paper)-[:CITES]->(cited:Paper)
WHERE cited.id = "fbb11a841893d4b68fa2173226285ded4f7b04d6"
RETURN citing.title, citing.id
LIMIT 10;
                ''',
        # note: hex(1436906225246299354080717389136457570294446097622)
        # is fbb11a841893d4b68fa2173226285ded4f7b04d6
        'post':'''
SELECT papers.title, papers.id
FROM papers
JOIN is_cited_by ON
  papers.id = is_cited_by.incit_id
WHERE is_cited_by.id = 1436906225246299354080717389136457570294446097622
LIMIT 10;
                ''',

        },{
        'desc':"Find the titles, ids, and citation count of the top 10 most cited papers",


        'neo4j':'''
MATCH (:Paper)-[r:CITES]->(p:Paper)
RETURN p.title, p.id, COUNT(r)
ORDER BY COUNT(r) DESC
LIMIT 10;
            ''',

        'post':'''
SELECT papers.title, papers.id, count(is_cited_by.incit_id)
FROM papers
JOIN is_cited_by ON
  papers.id = is_cited_by.id
GROUP BY papers.id
ORDER BY count(is_cited_by.incit_id) DESC
LIMIT 10;
              ''',
#        },{
#        'desc':'Top ten papers with most citations of citations of citations...',
#
#        'neo4j':'''
#MATCH (:Paper)-[r:CITES *1..]->(p:Paper)
#RETURN p.title, COUNT(r)
#ORDER BY COUNT(r) DESC
#LIMIT 10;
#            ''',

        },{
        'desc':"Find the names, ids, and paper counts of the top ten authors who have published the most papers",


        'neo4j':'''
MATCH (:Paper)-[r:HAS_AUTHOR]->(a:Author)
RETURN a.name, a.id, COUNT(r)
ORDER BY COUNT(r) DESC LIMIT 10;
            ''',

        'post':'''
SELECT authors.name, authors.id, count(has_author.paper_id)
FROM authors
JOIN has_author ON
  authors.id = has_author.author_id
GROUP BY authors.id
ORDER BY count(has_author.paper_id) DESC LIMIT 10;
            ''',

        },{
        'desc':"Find the names, ids, and citation counts of the top ten authors whose papers have the most direct citations",


        'neo4j':'''
MATCH (:Paper)-[r:CITES]-(:Paper)-[HAS_AUTHOR]-(a:Author)
RETURN a.name, a.id, COUNT(r)
ORDER BY COUNT(r) DESC LIMIT 10;
            ''',

        'post':'''
SELECT authors.name, authors.id, count(is_cited_by.incit_id)
FROM authors
JOIN has_author ON
  authors.id = has_author.author_id
JOIN is_cited_by ON
  has_author.paper_id = is_cited_by.id
GROUP BY authors.id
ORDER BY count(is_cited_by.incit_id) DESC LIMIT 10;
            ''',
#        },{
#        'desc':'Top ten authors whose papers have the most citations of citations...',
#
#        'neo4j':'''
#MATCH (:Paper)-[r:CITES *1..]->(:Paper)-[:HAS_AUTHOR]->(a:Author)
#RETURN a.name, COUNT(r)
#ORDER BY COUNT(r) DESC
#LIMIT 10;
#            ''',
        },
]


def run_test(database, db_size, test, repeats=3, save=True):

    neo4j_aliases = ['neo4j','n4j','neo']
    postgres_aliases = ['post','postgres','postgresql']

    if database not in neo4j_aliases and \
            database not in postgres_aliases:
        logger.info('invalid database :' + database)
        return None

    if db_size not in credentials.neo4j and \
            db_size not in credentials.postgres:
        logger.info('invalid database size :' + db_size)
        return None

    if test not in range(len(tests)):
        logger.info('invalid test :' + str(test))
        return None


    logger.info('Starting test: '+tests[test]['desc'])
    logger.info('on: '+', '.join([database,db_size]))

    results = []
    if database in neo4j_aliases:
        graph = n4u.start_connection(db_size)
        query = tests[test]['neo4j']
        for i in range(repeats):
            start_time = time.perf_counter()
            results.append(n4u.return_query(graph,query))
            logger.info('Test #'+str(i) + ' completed in ' +
                    str(time.perf_counter() - start_time) + ' seconds')

    elif database in postgres_aliases:
        pgu.set_database(db_size)
        query = tests[test]['post']
        for i in range(repeats):
            start_time = time.perf_counter()
            results.append(pgu.return_query(query))
            logger.info('Test #'+str(i) + ' completed in ' +
                    str(time.perf_counter() - start_time) + ' seconds')
    if save:
        save_test_results(database, db_size, test, repeats=repeats, results=results)
    return results

def get_test_filename(database, db_size, test, dt_string=''):
     return os.path.join('test_results',
            database+'-'+db_size+'_test_'+str(test)+dt_string+'.csv')


def save_test_results(database, db_size, test, repeats=3, results=None):

    dt_string = '_'+datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = get_test_filename(database, db_size, test)
    backup_filename = get_test_filename(database, db_size, test,dt_string)

    if not results:
        results = run_test(database, db_size, test, repeats, save=False)

    with ExitStack() as stack:
        file = stack.enter_context(open(filename,'w'))
        backup_file = stack.enter_context(open(backup_filename,'w'))
        for i in range(len(results)):
            file.write(str(results[i]['time'])+'\n')
            backup_file.write(str(results[i]['time'])+'\n')

    return results
