"""Show readme sub window."""
import logging
import PyQt5

import scctool.settings
# create logger
module_logger = logging.getLogger('scctool.view.subLiquipediaSearch')


class SubwindowLiquipediaSearch(PyQt5.QtWidgets.QWidget):
    """Show readme sub window."""

    def createWindow(self, mainWindow):
        """Create readme sub window."""
        super(SubwindowLiquipediaSearch, self).__init__(None)
        self.mainWindow = mainWindow
        self.setWindowIcon(
            PyQt5.QtGui.QIcon(scctool.settings.getAbsPath("src/liquipedia.png")))
            
        self.setWindowModality(PyQt5.QtCore.Qt.ApplicationModal)
        
        
        mainLayout = PyQt5.QtWidgets.QGridLayout()
        self.qle_search = PyQt5.QtWidgets.QLineEdit()
        self.qle_search.setAlignment(PyQt5.QtCore.Qt.AlignCenter)
        mainLayout.addWidget(self.qle_search, 0, 0)
        searchButton = PyQt5.QtWidgets.QPushButton(_("Search"))
        mainLayout.addWidget(searchButton, 0, 1)
        
        
        box = PyQt5.QtWidgets.QGroupBox(_("Results"))
        layout = PyQt5.QtWidgets.QHBoxLayout()
        self.result_list = PyQt5.QtWidgets.QListWidget()
        self.result_list.setViewMode(PyQt5.QtWidgets.QListWidget.IconMode)

       
        self.result_list.setIconSize(PyQt5.QtCore.QSize(75, 75))
        # list.setWrapping(False)
        # list.setVerticalScrollBarPolicy(PyQt5.QtCore.Qt.ScrollBarAlwaysOff)
        self.result_list.setAcceptDrops(False)
        self.result_list.setDragEnabled(False)
        layout.addWidget(self.result_list)
        box.setLayout(layout)

        mainLayout.addWidget(box, 1, 0, 1, 2)
        
        closeButton = PyQt5.QtWidgets.QPushButton(_("&OK"))
        closeButton.clicked.connect(self.close)
        mainLayout.addItem(PyQt5.QtWidgets.QSpacerItem(
            0, 0, PyQt5.QtWidgets.QSizePolicy.Expanding,
            PyQt5.QtWidgets.QSizePolicy.Minimum), 2, 0)
        mainLayout.addWidget(closeButton, 2, 1)
        self.setLayout(mainLayout)

        self.setWindowTitle(_("Liqupedia Image Search"))

        self.resize(PyQt5.QtCore.QSize(mainWindow.size().width()
                                       * 0.9, self.sizeHint().height()))
        relativeChange = PyQt5.QtCore.QPoint(mainWindow.size().width() / 2,
                                             mainWindow.size().height() / 3)\
            - PyQt5.QtCore.QPoint(self.size().width() / 2,
                                  self.size().height() / 3)
        self.move(mainWindow.pos() + relativeChange)
