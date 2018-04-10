"""Show readme sub window."""
import logging
import re

import markdown2
from PyQt5.QtCore import QPoint, QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QGridLayout, QPushButton, QSizePolicy,
                             QSpacerItem, QTextBrowser, QWidget)

import scctool.settings

# create logger
module_logger = logging.getLogger('scctool.view.subMarkdown')


class SubwindowMarkdown(QWidget):
    """Show readme sub window."""

    def createWindow(self, mainWindow, title, icon, markdown):
        """Create readme sub window."""
        super().__init__(None)
        self.setWindowIcon(
            QIcon(scctool.settings.getAbsPath(icon)))
        self.mainWindow = mainWindow

        self.createMarkdownViewer(markdown)

        mainLayout = QGridLayout()
        mainLayout.addWidget(self.viewer, 0, 0, 1, 3)
        closeButton = QPushButton(_("&OK"))
        closeButton.clicked.connect(self.close)
        mainLayout.addItem(QSpacerItem(
            0, 0, QSizePolicy.Expanding,
            QSizePolicy.Minimum), 1, 0)
        mainLayout.addWidget(closeButton, 1, 1)
        self.setLayout(mainLayout)

        self.setWindowTitle(title)

        self.resize(QSize(mainWindow.size().width()
                          * 0.9, self.sizeHint().height()))
        relativeChange = QPoint(mainWindow.size().width() / 2,
                                mainWindow.size().height() / 3)\
            - QPoint(self.size().width() / 2,
                     self.size().height() / 3)
        self.move(mainWindow.pos() + relativeChange)

    def createMarkdownViewer(self, markdown):
        """Create the readme viewer."""
        self.viewer = QTextBrowser()
        self.viewer.setReadOnly(True)
        self.viewer.setMinimumHeight(400)
        self.viewer.setOpenExternalLinks(True)
        # self.viewer.setAlignment(Qt.AlignJustify)
        html = markdown2.markdown_path(
            scctool.settings.getAbsPath(markdown))
        p = re.compile(r'<img.*?/>')
        html = p.sub('', html)

        html = '<p align="justify">' + html + '</p>'

        self.viewer.setHtml(html)
