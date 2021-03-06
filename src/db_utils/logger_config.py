import logging
import sys
from datetime import datetime, timedelta

# setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

converter = lambda x, y: (
    datetime.utcnow() - timedelta (
        hours=7 if time.localtime().tm_isdst else 6)
    ).timetuple()
logging.Formatter.converter = converter

handler = logging.FileHandler('populate_database.log')
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

sys.excepthook = handle_unhandled_exception
