#import setup.populate_neo4j as pop
import setup.populate_database as pop
import setup.neo4j_utils as n4j

n4j.make_all_indexes()

pop.populate_database(
        corpus_path='data/s2-corpus',
        csv_path='data/csv',
        prefix='s2-corpus',
        suffix='.csv',
        start=0,
        end=2,
        compress=False,
        engine='neo4j',
        testing=False)
#pop.populate_neo4j()
#pop.download_from_s3()

#bucket='data-atsume-arxiv'
#source='open-corpus/2019-09-17/s2-corpus-000.gz'
#destination='data/s2-corpus/s2-corpus-000.gz'

#s3 = boto3.client('s3')
#s3.download_file(bucket, source, destination)
