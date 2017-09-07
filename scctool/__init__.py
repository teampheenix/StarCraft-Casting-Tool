"""Starcraft Casting Tool."""

import sys
import logging

logger = logging.getLogger('scctool')


def main():
    """Run Starcraft Casting Tool."""
    from PyQt5.QtWidgets import QApplication, QStyleFactory
    from PyQt5.QtGui import QIcon
    from PyQt5.QtCore import QSize
    from scctool.view.main import MainWindow
    from scctool.controller import MainController
    from scctool.settings import getAbsPath

    try:
        """Run the main program."""
        app = QApplication(sys.argv)
        QApplication.setStyle(QStyleFactory.create('Fusion'))
        icon = QIcon()
        icon.addFile(getAbsPath('src/scct.ico'),QSize(32, 32))
        icon.addFile(getAbsPath('src/scct.png'),QSize(256, 256))
        app.setWindowIcon(icon)
        cntlr = MainController()
        MainWindow(cntlr, app)
        logger.info("Starting...")
        sys.exit(app.exec_())

    except Exception as e:
        logger.exception("message")
        raise
