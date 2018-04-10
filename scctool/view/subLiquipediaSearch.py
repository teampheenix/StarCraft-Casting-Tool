"""Show readme sub window."""
import logging

from PyQt5.QtCore import QPoint, QSize, Qt, QUrl
from PyQt5.QtGui import QIcon, QImage, QPixmap
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest
from PyQt5.QtWidgets import (QApplication, QCompleter, QGridLayout, QGroupBox,
                             QHBoxLayout, QLineEdit, QListWidget,
                             QListWidgetItem, QMenu, QPushButton, QSizePolicy,
                             QSpacerItem, QWidget)

import scctool.settings
from scctool.tasks.liquipedia import LiquipediaGrabber
from scctool.view.widgets import LogoDownloader

# create logger
module_logger = logging.getLogger('scctool.view.subLiquipediaSearch')
base_url = 'http://liquipedia.net'


class SubwindowLiquipediaSearch(QWidget):
    """Show readme sub window."""

    nams = dict()
    results = dict()
    data = dict()

    def createWindow(self, mainWindow, placeholder, team):
        """Create readme sub window."""
        super().__init__(None)
        self.mainWindow = mainWindow
        self.controller = mainWindow.controller
        self.team = team
        self.liquipediaGrabber = LiquipediaGrabber()
        self.setWindowIcon(
            QIcon(scctool.settings.getAbsPath("src/liquipedia.png")))

        self.setWindowModality(Qt.ApplicationModal)

        mainLayout = QGridLayout()
        self.qle_search = QLineEdit(placeholder)
        self.qle_search.setAlignment(Qt.AlignCenter)
        self.qle_search.returnPressed.connect(self.search)
        completer = QCompleter(scctool.settings.config.getMyTeams() +
                               self.controller.historyManager.getTeamList(), self.qle_search)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        completer.setCompletionMode(
            QCompleter.UnfilteredPopupCompletion)
        completer.setWrapAround(True)
        self.qle_search.setCompleter(completer)

        mainLayout.addWidget(self.qle_search, 0, 0, 1, 2)
        searchButton = QPushButton(_("Search"))
        searchButton.clicked.connect(self.search)
        mainLayout.addWidget(searchButton, 0, 2)

        self.box = QGroupBox(_("Results"))
        layout = QHBoxLayout()
        self.result_list = QListWidget()
        self.result_list.setViewMode(QListWidget.IconMode)
        self.result_list.itemDoubleClicked.connect(self.doubleClicked)
        self.result_list.setContextMenuPolicy(
            Qt.CustomContextMenu)
        self.result_list.customContextMenuRequested.connect(
            self.listItemRightClicked)

        self.result_list.setIconSize(QSize(75, 75))
        # list.setWrapping(False)
        # list.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.result_list.setAcceptDrops(False)
        self.result_list.setDragEnabled(False)
        layout.addWidget(self.result_list)
        self.box.setLayout(layout)

        mainLayout.addWidget(self.box, 1, 0, 1, 3)

        selectButton = QPushButton(
            " " + _("Use Selected Logo") + " ")
        selectButton.clicked.connect(self.applyLogo)
        closeButton = QPushButton(_("Cancel"))
        closeButton.clicked.connect(self.close)
        mainLayout.addItem(QSpacerItem(
            0, 0, QSizePolicy.Expanding,
            QSizePolicy.Minimum), 2, 0)
        mainLayout.addWidget(closeButton, 2, 1)
        mainLayout.addWidget(selectButton, 2, 2)
        self.setLayout(mainLayout)

        self.setWindowTitle(_("Liqupedia Image Search"))

        self.resize(QSize(mainWindow.size().width()
                          * 0.9, self.sizeHint().height()))
        relativeChange = QPoint(mainWindow.size().width() / 2,
                                mainWindow.size().height() / 3)\
            - QPoint(self.size().width() / 2,
                     self.size().height() / 3)
        self.move(mainWindow.pos() + relativeChange)

    def clean(self):
        self.nams.clear()
        self.results.clear()
        self.data.clear()

    def search(self):
        QApplication.setOverrideCursor(
            Qt.WaitCursor)
        self.clean()
        loading_map = QPixmap(
            scctool.settings.getAbsPath("src/loading.png"))
        try:
            self.result_list.clear()
            idx = 0
            search_str = self.qle_search.text()
            for name, thumb in self.liquipediaGrabber.image_search(search_str):
                self.data[idx] = name
                name = name.replace('/commons/File:', '')
                self.results[idx] = QListWidgetItem(
                    QIcon(loading_map), name)
                self.results[idx].setSizeHint(QSize(80, 90))
                url = base_url + thumb
                self.nams[idx] = QNetworkAccessManager()
                self.nams[idx].finished.connect(
                    lambda reply, i=idx: self.finishRequest(reply, i))
                self.nams[idx].get(QNetworkRequest(QUrl(url)))
                self.result_list.addItem(self.results[idx])
                if idx == 0:
                    self.result_list.setCurrentItem(self.results[idx])
                idx += 1
            self.box.setTitle(
                _("Results for '{}': {}").format(search_str, idx))
        except Exception as e:
            module_logger.exception("message")
        finally:
            QApplication.restoreOverrideCursor()

    def finishRequest(self, reply, idx):
        img = QImage()
        img.loadFromData(reply.readAll())
        map = QPixmap(img).scaled(
            75, 75, Qt.KeepAspectRatio)
        self.results[idx].setIcon(QIcon(map))

    def applyLogo(self, skip=False):
        item = self.result_list.currentItem()
        if item is not None and (skip or item.isSelected()):
            for idx, iteritem in self.results.items():
                if item is iteritem:
                    images = self.liquipediaGrabber.get_images(self.data[idx])
                    image = ""
                    for size in sorted(images):
                        if not image or size <= 600 * 600:
                            image = images[size]

                    self.downloadLogo(base_url + image)
                    break

        self.close()

    def doubleClicked(self, item):
        for idx, iteritem in self.results.items():
            if item is iteritem:
                images = self.liquipediaGrabber.get_images(self.data[idx])
                image = ""
                for size in sorted(images):
                    if not image or size <= 600 * 600:
                        image = images[size]

                self.downloadLogo(base_url + image)
                break

        self.close()

    def listItemRightClicked(self, QPos):
        self.listMenu = QMenu()
        menu_item = self.listMenu.addAction(_("Open on Liquipedia"))
        menu_item.triggered.connect(self.openLiquipedia)
        menu_item = self.listMenu.addAction(_("Use as Team Logo"))
        menu_item.triggered.connect(lambda: self.applyLogo(True))
        parentPosition = self.result_list.mapToGlobal(
            QPoint(0, 0))
        self.listMenu.move(parentPosition + QPos)
        self.listMenu.show()

    def openLiquipedia(self):
        item = self.result_list.currentItem()
        for idx, iteritem in self.results.items():
            if item is iteritem:
                url = base_url + self.data[idx]
                self.controller.openURL(url)
                break

    def downloadLogo(self, url):
        logo = LogoDownloader(
            self.controller, self, url).download()
        logo.refreshData()
        map = logo.provideQPixmap()

        if self.team == 1:
            self.controller.logoManager.setTeam1Logo(logo)
            self.mainWindow.team1_icon.setPixmap(map)
            self.mainWindow.refreshLastUsed()
        elif self.team == 2:
            self.controller.logoManager.setTeam2Logo(logo)
            self.mainWindow.team2_icon.setPixmap(map)
            self.mainWindow.refreshLastUsed()

    def closeEvent(self, event):
        """Handle close event."""
        try:
            self.clean()
            event.accept()
        except Exception as e:
            module_logger.exception("message")
