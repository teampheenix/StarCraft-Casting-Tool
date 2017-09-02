#!/usr/bin/python
import sys
import logging

# create logger with 'spam_application'
logger = logging.getLogger('scctool')
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler('src/scctool.log', 'w')
# create console handler with a higher log level
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(fh)


try:
    
    from scctool.controller import *
    from scctool.view import *

    from PyQt5.QtWidgets import QApplication, QStyleFactory
    from PyQt5.QtGui import QIcon


    def main():
    
        app = QApplication(sys.argv)
        QApplication.setStyle(QStyleFactory.create('Fusion'))
        app.setWindowIcon(QIcon('src/icon.png'))
        controller = MainController()
        view = mainWindow(controller, app)
        logger.info("Starting...")      
        sys.exit(app.exec_())


    if __name__ == '__main__':
        main()
        
except Exception as e:
    logger.exception("message")
    raise       