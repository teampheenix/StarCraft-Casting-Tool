"""StarCraft Casting Tool."""

import gettext
import logging
import sys

from PyQt5.QtCore import QLocale, QTranslator
from PyQt5.QtWidgets import QApplication, QStyleFactory

import scctool.settings
import scctool.settings.config

logger = logging.getLogger('scctool')

__version__ = "2.1.4"
__latest_version__ = __version__
__new_version__ = False


def main():
    """Run StarCraft Casting Tool."""
    from scctool.view.main import MainWindow
    from PyQt5.QtCore import QSize
    from PyQt5.QtGui import QIcon

    translator = None

    currentExitCode = MainWindow.EXIT_CODE_REBOOT
    while currentExitCode == MainWindow.EXIT_CODE_REBOOT:
        try:
            scctool.settings.loadSettings()
            app = QApplication(sys.argv)
            app.setStyle(QStyleFactory.create('Fusion'))
            translator = choose_language(app, translator)

            icon = QIcon()
            icon.addFile(scctool.settings.getResFile(
                'scct.ico'), QSize(32, 32))
            app.setWindowIcon(icon)

            showChangelog, updater = initial_download()
            if updater:
                scctool.settings.loadSettings()
            main_window(app, showChangelog)
            currentExitCode = app.exec_()
            app = None
        except Exception as e:
            logger.exception("message")
            break

    sys.exit(currentExitCode)


def main_window(app, showChangelog=False):
    """Run the main exectuable."""
    from PyQt5.QtCore import QSize
    from PyQt5.QtGui import QIcon
    from scctool.controller import MainController
    from scctool.view.main import MainWindow

    try:
        """Run the main program."""
        icon = QIcon()
        icon.addFile(scctool.settings.getResFile('scct.ico'), QSize(32, 32))
        icon.addFile(scctool.settings.getResFile('scct.png'), QSize(256, 256))
        app.setWindowIcon(icon)
        cntlr = MainController()
        MainWindow(cntlr, app, showChangelog)
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
    updater = False

    if scctool.tasks.updater.needInitialUpdate(version):
        InitialUpdater()
        updater = True
    elif restart_flag:
        InitialUpdater(version)
        updater = True

    scctool.tasks.updater.setRestartFlag(False)

    return restart_flag, updater


def choose_language(app, translator):
    language = scctool.settings.config.parser.get("SCT", "language")

    try:
        lang = gettext.translation(
            'messages',
            localedir=scctool.settings.getLocalesDir(),
            languages=[language])
    except Exception:
        lang = gettext.NullTranslations()

    lang.install()
    app.removeTranslator(translator)
    translator = QTranslator(app)
    translator.load(QLocale(language), "qtbase",
                    "_", scctool.settings.getLocalesDir(), ".qm")
    app.installTranslator(translator)

    return translator
