import pytest
from PyQt5.QtWidgets import QApplication, QStyleFactory
from scctool.controller import MainController
from scctool.view.main import MainWindow
import scctool.settings
import sys


@pytest.fixture()
def scct_app():
    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create('Fusion'))
    scctool.settings.loadSettings()
    cntlr = MainController()
    main_window = MainWindow(
        cntlr, app, False)
    main_window.show()
    yield (main_window, cntlr)
    main_window.close()
    app.exit(1)
