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
handler = logging.FileHandler('benchmarks.log')
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
        'desc':'Top ten authors with the most papers',

        'neo4j':'''
MATCH (:Paper)-[r:HAS_AUTHOR]->(a:Author)
RETURN a.name,COUNT(r)
ORDER BY COUNT(r) DESC LIMIT 10;
            ''',

        'post':'''
SELECT authors.name, count(*) FROM
authors LEFT JOIN (
    has_author LEFT JOIN is_cited_by
    ON is_cited_by.id = has_author.paper_id
) ON authors.id = has_author.author_id
GROUP BY authors.name
ORDER BY count(*) DESC LIMIT 10;
            ''',
        },{
        'desc':'Top ten authors whose papers have the most direct citations',

        'neo4j':'''
MATCH (:Paper)-[r:CITES]-(:Paper)-[HAS_AUTHOR]-(a:Author)
RETURN a.name, COUNT(r)
ORDER BY COUNT(r) DESC LIMIT 10;
            ''',

        'post':'''
SELECT authors.name, count(*)
    FROM authors
    JOIN has_author ON
        authors.id = has_author.author_id
    JOIN is_cited_by AS authorsPapers ON
        has_author.paper_id = authorsPapers.id
    JOIN is_cited_by AS citingPapers ON
        authorsPapers.id = citingPapers.incit_id
GROUP BY authors.name
ORDER BY count(*) DESC LIMIT 10;
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
        },{
        'desc':'Top ten most cited papers',

        'neo4j':'''
MATCH (:Paper)-[r:CITES]->(p:Paper)
RETURN p.title, COUNT(r)
ORDER BY COUNT(r) DESC LIMIT 10;
            ''',

        'post':'''
SELECT papers.title, count(*) FROM
papers INNER JOIN is_cited_by ON papers.id = is_cited_by.id
GROUP BY papers.title
ORDER BY count(*) DESC LIMIT 10;
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
