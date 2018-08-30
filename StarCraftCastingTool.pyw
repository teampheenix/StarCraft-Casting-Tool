"""StarCraft Casting Tool."""
import logging

import scctool

# create logger with 'spam_application'
logger = logging.getLogger('scctool')
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler(scctool.settings.getLogFile(), 'w')
ch = logging.StreamHandler()
# create console handler with a higher log level
# create formatter and add it to the handlers
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(fh)
logger.addHandler(ch)

if __name__ == '__main__':
    try:
        scctool.main()
    finally:
        fh.close()
        logger.removeHandler(fh)
        logger.removeHandler(ch)
