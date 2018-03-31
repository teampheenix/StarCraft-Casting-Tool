"""Show readme sub window."""
import logging
import PyQt5
import requests
import urllib.parse
import re
import scctool.settings

from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest
from bs4 import BeautifulSoup

from scctool.view.widgets import LogoDownloader

# create logger
module_logger = logging.getLogger('scctool.view.subLiquipediaSearch')
base_url = 'http://liquipedia.net'


class SubwindowLiquipediaSearch(PyQt5.QtWidgets.QWidget):
    """Show readme sub window."""

    nams = dict()
    results = dict()
    data = dict()

    def createWindow(self, mainWindow, placeholder, team):
        """Create readme sub window."""
        super(SubwindowLiquipediaSearch, self).__init__(None)
        self.mainWindow = mainWindow
        self.controller = mainWindow.controller
        self.team = team
        self.setWindowIcon(
            PyQt5.QtGui.QIcon(scctool.settings.getAbsPath("src/liquipedia.png")))

        self.setWindowModality(PyQt5.QtCore.Qt.ApplicationModal)

        mainLayout = PyQt5.QtWidgets.QGridLayout()
        self.qle_search = PyQt5.QtWidgets.QLineEdit(placeholder)
        self.qle_search.setAlignment(PyQt5.QtCore.Qt.AlignCenter)
        self.qle_search.returnPressed.connect(self.search)
        mainLayout.addWidget(self.qle_search, 0, 0, 1, 2)
        searchButton = PyQt5.QtWidgets.QPushButton(_("Search"))
        searchButton.clicked.connect(self.search)
        mainLayout.addWidget(searchButton, 0, 2)

        box = PyQt5.QtWidgets.QGroupBox(_("Results"))
        layout = PyQt5.QtWidgets.QHBoxLayout()
        self.result_list = PyQt5.QtWidgets.QListWidget()
        self.result_list.setViewMode(PyQt5.QtWidgets.QListWidget.IconMode)
        self.result_list.setContextMenuPolicy(PyQt5.QtCore.Qt.CustomContextMenu)
        self.result_list.customContextMenuRequested.connect(
            self.listItemRightClicked)

        self.result_list.setIconSize(PyQt5.QtCore.QSize(75, 75))
        # list.setWrapping(False)
        # list.setVerticalScrollBarPolicy(PyQt5.QtCore.Qt.ScrollBarAlwaysOff)
        self.result_list.setAcceptDrops(False)
        self.result_list.setDragEnabled(False)
        layout.addWidget(self.result_list)
        box.setLayout(layout)

        mainLayout.addWidget(box, 1, 0, 1, 3)

        selectButton = PyQt5.QtWidgets.QPushButton(
            " " + _("Use Selected Logo") + " ")
        selectButton.clicked.connect(self.applyLogo)
        closeButton = PyQt5.QtWidgets.QPushButton(_("Cancel"))
        closeButton.clicked.connect(self.close)
        mainLayout.addItem(PyQt5.QtWidgets.QSpacerItem(
            0, 0, PyQt5.QtWidgets.QSizePolicy.Expanding,
            PyQt5.QtWidgets.QSizePolicy.Minimum), 2, 0)
        mainLayout.addWidget(closeButton, 2, 1)
        mainLayout.addWidget(selectButton, 2, 2)
        self.setLayout(mainLayout)

        self.setWindowTitle(_("Liqupedia Image Search"))

        self.resize(PyQt5.QtCore.QSize(mainWindow.size().width()
                                       * 0.9, self.sizeHint().height()))
        relativeChange = PyQt5.QtCore.QPoint(mainWindow.size().width() / 2,
                                             mainWindow.size().height() / 3)\
            - PyQt5.QtCore.QPoint(self.size().width() / 2,
                                  self.size().height() / 3)
        self.move(mainWindow.pos() + relativeChange)

    def clean(self):
        self.nams.clear()
        self.results.clear()
        self.data.clear()

    def search(self):
        PyQt5.QtWidgets.QApplication.setOverrideCursor(
            PyQt5.QtCore.Qt.WaitCursor)
        self.clean()
        loading_map = PyQt5.QtGui.QPixmap(
            scctool.settings.getAbsPath("src/loading.png"))
        try:
            self.result_list.clear()
            idx = 0
            for name, thumb in search_liquipedia(self.qle_search.text()):
                self.data[idx] = name
                name = name.replace('/commons/File:', '')
                self.results[idx] = PyQt5.QtWidgets.QListWidgetItem(
                    PyQt5.QtGui.QIcon(loading_map), name)
                self.results[idx].setSizeHint(PyQt5.QtCore.QSize(80, 90))
                url = base_url + thumb
                self.nams[idx] = QNetworkAccessManager()
                self.nams[idx].finished.connect(
                    lambda reply, i=idx: self.finishRequest(reply, i))
                self.nams[idx].get(QNetworkRequest(PyQt5.QtCore.QUrl(url)))
                self.result_list.addItem(self.results[idx])
                if idx == 0:
                    self.result_list.setCurrentItem(self.results[idx])
                idx += 1
        except Exception as e:
            module_logger.exception("message")
        finally:
            PyQt5.QtWidgets.QApplication.restoreOverrideCursor()

    def finishRequest(self, reply, idx):
        img = PyQt5.QtGui.QImage()
        img.loadFromData(reply.readAll())
        map = PyQt5.QtGui.QPixmap(img).scaled(
            75, 75, PyQt5.QtCore.Qt.KeepAspectRatio)
        self.results[idx].setIcon(PyQt5.QtGui.QIcon(map))

    def applyLogo(self, skip = False):
        item = self.result_list.currentItem()
        if item is not None and (skip or item.isSelected()):
            for idx, iteritem in self.results.items():
                if item is iteritem:
                    images = get_liquipedia_image(self.data[idx])
                    image = ""
                    for size in sorted(images):
                        if not image or size <= 600 * 600:
                            image = images[size]

                    self.downloadLogo(base_url + image)
                    break

        self.close()
        
    def listItemRightClicked(self, QPos):
        self.listMenu = PyQt5.QtWidgets.QMenu()
        menu_item = self.listMenu.addAction(_("Open on Liquipedia"))
        menu_item.triggered.connect(self.openLiquipedia)
        menu_item = self.listMenu.addAction(_("Use as Team Logo"))
        menu_item.triggered.connect(lambda: self.applyLogo(True))
        parentPosition = self.result_list.mapToGlobal(PyQt5.QtCore.QPoint(0, 0))
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


