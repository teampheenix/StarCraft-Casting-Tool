"""Show readme sub window."""
import logging
import PyQt5

import scctool.settings
from scctool.view.widgets import DragImageLabel
# create logger
module_logger = logging.getLogger('scctool.view.subIcons')


class SubwindowIcons(PyQt5.QtWidgets.QWidget):
    """Show readme sub window."""

    def createWindow(self, mainWindow, controller):
        """Create readme sub window."""
        super(SubwindowIcons, self).__init__(None)
        self.controller = controller
        # self.setWindowIcon(
        #     PyQt5.QtGui.QIcon(scctool.settings.getAbsPath(icon)))
        self.mainWindow = mainWindow
        self.setWindowModality(PyQt5.QtCore.Qt.ApplicationModal)

        mainLayout = PyQt5.QtWidgets.QGridLayout()

        self.iconsize = 120

        box = PyQt5.QtWidgets.QGroupBox(_("Logo Team 1"))
        layout = PyQt5.QtWidgets.QGridLayout()
        self.team1_icon = DragImageLabel(
            self.controller.logoManager.getTeam1().getAbsFile())
        layout.addWidget(self.team1_icon, 0, 0, 5, 1)
        layout.addWidget(PyQt5.QtWidgets.QPushButton(
            _("Load from File")), 0, 1)
        layout.addWidget(PyQt5.QtWidgets.QPushButton(_("Load from URL")), 1, 1)
        layout.addWidget(PyQt5.QtWidgets.QPushButton(
            _("Search Liquipedia")), 2, 1)
        layout.addWidget(PyQt5.QtWidgets.QPushButton(
            _("Add to Favorites")), 3, 1)
        layout.addWidget(PyQt5.QtWidgets.QPushButton(_("Remove")), 4, 1)
        box.setLayout(layout)
        mainLayout.addWidget(box, 0, 0)

        box = PyQt5.QtWidgets.QGroupBox("")
        layout = PyQt5.QtWidgets.QVBoxLayout()
        layout.addWidget(PyQt5.QtWidgets.QPushButton("↔"))
        layout.addWidget(PyQt5.QtWidgets.QPushButton("→"))
        layout.addWidget(PyQt5.QtWidgets.QPushButton("←"))
        box.setLayout(layout)
        mainLayout.addWidget(box, 0, 1)

        # mainLayout.addItem(PyQt5.QtWidgets.QSpacerItem(
        #     0, 0, PyQt5.QtWidgets.QSizePolicy.Expanding,
        #     PyQt5.QtWidgets.QSizePolicy.Minimum), 0, 1)

        box = PyQt5.QtWidgets.QGroupBox(_("Logo Team 2"))
        box.setAlignment(PyQt5.QtCore.Qt.AlignRight)
        layout = PyQt5.QtWidgets.QGridLayout()
        self.team2_icon = DragImageLabel(
            self.controller.logoManager.getTeam2().getAbsFile())
        layout.addWidget(self.team2_icon, 0, 1, 5, 1)
        layout.addWidget(PyQt5.QtWidgets.QPushButton(
            _("Load from File")), 0, 0)
        layout.addWidget(PyQt5.QtWidgets.QPushButton(_("Load from URL")), 1, 0)
        layout.addWidget(PyQt5.QtWidgets.QPushButton(
            _("Search Liquipedia")), 2, 0)
        layout.addWidget(PyQt5.QtWidgets.QPushButton(
            _("Add to Favorites")), 3, 0)
        layout.addWidget(PyQt5.QtWidgets.QPushButton(_("Remove")), 4, 0)
        box.setLayout(layout)
        mainLayout.addWidget(box, 0, 2, 1, 2)

        box = PyQt5.QtWidgets.QGroupBox(_("Favorites"))
        layout = PyQt5.QtWidgets.QHBoxLayout()
        self.fav_list = PyQt5.QtWidgets.QListWidget()
        self.fav_list.setViewMode(PyQt5.QtWidgets.QListWidget.IconMode)
        self.fav_list.setContextMenuPolicy(PyQt5.QtCore.Qt.CustomContextMenu)
        self.fav_list.customContextMenuRequested.connect(
            self.listItemRightClickedFav)

        for logo in self.controller.logoManager.getFavorites():
            map = PyQt5.QtGui.QPixmap(logo.getAbsFile()).scaled(
                self.iconsize, self.iconsize, PyQt5.QtCore.Qt.KeepAspectRatio)
            item = PyQt5.QtWidgets.QListWidgetItem(
                PyQt5.QtGui.QIcon(map), logo.getDesc())
            self.fav_list.addItem(item)
        self.fav_list.setIconSize(PyQt5.QtCore.QSize(75, 75))
        self.fav_list.setMaximumHeight(160)
        # list.setWrapping(False)
        # list.setVerticalScrollBarPolicy(PyQt5.QtCore.Qt.ScrollBarAlwaysOff)
        layout.addWidget(self.fav_list)
        box.setLayout(layout)

        mainLayout.addWidget(box, 1, 0, 1, 4)

        box = PyQt5.QtWidgets.QGroupBox(_("Last Used"))
        layout = PyQt5.QtWidgets.QHBoxLayout()
        self.lastused_list = PyQt5.QtWidgets.QListWidget()
        self.lastused_list.setViewMode(PyQt5.QtWidgets.QListWidget.IconMode)
        self.lastused_list.setContextMenuPolicy(
            PyQt5.QtCore.Qt.CustomContextMenu)
        self.lastused_list.customContextMenuRequested.connect(
            self.listItemRightClickedLastUsed)
        for logo in self.controller.logoManager.getLastUsed():
            map = PyQt5.QtGui.QPixmap(logo.getAbsFile()).scaled(
                self.iconsize, self.iconsize, PyQt5.QtCore.Qt.KeepAspectRatio)
            item = PyQt5.QtWidgets.QListWidgetItem(
                PyQt5.QtGui.QIcon(map), logo.getDesc())
            self.lastused_list.addItem(item)
        self.lastused_list.setIconSize(PyQt5.QtCore.QSize(75, 75))
        self.lastused_list.setMaximumHeight(160)
        self.lastused_list.setAcceptDrops(False)
        layout.addWidget(self.lastused_list)

        box.setLayout(layout)

        mainLayout.addWidget(box, 2, 0, 1, 4)

        # mainLayout.addItem(PyQt5.QtWidgets.QSpacerItem(
        #     0, 0, PyQt5.QtWidgets.QSizePolicy.Expanding,
        #     PyQt5.QtWidgets.QSizePolicy.Minimum), 3, 0,1,2)

        buttonSave = PyQt5.QtWidgets.QPushButton(_('&OK'))
        buttonSave.clicked.connect(self.close)
        mainLayout.addItem(PyQt5.QtWidgets.QSpacerItem(
            0, 0, PyQt5.QtWidgets.QSizePolicy.Expanding,
            PyQt5.QtWidgets.QSizePolicy.Minimum), 4, 0, 1, 3)
        mainLayout.addWidget(buttonSave, 4, 3)
        self.setLayout(mainLayout)

        self.setWindowTitle(_("Logo Manager"))

        self.resize(PyQt5.QtCore.QSize(self.sizeHint().width(),
                                       mainWindow.size().height() * 0.95))
        relativeChange = PyQt5.QtCore.QPoint(mainWindow.size().width() / 2,
                                             mainWindow.size().height() / 2)\
            - PyQt5.QtCore.QPoint(self.size().width() / 2,
                                  self.size().height() / 2)
        self.move(mainWindow.pos() + relativeChange)

    def listItemRightClickedFav(self, QPos):
        self.listMenu = PyQt5.QtWidgets.QMenu()
        menu_item = self.listMenu.addAction(_("Set Team 1 Logo"))
        menu_item.triggered.connect(lambda: self.setTeam1Logo(self.fav_list))
        menu_item = self.listMenu.addAction(_("Set Team 2 Logo"))
        menu_item.triggered.connect(lambda: self.setTeam2Logo(self.fav_list))
        menu_item = self.listMenu.addAction(_("Remove from Favorites"))
        menu_item.triggered.connect(self.deleteFavorite)
        parentPosition = self.fav_list.mapToGlobal(PyQt5.QtCore.QPoint(0, 0))
        self.listMenu.move(parentPosition + QPos)
        self.listMenu.show()

    def listItemRightClickedLastUsed(self, QPos):
        self.listMenu = PyQt5.QtWidgets.QMenu()
        menu_item = self.listMenu.addAction(_("Set Team 1 Logo"))
        menu_item.triggered.connect(
            lambda: self.setTeam1Logo(self.lastused_list))
        menu_item = self.listMenu.addAction(_("Set Team 2 Logo"))
        menu_item.triggered.connect(
            lambda: self.setTeam2Logo(self.lastused_list))
        menu_item = self.listMenu.addAction(_("Add to Favorites"))
        menu_item.triggered.connect(self.addFavoriteLastUsed)

        parentPosition = self.lastused_list.mapToGlobal(
            PyQt5.QtCore.QPoint(0, 0))
        self.listMenu.move(parentPosition + QPos)
        self.listMenu.show()

    def deleteFavorite(self):
        item = self.fav_list.takeItem(self.fav_list.currentRow())
        item = None

    def setTeam1Logo(self, list):
        item = list.currentItem()
        map = item.icon().pixmap(self.iconsize)
        map = map.scaled(self.iconsize, self.iconsize,
                         PyQt5.QtCore.Qt.KeepAspectRatio)
        self.team1_icon.setPixmap(map)

    def setTeam2Logo(self, list):
        item = list.currentItem()
        map = item.icon().pixmap(self.iconsize)
        map = map.scaled(self.iconsize, self.iconsize,
                         PyQt5.QtCore.Qt.KeepAspectRatio)
        self.team2_icon.setPixmap(map)

    def addFavoriteLastUsed(self):
        item = self.lastused_list.currentItem()
        map = item.icon().pixmap(self.iconsize)
        map = map.scaled(self.iconsize, self.iconsize,
                         PyQt5.QtCore.Qt.KeepAspectRatio)
        item = PyQt5.QtWidgets.QListWidgetItem(
            PyQt5.QtGui.QIcon(map), item.text())
        self.fav_list.addItem(item)
