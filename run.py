import boto3
import setup.populate_neo4j as pop

pop.populate_neo4j()
#pop.download_from_s3()

#bucket='data-atsume-arxiv'
#source='open-corpus/2019-09-17/s2-corpus-000.gz'
#destination='data/s2-corpus/s2-corpus-000.gz'

#s3 = boto3.client('s3')
#s3.download_file(bucket, source, destination)
