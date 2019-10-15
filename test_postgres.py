
import setup.populate_database as pop
import setup.postgres_utils as pgu

pgu.main()
pop.populate_database(
        corpus_path='data/s2-corpus',
        csv_path='data/csv',
        prefix='s2-corpus',
        suffix='.csv',
        start=0,
        end=1,
        compress=False,
        engine='psql',
        make_int=True,
        testing=True,
        database='david'
        )


pgu.create_all_indexes(database='david')
pgu.cleanup_database(database='david')
