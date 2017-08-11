#!/usr/bin/python
import sys
import logging

# create logger with 'spam_application'
logger = logging.getLogger('alphasc2tool')
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler('src/alphasc2tool.log', 'w')
# create console handler with a higher log level
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(fh)


try:
    
    from alphasc2tool.controller import *
    from alphasc2tool.view import *

    from PyQt5.QtWidgets import QApplication, QStyleFactory
    from PyQt5.QtGui import QIcon

    def main():
    
        app = QApplication(sys.argv)
        QApplication.setStyle(QStyleFactory.create('Fusion'))
        app.setWindowIcon(QIcon('src/alpha.ico'))
        controller = AlphaController()
        view = mainWindow(controller)
        logger.info("Starting...")      
        sys.exit(app.exec_())


    if __name__ == '__main__':
        main()
        
except Exception as e:
    logger.exception("message")       