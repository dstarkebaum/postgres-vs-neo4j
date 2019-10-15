import setup.populate_database as pop
import setup.postgres_utils as pgu


pgu.create_all_indexes()
pgu.cleanup_database()
