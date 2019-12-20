"""StarCraft Casting Tool."""
import logging
import sys

from PyQt5.QtCore import QLocale, QTranslator
from PyQt5.QtWidgets import QApplication, QMessageBox, QStyleFactory

import scctool.settings
import scctool.settings.config
import scctool.settings.translation

logger = logging.getLogger(__name__)

__version__ = "2.7.14"
__latest_version__ = __version__
__new_version__ = False

_ = scctool.settings.translation.gettext


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
            message = _(
                'Critical error <i>`{error}`</i>! Please provide the log-file'
                ' to the developer of StarCraft Casting Tool. '
                '<a href="{link}">{link}</a>')
            QMessageBox.critical(
                None, _('Critical Error'),
                message.format(
                    error=e, link='https://discord.gg/G9hFEfh'),
                QMessageBox.Ok)
            break

    sys.exit(currentExitCode)


def main_window(app, showChangelog=False):
    """Run the main exectuable."""
    from PyQt5.QtCore import QSize
    from PyQt5.QtGui import QIcon
    from scctool.controller import MainController
    from scctool.view.main import MainWindow

    try:
        icon = QIcon()
        icon.addFile(scctool.settings.getResFile('scct.ico'), QSize(32, 32))
        icon.addFile(scctool.settings.getResFile('scct.png'), QSize(256, 256))
        app.setWindowIcon(icon)
        cntlr = MainController()
        logger.info("Starting... v{}".format(__version__))
        MainWindow(cntlr, app, showChangelog)
        return cntlr

    except Exception:
        logger.exception("Exception in main_window")
        raise


def initial_download():
    """Download the required data at an inital startup."""
    import scctool.tasks.updater
    from scctool.view.widgets import InitialUpdater
    scctool.tasks.updater.readJsonFile(True)
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
    """Select a language for gettext and PyQt."""
    scctool.settings.translation.set_language()

    language = scctool.settings.config.parser.get("SCT", "language")
    app.removeTranslator(translator)
    translator = QTranslator(app)
    translator.load(QLocale(language), "qtbase",
                    "_", scctool.settings.getLocalesDir(), ".qm")
    app.installTranslator(translator)

    return translator
