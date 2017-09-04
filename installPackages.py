"""Install Packages for Starcraft Casting Tool."""
import pip
import platform
import logging

system = platform.system()


# create logger with 'spam_application'
logger = logging.getLogger('installpackages')
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler('src/installpackages.log', 'w')
# create console handler with a higher log level
ch = logging.StreamHandler()
# create formatter and add it to the handlers
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(fh)
logger.addHandler(ch)

logger.info("system: " + system)

try:
    pip.main(['install', 'PyQt5'])
    pip.main(['install', 'requests'])
    pip.main(['install', 'configparser'])
    pip.main(['install', 'flask'])
    pip.main(['install', 'obs-ws-rc'])
    pip.main(['install', 'pytesseract'])
    pip.main(['install', 'Pillow'])

    if(system == "Windows"):
        pip.main(['install', 'pypiwin32'])

except Exception as e:
    logger.exception("message")
