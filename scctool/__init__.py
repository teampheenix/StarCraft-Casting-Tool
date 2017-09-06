"""Starcraft Casting Tool."""

import sys
import logging

# create logger with 'spam_application'
logger = logging.getLogger('scctool')
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler('data/scctool.log', 'w')
# create console handler with a higher log level
# create formatter and add it to the handlers
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(fh)


def main():
    """Run Starcraft Casting Tool."""
    from PyQt5.QtWidgets import QApplication, QStyleFactory
    from PyQt5.QtGui import QIcon
    from scctool.view.main import mainWindow
    from scctool.controller import MainController

    try:
        """Run the main program."""
        app = QApplication(sys.argv)
        QApplication.setStyle(QStyleFactory.create('Fusion'))
        app.setWindowIcon(QIcon('src/icon.png'))
        cntlr = MainController()
        mainWindow(cntlr, app)
        logger.info("Starting...")
        sys.exit(app.exec_())

    except Exception as e:
        logger.exception("message")
        raise
