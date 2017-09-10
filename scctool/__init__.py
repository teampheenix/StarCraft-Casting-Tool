"""StarCraft Casting Tool."""

import sys
import logging
from PyQt5.QtWidgets import QApplication, QStyleFactory

logger = logging.getLogger('scctool')

__version__ = "1.0.4"
__latest_version__ = __version__
__new_version__ = False


def main():
    """Run StarCraft Casting Tool."""
    app = QApplication(sys.argv)
    QApplication.setStyle(QStyleFactory.create('Fusion'))
    initial_download()
    main_window(app)
    sys.exit(app.exec_())


def main_window(app):
    """Run the main exectuable."""
    from PyQt5.QtCore import QSize
    from PyQt5.QtGui import QIcon
    from scctool.view.main import MainWindow
    from scctool.controller import MainController
    from scctool.settings import getAbsPath

    try:
        """Run the main program."""
        icon = QIcon()
        icon.addFile(getAbsPath('src/scct.ico'), QSize(32, 32))
        icon.addFile(getAbsPath('src/scct.png'), QSize(256, 256))
        app.setWindowIcon(icon)
        cntlr = MainController()
        MainWindow(cntlr, app)
        logger.info("Starting...")

    except Exception as e:
        logger.exception("message")
        raise


def initial_download():
    """Download the required data at an inital startup."""
    import scctool.tasks.updater
    from scctool.view.widgets import InitialUpdater

    if scctool.tasks.updater.needInitialUpdate(scctool.tasks.updater.getDataVersion()):
        InitialUpdater()
