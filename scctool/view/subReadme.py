#!/usr/bin/env python
import logging

# create logger
module_logger = logging.getLogger('scctool.view.subReadme')

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from scctool.view.widgets import *
import markdown2
import re


class subwindowReadme(QWidget):
    def createWindow(self, mainWindow):
        super(subwindowReadme, self).__init__(None)
        self.setWindowIcon(QIcon('src/readme.ico'))
        self.mainWindow = mainWindow

        self.createReadmeViewer()

        mainLayout = QGridLayout()
        mainLayout.addWidget(self.viewer, 0, 0, 1, 3)
        closeButton = QPushButton("&OK")
        closeButton.clicked.connect(self.close)
        mainLayout.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum), 1, 0)
        mainLayout.addWidget(closeButton, 1, 1)
        self.setLayout(mainLayout)

        self.setWindowTitle("Readme")

        self.resize(QSize(mainWindow.size().width()
                          * 0.9, self.sizeHint().height()))
        self.move(mainWindow.pos() + QPoint(mainWindow.size().width() / 2, mainWindow.size().height() / 3)
                  - QPoint(self.size().width() / 2, self.size().height() / 3))

    def createReadmeViewer(self):
        self.viewer = QTextBrowser()
        self.viewer.setReadOnly(True)
        self.viewer.setMinimumHeight(400)
        self.viewer.setOpenExternalLinks(True)
        # self.viewer.setAlignment(Qt.AlignJustify)
        html = markdown2.markdown_path("README.md")
        p = re.compile(r'<img.*?/>')
        html = p.sub('', html)

        html = '<p align="justify">' + html + '</p>'

        self.viewer.setHtml(html)
