"""Install Packages for StarCraft Casting Tool."""
import pip
import platform
import logging
import subprocess

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
logger.info("pip-version: " + pip.__version__)

modules = ['pip', 'pyqt5', 'requests', 'configparser', 'flask', 'keyboard', 'websockets', 'humanize', 'markdown2', 'pyupdater', 'beautifulsoup4']

win_modules = ['pypiwin32', 'pytesseract', 'Pillow']

try:
    
    for module in modules:
        subprocess.check_call(["python", '-m', 'pip', 'install',"--upgrade", module])
        
    if system == "Windows":
        for module in win_modules:
            subprocess.check_call(["python", '-m', 'pip', 'install',"--upgrade", module])

except Exception as e:
    logger.exception("message")
