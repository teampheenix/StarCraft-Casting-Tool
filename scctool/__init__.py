"""StarCraft Casting Tool."""

import sys
import logging
import gettext
import scctool.settings
import scctool.settings.config
from PyQt5.QtWidgets import QApplication, QStyleFactory
from PyQt5.QtCore import QTranslator, QLocale
from scctool.settings import getAbsPath

logger = logging.getLogger('scctool')

__version__ = "1.1.2"
__latest_version__ = __version__
__new_version__ = False

language = scctool.settings.config.parser.get("SCT", "language")

try:
    lang = gettext.translation(
        'messages', localedir='locales', languages=[language])
except:
    lang = gettext.NullTranslations()
    
lang.install()


def main():
    """Run StarCraft Casting Tool."""
    global language
    from scctool.view.main import MainWindow

    currentExitCode = MainWindow.EXIT_CODE_REBOOT
    cntlr = None
    while currentExitCode == MainWindow.EXIT_CODE_REBOOT:
        try:
            app = QApplication(sys.argv)
            app.setStyle(QStyleFactory.create('Fusion'))

            translator = QTranslator(app)
            translator.load(QLocale(language), "qtbase",
                            "_",  getAbsPath('locales'), ".qm")
            app.installTranslator(translator)

            initial_download()
            cntlr = main_window(app, translator, cntlr)
            currentExitCode = app.exec_()
            app = None
        except Exception as e:
            logger.exception("message")

    sys.exit(currentExitCode)


def main_window(app, translator, cntlr=None):
    """Run the main exectuable."""
    from PyQt5.QtCore import QSize
    from PyQt5.QtGui import QIcon
    from scctool.controller import MainController
    from scctool.view.main import MainWindow

    try:
        """Run the main program."""
        icon = QIcon()
        icon.addFile(getAbsPath('src/scct.ico'), QSize(32, 32))
        icon.addFile(getAbsPath('src/scct.png'), QSize(256, 256))
        app.setWindowIcon(icon)
        if cntlr is None:
            cntlr = MainController()
        MainWindow(cntlr, app, translator)
        logger.info("Starting...")
        return cntlr

    except Exception as e:
        logger.exception("message")
        raise


def initial_download():
    """Download the required data at an inital startup."""
    import scctool.tasks.updater
    from scctool.view.widgets import InitialUpdater

    if scctool.tasks.updater.needInitialUpdate(scctool.tasks.updater.getDataVersion()):
        InitialUpdater()
