"""Install Packages for StarCraft Casting Tool."""
import pip
import platform
import logging

system = platform.system()


# create logger with 'spam_application'
logger = logging.getLogger('installpackages')
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler('installpackages.log', 'w')
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
    pip.main(['install', 'pip', '--upgrade'])
    pip.main(['install', 'pyqt5', '--upgrade'])
    pip.main(['install', 'requests', '--upgrade'])
    pip.main(['install', 'configparser', '--upgrade'])
    pip.main(['install', 'flask', '--upgrade'])
    pip.main(['install', 'keyboard', '--upgrade'])
    pip.main(['install', 'websockets', '--upgrade'])
    pip.main(['install', 'humanize', '--upgrade'])
    pip.main(['install', 'markdown2', '--upgrade'])
    pip.main(['install', 'pyupdater', '--upgrade'])
    pip.main(['install', 'beautifulsoup4', '--upgrade'])

    if(system == "Windows"):
        pip.main(['install', 'pypiwin32', '--upgrade'])
        pip.main(['install', 'pytesseract', '--upgrade'])
        pip.main(['install', 'Pillow', '--upgrade'])

except Exception as e:
    logger.exception("message")
