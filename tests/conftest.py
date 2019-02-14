import os
import random
import shutil
import sys

import pytest
from PyQt5.QtWidgets import QApplication, QStyleFactory

import scctool.settings
from scctool.controller import MainController
from scctool.view.main import MainWindow


@pytest.fixture()
def scct_app(tmpdir_factory):
    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create('Fusion'))
    tmp_dir = tmpdir_factory.getbasetemp()
    if tmp_dir.join('profiles').check(exists=0):
        profile_dir = tmp_dir.mkdir('profiles').mkdir(
            hex(random.randint(49152, 65535))[2:])
        casting_html_src = os.path.normpath(os.path.join(
            os.path.dirname(__file__), '../casting_html'))
        assert os.path.exists(casting_html_src)
        casting_html = profile_dir.join('casting_html')
        if casting_html.check(exists=0):
            shutil.copytree(
                casting_html_src,
                casting_html)
    scctool.settings.loadSettings(str(tmp_dir), True)
    cntlr = MainController()
    main_window = MainWindow(
        cntlr, app, False)
    main_window.show()
    yield (main_window, cntlr)
    main_window.close()
    cntlr.cleanUp()
    app.exit(1)
