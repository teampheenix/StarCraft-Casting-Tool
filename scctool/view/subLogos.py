"""Show logo manager sub window."""
import logging
import re

from PyQt5.QtWidgets import QWidget, QGridLayout, QGroupBox, QPushButton, QVBoxLayout,\
    QHBoxLayout, QListWidget, QListWidgetItem, QSpacerItem, QSizePolicy, QMenu, QFileDialog, \
    QErrorMessage, QInputDialog, QLineEdit, QMessageBox
from PyQt5.QtCore import QMutex, Qt, QSize, QPoint
from PyQt5.QtGui import QIcon

import scctool.settings
from scctool.view.subLiquipediaSearch import SubwindowLiquipediaSearch
from scctool.view.widgets import DragImageLabel, LogoDownloader

# create logger
module_logger = logging.getLogger('scctool.view.subLogos')


class SubwindowLogos(QWidget):
    """Show readme sub window."""

    def createWindow(self, mainWindow, controller, team):
        """Create readme sub window."""
        super(SubwindowLogos, self).__init__(None)
        self.controller = controller
        self.team = team
        self.mutex = QMutex()
        # self.setWindowIcon(
        #     QIcon(scctool.settings.getAbsPath(icon)))
        self.mainWindow = mainWindow
        self.setWindowModality(Qt.ApplicationModal)

        mainLayout = QGridLayout()

        self.iconsize = scctool.settings.logoManager.Logo._iconsize

        box = QGroupBox(
            _("Logo Team 1") + " - {}".format(mainWindow.le_team[0].text()))
        layout = QGridLayout()
        self.team1_icon = DragImageLabel(
            self.controller.logoManager.getTeam1(), 1)
        layout.addWidget(self.team1_icon, 0, 0, 5, 1)
        button = QPushButton(_("Load from File"))
        button.clicked.connect(lambda: self.logoFromFileDialog(1))
        layout.addWidget(button, 0, 1)
        button = QPushButton(_("Load from URL"))
        button.clicked.connect(lambda: self.logoFromUrlDialog(1))
        layout.addWidget(button, 1, 1)
        button = QPushButton(_("Search Liquipedia"))
        button.clicked.connect(lambda: self.liqupediaSearchDialog(
            1, mainWindow.le_team[0].text()))
        layout.addWidget(button, 2, 1)
        button = QPushButton(_("Add to Favorites"))
        button.clicked.connect(lambda: self.addFavorite(1))
        layout.addWidget(button, 3, 1)
        button = QPushButton(_("Remove"))
        button.clicked.connect(lambda: self.removeLogo(1))
        layout.addWidget(button, 4, 1)
        box.setLayout(layout)
        mainLayout.addWidget(box, 0, 0)

        box = QGroupBox("")
        layout = QVBoxLayout()
        button = QPushButton("↔")
        button.clicked.connect(self.swapLogos)
        layout.addWidget(button)

        button = QPushButton("→")
        button.clicked.connect(self.one2two)
        layout.addWidget(button)

        button = QPushButton("←")
        button.clicked.connect(self.two2one)
        layout.addWidget(button)

        box.setLayout(layout)
        mainLayout.addWidget(box, 0, 1)

        # mainLayout.addItem(QSpacerItem(
        #     0, 0, QSizePolicy.Expanding,
        #     QSizePolicy.Minimum), 0, 1)

        box = QGroupBox(
            _("Logo Team 2") + " - {}".format(mainWindow.le_team[1].text()))
        box.setAlignment(Qt.AlignRight)
        layout = QGridLayout()
        self.team2_icon = DragImageLabel(
            self.controller.logoManager.getTeam2(), 2)
        layout.addWidget(self.team2_icon, 0, 1, 5, 1)
        button = QPushButton(_("Load from File"))
        button.clicked.connect(lambda: self.logoFromFileDialog(2))
        layout.addWidget(button, 0, 0)
        button = QPushButton(_("Load from URL"))
        button.clicked.connect(lambda: self.logoFromUrlDialog(2))
        layout.addWidget(button, 1, 0)
        button = QPushButton(_("Search Liquipedia"))
        button.clicked.connect(lambda: self.liqupediaSearchDialog(
            2, mainWindow.le_team[1].text()))
        layout.addWidget(button, 2, 0)
        button = QPushButton(_("Add to Favorites"))
        button.clicked.connect(lambda: self.addFavorite(2))
        layout.addWidget(button, 3, 0)
        button = QPushButton(_("Remove"))
        button.clicked.connect(lambda: self.removeLogo(2))
        layout.addWidget(button, 4, 0)
        box.setLayout(layout)
        mainLayout.addWidget(box, 0, 2, 1, 2)

        box = QGroupBox(_("Favorites"))
        layout = QHBoxLayout()
        self.fav_list = QListWidget()
        self.fav_list.itemDoubleClicked.connect(self.doubleClicked)
        self.fav_list.setViewMode(QListWidget.IconMode)
        self.fav_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.fav_list.customContextMenuRequested.connect(
            self.listItemRightClickedFav)

        for logo in self.controller.logoManager.getFavorites():
            map = logo.provideQPixmap()
            item = QListWidgetItem(
                QIcon(map), logo.getDesc())
            self.fav_list.addItem(item)
        self.fav_list.setIconSize(QSize(75, 75))
        self.fav_list.setMaximumHeight(160)
        # list.setWrapping(False)
        # list.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.fav_list.setAcceptDrops(False)
        self.fav_list.setDragEnabled(False)
        layout.addWidget(self.fav_list)
        box.setLayout(layout)

        mainLayout.addWidget(box, 1, 0, 1, 4)

        box = QGroupBox(_("Last Used"))
        layout = QHBoxLayout()
        self.lastused_list = QListWidget()
        self.lastused_list.itemDoubleClicked.connect(self.doubleClicked)
        self.lastused_list.setViewMode(QListWidget.IconMode)
        self.lastused_list.setContextMenuPolicy(
            Qt.CustomContextMenu)
        self.lastused_list.customContextMenuRequested.connect(
            self.listItemRightClickedLastUsed)
        self.lastused_list.setIconSize(QSize(75, 75))
        self.lastused_list.setMaximumHeight(160)
        self.lastused_list.setAcceptDrops(False)
        self.lastused_list.setDragEnabled(False)
        self.refreshLastUsed()
        layout.addWidget(self.lastused_list)

        box.setLayout(layout)

        mainLayout.addWidget(box, 2, 0, 1, 4)

        # mainLayout.addItem(QSpacerItem(
        #     0, 0, QSizePolicy.Expanding,
        #     QSizePolicy.Minimum), 3, 0,1,2)

        buttonSave = QPushButton(_('&OK'))
        buttonSave.clicked.connect(self.close)
        mainLayout.addItem(QSpacerItem(
            0, 0, QSizePolicy.Expanding,
            QSizePolicy.Minimum), 4, 0, 1, 3)
        mainLayout.addWidget(buttonSave, 4, 3)
        self.setLayout(mainLayout)

        self.setWindowTitle(_("Logo Manager"))

        self.resize(QSize(self.sizeHint().width(),
                          mainWindow.size().height() * 0.95))
        relativeChange = QPoint(mainWindow.size().width() / 2,
                                mainWindow.size().height() / 2)\
            - QPoint(self.size().width() / 2,
                     self.size().height() / 2)
        self.move(mainWindow.pos() + relativeChange)

    def listItemRightClickedFav(self, QPos):
        self.listMenu = QMenu()
        menu_item = self.listMenu.addAction(_("Set Team 1 Logo"))
        menu_item.triggered.connect(lambda: self.setTeam1Logo(self.fav_list))
        menu_item = self.listMenu.addAction(_("Set Team 2 Logo"))
        menu_item.triggered.connect(lambda: self.setTeam2Logo(self.fav_list))
        menu_item = self.listMenu.addAction(_("Remove from Favorites"))
        menu_item.triggered.connect(self.deleteFavorite)
        parentPosition = self.fav_list.mapToGlobal(QPoint(0, 0))
        self.listMenu.move(parentPosition + QPos)
        self.listMenu.show()

    def listItemRightClickedLastUsed(self, QPos):
        self.listMenu = QMenu()
        menu_item = self.listMenu.addAction(_("Set Team 1 Logo"))
        menu_item.triggered.connect(
            lambda: self.setTeam1Logo(self.lastused_list))
        menu_item = self.listMenu.addAction(_("Set Team 2 Logo"))
        menu_item.triggered.connect(
            lambda: self.setTeam2Logo(self.lastused_list))
        menu_item = self.listMenu.addAction(_("Add to Favorites"))
        menu_item.triggered.connect(self.addFavoriteLastUsed)

        parentPosition = self.lastused_list.mapToGlobal(
            QPoint(0, 0))
        self.listMenu.move(parentPosition + QPos)
        self.listMenu.show()

    def deleteFavorite(self):
        item = self.fav_list.takeItem(self.fav_list.currentRow())
        map = item.icon().pixmap(self.iconsize)
        ident = self.controller.logoManager.pixmap2ident(map)
        self.controller.logoManager.removeFavorite(ident)
        item = None

    def setTeam1Logo(self, list):
        item = list.currentItem()
        map = item.icon().pixmap(self.iconsize)
        ident = self.controller.logoManager.pixmap2ident(map)
        logo = self.controller.logoManager.findLogo(ident)
        self.controller.logoManager.setTeam1Logo(logo)
        self.team1_icon.setPixmap(map)
        self.refreshLastUsed()

    def setTeam2Logo(self, list):
        item = list.currentItem()
        map = item.icon().pixmap(self.iconsize)
        ident = self.controller.logoManager.pixmap2ident(map)
        logo = self.controller.logoManager.findLogo(ident)
        self.controller.logoManager.setTeam2Logo(logo)
        self.team2_icon.setPixmap(map)
        self.refreshLastUsed()

    def removeLogo(self, team):
        if team == 1:
            self.controller.logoManager.resetTeam1Logo()
            self.team1_icon.setLogo(self.controller.logoManager.getTeam1())
        elif team == 2:
            self.controller.logoManager.resetTeam2Logo()
            self.team2_icon.setLogo(self.controller.logoManager.getTeam2())
        else:
            return

        self.refreshLastUsed()
        
    def doubleClicked(self, item):
        map = item.icon().pixmap(self.iconsize)
        ident = self.controller.logoManager.pixmap2ident(map)
        logo = self.controller.logoManager.findLogo(ident)
        if self.team == 1:
            self.controller.logoManager.setTeam1Logo(logo)
            self.team1_icon.setPixmap(map)
        else:
            self.controller.logoManager.setTeam2Logo(logo)
            self.team2_icon.setPixmap(map)
        self.refreshLastUsed()

    def addFavorite(self, team):
        if team == 1:
            map = self.team1_icon.pixmap()
        elif team == 2:
            map = self.team2_icon.pixmap()
        else:
            return

        ident = self.controller.logoManager.pixmap2ident(map)
        logo = self.controller.logoManager.findLogo(ident)
        item = QListWidgetItem(
            QIcon(map), logo.getDesc())

        if self.controller.logoManager.addFavorite(ident):
            self.fav_list.addItem(item)

    def addFavoriteLastUsed(self):
        item = self.lastused_list.currentItem()
        map = item.icon().pixmap(self.iconsize)
        item = QListWidgetItem(
            QIcon(map), item.text())
        ident = self.controller.logoManager.pixmap2ident(map)
        if self.controller.logoManager.addFavorite(ident):
            self.fav_list.addItem(item)

    def refreshLastUsed(self):
        self.lastused_list.clear()
        for logo in self.controller.logoManager.getLastUsed():
            map = logo.provideQPixmap()
            item = QListWidgetItem(
                QIcon(map), logo.getDesc())
            self.lastused_list.addItem(item)

    def swapLogos(self):
        self.controller.logoManager.swapTeamLogos()
        self.team1_icon.setLogo(self.controller.logoManager.getTeam1())
        self.team2_icon.setLogo(self.controller.logoManager.getTeam2())

    def one2two(self):
        self.controller.logoManager.setTeam2Logo(
            self.controller.logoManager.getTeam1())
        self.team2_icon.setLogo(self.controller.logoManager.getTeam2())
        self.refreshLastUsed()

    def two2one(self):
        self.controller.logoManager.setTeam1Logo(
            self.controller.logoManager.getTeam2())
        self.team1_icon.setLogo(self.controller.logoManager.getTeam1())
        self.refreshLastUsed()

    def logoFromFileDialog(self, team):
        """Open dialog for team logo."""
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog

        fileName, status = QFileDialog.getOpenFileName(
            self, _("Select Team Logo"), "",
            (_("Supported Images") + " ({})").format("*.png *.jpg"))
        if fileName:
            logo = self.controller.logoManager.newLogo()
            logo.fromFile(fileName)
            map = logo.provideQPixmap()

            if team == 1:
                self.controller.logoManager.setTeam1Logo(logo)
                self.team1_icon.setPixmap(map)
                self.refreshLastUsed()
            elif team == 2:
                self.controller.logoManager.setTeam2Logo(logo)
                self.team2_icon.setPixmap(map)
                self.refreshLastUsed()

    def logoFromUrlDialog(self, team):
        """Open dialog for team logo."""

        url = "http://"
        regex = re.compile(
            r'^(?:http|ftp)s?://'  # http:// or https://
            # domain...
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+'
            r'(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        emsg = QErrorMessage(self)
        emsg.setWindowModality(Qt.WindowModal)

        while True:

            url, status = QInputDialog.getText(self, _("Logo from URL"), _(
                "URL of Team Logo") + ":", QLineEdit.Normal, url)

            if status:

                if not regex.match(url):
                    QMessageBox.critical(
                        self, "Invalid URL", _('{} is not a valid URL.').format(url))
                    continue
                else:
                    logo = LogoDownloader(
                        self.controller, self, url).download()
                    logo.refreshData()
                    map = logo.provideQPixmap()

                    if team == 1:
                        self.controller.logoManager.setTeam1Logo(logo)
                        self.team1_icon.setPixmap(map)
                        self.refreshLastUsed()
                    elif team == 2:
                        self.controller.logoManager.setTeam2Logo(logo)
                        self.team2_icon.setPixmap(map)
                        self.refreshLastUsed()
                    break
            else:
                break

    def liqupediaSearchDialog(self, team, placeholder):
        self.mysubwindow = SubwindowLiquipediaSearch()
        self.mysubwindow.createWindow(self, placeholder, team)
        self.mysubwindow.show()

    def closeWindow(self):
        """Close window."""
        self.close()

    def closeEvent(self, event):
        """Handle close event."""
        try:
            self.controller.updateLogos()
            self.controller.matchData.metaChanged()
            event.accept()
        except Exception as e:
            module_logger.exception("message")
