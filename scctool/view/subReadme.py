"""Show readme sub window."""
import logging
from PyQt5.QtWidgets import QWidget, QGridLayout, QPushButton, QSpacerItem,\
    QSizePolicy, QTextBrowser
from PyQt5.QtCore import QSize, QPoint
from PyQt5.QtGui import QIcon

import markdown2
import scctool.settings
import re
# create logger
module_logger = logging.getLogger('scctool.view.subReadme')


class SubwindowReadme(QWidget):
    """Show readme sub window."""

    def createWindow(self, mainWindow):
        """Create readme sub window."""
        super(SubwindowReadme, self).__init__(None)
        self.setWindowIcon(
            QIcon(scctool.settings.getAbsPath('src/readme.ico')))
        self.mainWindow = mainWindow

        self.createReadmeViewer()

        mainLayout = QGridLayout()
        mainLayout.addWidget(self.viewer, 0, 0, 1, 3)
        closeButton = QPushButton("&OK")
        closeButton.clicked.connect(self.close)
        mainLayout.addItem(QSpacerItem(
            0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum), 1, 0)
        mainLayout.addWidget(closeButton, 1, 1)
        self.setLayout(mainLayout)

        self.setWindowTitle("Readme")

        self.resize(QSize(mainWindow.size().width()
                          * 0.9, self.sizeHint().height()))
        relativeChange = QPoint(mainWindow.size().width() / 2,
                                mainWindow.size().height() / 3)\
            - QPoint(self.size().width() / 2, self.size().height() / 3)
        self.move(mainWindow.pos() + relativeChange)

    def createReadmeViewer(self):
        """Create the readme viewer."""
        self.viewer = QTextBrowser()
        self.viewer.setReadOnly(True)
        self.viewer.setMinimumHeight(400)
        self.viewer.setOpenExternalLinks(True)
        # self.viewer.setAlignment(Qt.AlignJustify)
        html = markdown2.markdown_path(
            scctool.settings.getAbsPath("README.md"))
        p = re.compile(r'<img.*?/>')
        html = p.sub('', html)

        html = '<p align="justify">' + html + '</p>'

        self.viewer.setHtml(html)