def search_liquipedia(search):
    params = {'title': 'Special:Search',
              'profile': 'advanced', 'fulltext': 'Search', 'ns6': 1}
    params['search'] = str(search)
    source = '{}/commons/index.php?{}'.format(
        base_url, urllib.parse.urlencode(params))

    urllib.parse.urlencode(params)
    r = requests.get(source)

    soup = BeautifulSoup(r.content, 'html.parser')
    try:
        for result in soup.find("ul", class_="mw-search-results").find_all("li"):
            try:
                link = result.find("a", class_="image")
                href = link['href']
                thumb = link.find("img")['src']
                data = result.find(
                    "div", class_="mw-search-result-data").contents[0]
                r = re.compile(
                    r'\((\d+,?\d*)\s+×\s+(\d+,?\d*)\s\((\d+)\s+([KM]*B)\)\)')
                data = r.match(data)
                pixel = int(data.group(1).replace(",", "")) * \
                    int(data.group(2).replace(",", ""))
                if(pixel > 10000):
                    yield href, thumb
            except Exception:
                continue
    except Exception:
        pass


def get_liquipedia_image(image):
    r = requests.get(base_url + image)
    regex = re.compile(r'(\d+,?\d*)\s+×\s+(\d+,?\d*)')
    soup = BeautifulSoup(r.content, 'html.parser')
    images = dict()
    for item in soup.select('div[class*="mw-filepage-"]'):
        for link in item.findAll("a"):
            data = regex.match(link.contents[0])
            pixel = int(data.group(1).replace(",", "")) * \
                int(data.group(2).replace(",", ""))
            images[pixel] = link['href']
    if len(images) == 0:
        link = soup.find("div", class_="fullMedia").find("a")
        data = regex.match(link.contents[0])
        try:
            pixel = int(data.group(1).replace(",", "")) * \
                int(data.group(2).replace(",", ""))
        except Exception:
            pixel = 0
        images[pixel] = link['href']

    return images
