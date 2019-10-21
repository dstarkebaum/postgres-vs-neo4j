
import os
import sys
import argparse
import logging
from datetime import datetime
import src.db_utils.benchmark as bench

# setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# log unhandled exceptions
def handle_unhandled_exception(exc_type, exc_value, exc_traceback):
    """Handler for unhandled exceptions that will write to the logs"""
    if issubclass(exc_type, KeyboardInterrupt):
        # if it's a ctl-C call the default excepthook saved at __excepthook__
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logger.critical("Unhandled exception", exc_info=(exc_type, exc_value, exc_traceback))

# tell the python interpreter to use my own exception handler (so it can be logged)
sys.excepthook = handle_unhandled_exception



username = os.path.split(os.path.expanduser('~'))[-1]

def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('--repeat',type=int,default=1,
            help='How many times to repeat each test')
    parser.add_argument('--database',type=str,default='both',
            help='Which database engine to use: postgres, neo4j, both')
    parser.add_argument('--size',type=str,default='local',
            help='Which database size to use: local, small, medium, or large')

    return parser.parse_args()

def main():
    args = parse_args()


    log_filename = '_'.join([
            'run_tests',
            args.database,
            args.size,
            datetime.now().strftime("%Y-%m-%d_%H-%M-%S"),
            ])+'.log'

    # make a handler that exports to a file
    handler = logging.FileHandler(log_filename)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(message)s')
    handler.setFormatter(formatter)
    # then add it to the logger
    logger.addHandler(handler)

    logger.info('Database '+args.database+', size: '+args.size+', repeats: '+str(args.repeat))

    if 'both'==args.database or 'postgres'==args.database:
        for i in range(len(bench.tests)):
            logger.info('Starting test: '+bench.tests[i]['desc'])
            post = bench.run_test('postgres', args.size, i, repeats=args.repeat)
            for r in post[0]['results']:
                logger.info(r)

    if 'both'==args.database or 'neo4j'==args.database:
        for i in range(len(bench.tests)):
            logger.info('Starting test: '+bench.tests[i]['desc'])
            neo = bench.run_test('neo4j', args.size, i, repeats=args.repeat)
            for r in neo[0]['results']:
                logger.info(r)




if __name__ == "__main__":
    main()
