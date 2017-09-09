"""StarCraft Casting Tool."""

import sys
import logging

logger = logging.getLogger('scctool')

__version__ = "0.25.8"
__latest_version__ = __version__
__new_version__ = False


def main():
    """Run StarCraft Casting Tool."""
    import PyQt5
    from scctool.view.main import MainWindow
    from scctool.controller import MainController
    from scctool.settings import getAbsPath

    try:
        """Run the main program."""
        app = PyQt5.QtWidgets.QApplication(sys.argv)
        PyQt5.QtWidgets.QApplication.setStyle(
            PyQt5.QtWidgets.QStyleFactory.create('Fusion'))
        icon = PyQt5.QtGui.QIcon()
        icon.addFile(getAbsPath('src/scct.ico'), PyQt5.QtCore.QSize(32, 32))
        icon.addFile(getAbsPath('src/scct.png'), PyQt5.QtCore.QSize(256, 256))
        app.setWindowIcon(icon)
        cntlr = MainController()
        MainWindow(cntlr, app)
        logger.info("Starting...")
        sys.exit(app.exec_())

    except Exception as e:
        logger.exception("message")
        raise
