"""Show readme sub window."""
import logging
import PyQt5

import markdown2
import scctool.settings
import re
# create logger
module_logger = logging.getLogger('scctool.view.subReadme')


class SubwindowReadme(PyQt5.QtWidgets.QWidget):
    """Show readme sub window."""

    def createWindow(self, mainWindow):
        """Create readme sub window."""
        super(SubwindowReadme, self).__init__(None)
        self.setWindowIcon(
            PyQt5.QtGui.QIcon(scctool.settings.getAbsPath('src/readme.ico')))
        self.mainWindow = mainWindow

        self.createReadmeViewer()

        mainLayout = PyQt5.QtWidgets.QGridLayout()
        mainLayout.addWidget(self.viewer, 0, 0, 1, 3)
        closeButton = PyQt5.QtWidgets.QPushButton("&OK")
        closeButton.clicked.connect(self.close)
        mainLayout.addItem(PyQt5.QtWidgets.QSpacerItem(
            0, 0, PyQt5.QtWidgets.QSizePolicy.Expanding,
            PyQt5.QtWidgets.QSizePolicy.Minimum), 1, 0)
        mainLayout.addWidget(closeButton, 1, 1)
        self.setLayout(mainLayout)

        self.setWindowTitle("Readme")

        self.resize(PyQt5.QtCore.QSize(mainWindow.size().width()
                                       * 0.9, self.sizeHint().height()))
        relativeChange = PyQt5.QtCore.QPoint(mainWindow.size().width() / 2,
                                             mainWindow.size().height() / 3)\
            - PyQt5.QtCore.QPoint(self.size().width() / 2,
                                  self.size().height() / 3)
        self.move(mainWindow.pos() + relativeChange)

    def createReadmeViewer(self):
        """Create the readme viewer."""
        self.viewer = PyQt5.QtWidgets.QTextBrowser()
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
