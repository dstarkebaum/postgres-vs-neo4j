import boto3


#s3 = boto3.resource('s3')
s3 = boto3.client('s3')

s3.download_file(
        'data-atsume-arxiv',
        'open-corpus/2019-09-17/s2-corpus-000.gz',
        'data/s2-corpus/s2-corpus-000.gz')
