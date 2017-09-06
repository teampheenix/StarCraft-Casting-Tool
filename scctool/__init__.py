"""Starcraft Casting Tool."""

import sys
import logging

logger = logging.getLogger('scctool')


def main():
    """Run Starcraft Casting Tool."""
    from PyQt5.QtWidgets import QApplication, QStyleFactory
    from PyQt5.QtGui import QIcon
    from scctool.view.main import MainWindow
    from scctool.controller import MainController

    try:
        """Run the main program."""
        app = QApplication(sys.argv)
        QApplication.setStyle(QStyleFactory.create('Fusion'))
        app.setWindowIcon(QIcon('src/icon.png'))
        cntlr = MainController()
        MainWindow(cntlr, app)
        logger.info("Starting...")
        sys.exit(app.exec_())

    except Exception as e:
        logger.exception("message")
        raise
