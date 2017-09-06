"""Starcraft Casting Tool."""
import sys
import logging

# create logger with 'spam_application'
logger = logging.getLogger('scctool.main')


try:

    from scctool.controller import MainController
    from scctool.view import mainWindow

    from PyQt5.QtWidgets import QApplication, QStyleFactory
    from PyQt5.QtGui import QIcon

    def main():
        """Run the main program."""
        app = QApplication(sys.argv)
        QApplication.setStyle(QStyleFactory.create('Fusion'))
        app.setWindowIcon(QIcon('src/icon.png'))
        controller = MainController()
        mainWindow(controller, app)
        logger.info("Starting...")
        sys.exit(app.exec_())

    if __name__ == '__main__':
        main()

except Exception as e:
    logger.exception("message")
    raise
