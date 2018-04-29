"""StarCraft Casting Tool."""

import gettext
import logging
import sys

from PyQt5.QtCore import QLocale, QTranslator
from PyQt5.QtWidgets import QApplication, QStyleFactory

import scctool.settings
import scctool.settings.config
from scctool.settings import getLocalesDir, getResFile

logger = logging.getLogger('scctool')

__version__ = "2.0.0"
__latest_version__ = __version__
__new_version__ = False

language = scctool.settings.config.parser.get("SCT", "language")

try:
    lang = gettext.translation(
        'messages', localedir=getLocalesDir(), languages=[language])
except Exception:
    lang = gettext.NullTranslations()

lang.install()


def main():
    """Run StarCraft Casting Tool."""
    global language
    from scctool.view.main import MainWindow
    from PyQt5.QtCore import QSize
    from PyQt5.QtGui import QIcon

    currentExitCode = MainWindow.EXIT_CODE_REBOOT
    cntlr = None
    while currentExitCode == MainWindow.EXIT_CODE_REBOOT:
        try:
            app = QApplication(sys.argv)
            app.setStyle(QStyleFactory.create('Fusion'))
            translator = QTranslator(app)
            translator.load(QLocale(language), "qtbase",
                            "_",  getLocalesDir(), ".qm")
            app.installTranslator(translator)

            icon = QIcon()
            icon.addFile(getResFile('scct.ico'), QSize(32, 32))
            app.setWindowIcon(icon)

            showChangelog = initial_download()
            cntlr = main_window(app, translator, cntlr, showChangelog)
            currentExitCode = app.exec_()
            app = None
        except Exception as e:
            logger.exception("message")
            break

    sys.exit(currentExitCode)


def main_window(app, translator, cntlr=None, showChangelog=False):
    """Run the main exectuable."""
    from PyQt5.QtCore import QSize
    from PyQt5.QtGui import QIcon
    from scctool.controller import MainController
    from scctool.view.main import MainWindow

    try:
        """Run the main program."""
        icon = QIcon()
        icon.addFile(getResFile('scct.ico'), QSize(32, 32))
        icon.addFile(getResFile('scct.png'), QSize(256, 256))
        app.setWindowIcon(icon)
        if cntlr is None:
            pass
        cntlr = MainController()
        MainWindow(cntlr, app, translator, showChangelog)
        logger.info("Starting...")
        return cntlr

    except Exception as e:
        logger.exception("message")
        raise


def initial_download():
    """Download the required data at an inital startup."""
    import scctool.tasks.updater
    from scctool.view.widgets import InitialUpdater

    version = scctool.tasks.updater.getDataVersion()
    restart_flag = scctool.tasks.updater.getRestartFlag()

    if scctool.tasks.updater.needInitialUpdate(version):
        InitialUpdater()
    elif restart_flag:
        InitialUpdater(version)

    scctool.tasks.updater.setRestartFlag(False)

    return restart_flag
