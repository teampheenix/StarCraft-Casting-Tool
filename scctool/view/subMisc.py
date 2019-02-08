"""Subwindow with miscellaneous settings."""
import logging
import os.path

import humanize  # pip install humanize
import requests
from PyQt5.QtCore import QPoint, QRegExp, QSize, Qt
from PyQt5.QtGui import QIcon, QKeySequence, QPixmap, QRegExpValidator
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QFileDialog,
                             QGridLayout, QGroupBox, QHBoxLayout, QInputDialog,
                             QLabel, QListWidget, QListWidgetItem, QMessageBox,
                             QPushButton, QShortcut, QSizePolicy, QSpacerItem,
                             QTabWidget, QVBoxLayout, QWidget)

import scctool.settings
import scctool.settings.translation
from scctool.tasks.liquipedia import LiquipediaGrabber, MapNotFound
from scctool.view.widgets import (AliasTreeView, AligulacTreeView, ListTable,
                                  MapDownloader, MonitoredLineEdit)


# create logger
module_logger = logging.getLogger(__name__)
_ = scctool.settings.translation.gettext


class SubwindowMisc(QWidget):
    """Show subwindow with miscellaneous settings."""

    current_tab = -1

    def createWindow(self, mainWindow, tab=''):
        """Create subwindow with miscellaneous settings."""
        try:
            parent = None
            super().__init__(parent)
            # self.setWindowFlags(Qt.WindowStaysOnTopHint)

            self.setWindowIcon(
                QIcon(scctool.settings.getResFile('settings.png')))
            self.setWindowModality(Qt.ApplicationModal)
            self.mainWindow = mainWindow
            self.passEvent = False
            self.controller = mainWindow.controller
            self.__dataChanged = False

            self.createButtonGroup()
            self.createTabs(tab)

            mainLayout = QVBoxLayout()

            mainLayout.addWidget(self.tabs)
            mainLayout.addLayout(self.buttonGroup)

            self.setLayout(mainLayout)

            self.resize(QSize(mainWindow.size().width() * 0.9,
                              self.sizeHint().height()))
            relativeChange = QPoint(mainWindow.size().width() / 2,
                                    mainWindow.size().height() / 3)\
                - QPoint(self.size().width() / 2,
                         self.size().height() / 3)
            self.move(mainWindow.pos() + relativeChange)

            self.setWindowTitle(_("Miscellaneous Settings"))

        except Exception:
            module_logger.exception("message")

    def createTabs(self, tab=''):
        """Create tabs."""
        self.tabs = QTabWidget()

        self.createMapsBox()
        self.createFavBox()
        self.createAliasBox()
        self.createOcrBox()
        self.createAlphaBox()
        self.createSC2ClientAPIBox()
        self.createAligulacTab()

        # Add tabs
        self.tabs.addTab(self.mapsBox, _("Map Manager"))
        self.tabs.addTab(self.favBox, _("Favorites"))
        self.tabs.addTab(self.aliasBox, _("Alias"))
        self.tabs.addTab(self.ocrBox, _("OCR"))
        self.tabs.addTab(self.alphaBox, _("AlphaTL && Ingame Score"))
        self.tabs.addTab(self.clientapiBox, _("SC2 Client API"))
        self.tabs.addTab(self.aligulacTab, _("Aligulac"))

        table = dict()
        table['mapmanager'] = 0
        table['favorites'] = 1
        table['alias'] = 2
        table['ocr'] = 3
        table['alphatl'] = 4
        table['sc2clientapi'] = 5
        table['aligulac'] = 6
        self.tabs.setCurrentIndex(table.get(tab, SubwindowMisc.current_tab))
        self.tabs.currentChanged.connect(self.tabChanged)

    @classmethod
    def tabChanged(cls, idx):
        """Save the current tab index."""
        SubwindowMisc.current_tab = idx

    def changed(self):
        """Handle changes."""
        self.__dataChanged = True

    def createAlphaBox(self):
        """Create Alpha QWidget."""
        self.alphaBox = QWidget()
        mainLayout = QVBoxLayout()

        box = QGroupBox(_("AlphaTL"))
        layout = QHBoxLayout()

        self.cb_trans_banner = QCheckBox(
            " " + _("Download transparent Banner of the Match"))
        self.cb_trans_banner.setChecked(
            scctool.settings.config.parser.getboolean(
                "SCT", "transparent_match_banner"))
        self.cb_trans_banner.stateChanged.connect(self.changed)

        layout.addWidget(self.cb_trans_banner)
        box.setLayout(layout)

        mainLayout.addWidget(box)

        box = QGroupBox(_("Set Ingame Score Task"))
        layout = QVBoxLayout()

        self.cb_ctrlx = QCheckBox(
            " " + _('Automatically press Ctrl+X to apply the'
                    ' correct player order ingame'))
        self.cb_ctrlx.setToolTip(
            _("This will ensure that the player of the first team is always"
              " on the left/top in the ingame Observer UI."))
        self.cb_ctrlx.setChecked(
            scctool.settings.config.parser.getboolean("SCT", "CtrlX"))
        self.cb_ctrlx.stateChanged.connect(self.changed)
        layout.addWidget(self.cb_ctrlx)

        self.cb_ctrln = QCheckBox(
            " " + _('Automatically press Ctrl+N before'
                    ' OCR to display player names'))
        self.cb_ctrln.setToolTip(
            _("This is recommended for Standard and Gawliq Observer UI."))
        self.cb_ctrln.setChecked(
            scctool.settings.config.parser.getboolean("SCT", "CtrlN"))
        self.cb_ctrln.stateChanged.connect(self.changed)
        layout.addWidget(self.cb_ctrln)

        self.cb_ctrlshifts = QCheckBox(
            " " + _('Automatically press Ctrl+Shift+S to display'
                    ' the ingame score'))
        self.cb_ctrlshifts.setToolTip(
            _("Ctrl+Shift+S is needed for the WCS-Gameheart Oberserver"
              " Overlay, but disables the sound for other overlays."))
        self.cb_ctrlshifts.setChecked(
            scctool.settings.config.parser.getboolean("SCT", "CtrlShiftS"))
        self.cb_ctrlshifts.stateChanged.connect(self.changed)
        layout.addWidget(self.cb_ctrlshifts)

        self.cb_ctrlshiftc = QCheckBox(
            " " + _('Automatically press Ctrl+Shift+C to toogle the clan tag'))
        self.cb_ctrlshiftc.setChecked(
            scctool.settings.config.parser.getboolean("SCT", "CtrlShiftC"))
        self.cb_ctrlshiftc.stateChanged.connect(self.changed)
        layout.addWidget(self.cb_ctrlshiftc)

        container = QHBoxLayout()
        self.cb_ctrlshiftr = QComboBox()
        self.cb_ctrlshiftr.addItem("0")
        self.cb_ctrlshiftr.addItem("1")
        self.cb_ctrlshiftr.addItem("2")
        try:
            self.cb_ctrlshiftr.setCurrentIndex(
                scctool.settings.config.parser.getint("SCT", "CtrlShiftR"))
        except Exception:
            self.cb_ctrlshiftr.setCurrentIndex(0)
        self.cb_ctrlshiftr.setMaximumWidth(40)
        self.cb_ctrlshiftr.currentIndexChanged.connect(self.changed)
        container.addWidget(QLabel(
            _('Automatically press Ctrl+Shift+R to toogle the race icon ')))
        container.addWidget(self.cb_ctrlshiftr)
        container.addWidget(QLabel(_(' time(s)')))
        layout.addLayout(container)

        self.cb_blacklist = QCheckBox(
            " " + _('Activate Blacklist for'
                    ' Ingame Score'))
        self.cb_blacklist.setChecked(
            scctool.settings.config.parser.getboolean("SCT", "blacklist_on"))
        self.cb_blacklist.stateChanged.connect(self.changed)
        layout.addWidget(self.cb_blacklist)

        box.setLayout(layout)

        mainLayout.addWidget(box)

        box = QGroupBox(_("Blacklist for Ingame Score"))
        layout = QVBoxLayout()

        blacklistDesc = _("Enter your SC2 client usernames to deactivate"
                          " automatically setting the ingame score and"
                          " toogling the production tab when you are playing"
                          " yourself. Replays are exempt.")
        label = QLabel(blacklistDesc)
        label.setAlignment(Qt.AlignJustify)
        label.setWordWrap(True)
        layout.addWidget(label)

        self.list_blacklist = ListTable(
            4, scctool.settings.config.getBlacklist())
        self.list_blacklist.dataModified.connect(self.changed)
        self.list_blacklist.setFixedHeight(50)
        layout.addWidget(self.list_blacklist)
        box.setLayout(layout)

        mainLayout.addWidget(box)

        mainLayout.addItem(QSpacerItem(
            0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))

        self.alphaBox.setLayout(mainLayout)

    def createFavBox(self):
        """Create favorites box."""
        self.favBox = QWidget()
        mainLayout = QVBoxLayout()

        box = QGroupBox(_("Players"))
        layout = QHBoxLayout()

        self.list_favPlayers = ListTable(
            4, scctool.settings.config.getMyPlayers())
        self.list_favPlayers.dataModified.connect(self.changed)
        self.list_favPlayers.setFixedHeight(150)
        layout.addWidget(self.list_favPlayers)
        box.setLayout(layout)

        mainLayout.addWidget(box)

        box = QGroupBox(_("Teams"))
        layout = QVBoxLayout()

        self.list_favTeams = ListTable(3, scctool.settings.config.getMyTeams())
        self.list_favTeams.dataModified.connect(self.changed)
        self.list_favTeams.setFixedHeight(100)
        layout.addWidget(self.list_favTeams)
        self.cb_swapTeams = QCheckBox(
            _('Swap my favorite team always to the left'))
        self.cb_swapTeams.setChecked(
            scctool.settings.config.parser.getboolean("SCT", "swap_myteam"))
        self.cb_swapTeams.stateChanged.connect(self.changed)
        layout.addWidget(self.cb_swapTeams)
        box.setLayout(layout)
        mainLayout.addWidget(box)

        mainLayout.addItem(QSpacerItem(
            0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))

        self.favBox.setLayout(mainLayout)

    def createAliasBox(self):
        """Create favorites box."""
        self.aliasBox = QWidget()
        mainLayout = QGridLayout()

        aliasDesc = _(
            'Player and team aliases are replaced by the actual name when'
            + ' encountered by the match grabber. Additionally, SC2 player'
            + ' names listed as aliases are replaced in the intros'
            + ' and used to identify players by the automatic'
            + ' background tasks "Auto Score Update" and "Set Ingame Score".')
        label = QLabel(aliasDesc)
        label.setAlignment(Qt.AlignJustify)
        label.setWordWrap(True)

        mainLayout.addWidget(label, 1, 0, 1, 2)

        box = QGroupBox(_("Player Aliases"))
        layout = QVBoxLayout()
        self.list_aliasPlayers = AliasTreeView(self)
        self.list_aliasPlayers.aliasRemoved.connect(
            self.controller.aliasManager.removePlayerAlias)
        layout.addWidget(self.list_aliasPlayers)
        addButton = QPushButton(_("Add Alias"))
        addButton.clicked.connect(lambda: self.addAlias(
            self.list_aliasPlayers, _('Player Name')))
        layout.addWidget(addButton)
        box.setLayout(layout)
        mainLayout.addWidget(box, 0, 0)

        box = QGroupBox(_("Team Aliases"))
        layout = QVBoxLayout()
        self.list_aliasTeams = AliasTreeView(self)
        self.list_aliasTeams.aliasRemoved.connect(
            self.controller.aliasManager.removeTeamAlias)
        layout.addWidget(self.list_aliasTeams)
        addButton = QPushButton(_("Add Alias"))
        addButton.clicked.connect(lambda: self.addAlias(
            self.list_aliasTeams, _('Team Name')))
        layout.addWidget(addButton)
        box.setLayout(layout)
        mainLayout.addWidget(box, 0, 1)

        alias_list = self.controller.aliasManager.playerAliasList()
        for player, aliases in alias_list.items():
            self.list_aliasPlayers.insertAliasList(player, aliases)

        alias_list = self.controller.aliasManager.teamAliasList()
        for team, aliases in alias_list.items():
            self.list_aliasTeams.insertAliasList(team, aliases)

        self.aliasBox.setLayout(mainLayout)

    def addAlias(self, widget, scope, name=""):
        """Add an alias."""
        name, ok = QInputDialog.getText(
            self, scope, scope + ':', text=name)
        if not ok:
            return

        name = name.strip()
        alias, ok = QInputDialog.getText(
            self, _('Alias'), _('Alias of {}').format(name) + ':', text="")

        alias = alias.strip()
        if not ok:
            return

        try:
            if widget == self.list_aliasPlayers:
                self.controller.aliasManager.addPlayerAlias(name, alias)
            elif widget == self.list_aliasTeams:
                self.controller.aliasManager.addTeamAlias(name, alias)
            widget.insertAlias(name, alias, True)
        except Exception as e:
            module_logger.exception("message")
            QMessageBox.critical(self, _("Error"), str(e))

    def createSC2ClientAPIBox(self):
        """Create form for SC2 Client API config."""
        self.clientapiBox = QWidget()

        mainLayout = QVBoxLayout()

        box = QGroupBox(
            _("SC2 Client API Address"))

        layout = QGridLayout()

        self.cb_usesc2listener = QCheckBox(
            " " + _("Listen to SC2 Client API running"
                    " on a different PC in the network."))
        self.cb_usesc2listener.setChecked(
            scctool.settings.config.parser.getboolean(
                "SCT", "sc2_network_listener_enabled"))
        self.cb_usesc2listener.stateChanged.connect(self.changed)

        self.listener_address = MonitoredLineEdit()
        self.listener_address.setAlignment(Qt.AlignCenter)
        self.listener_address.setText(
            scctool.settings.config.parser.get(
                "SCT", "sc2_network_listener_address"))
        self.listener_address.textModified.connect(self.changed)
        # self.tesseract.setAlignment(Qt.AlignCenter)
        self.listener_address.setPlaceholderText(
            "[Your SC2 PC IP]:6119")
        self.listener_address.setToolTip(
            _('IP address and port of machine running SC2.'))
        ip_port = (
            r"^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.)"
            + r"{3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]):[0-9]+$")
        self.listener_address.setValidator(QRegExpValidator(QRegExp(ip_port)))

        self.test_listener = QPushButton(
            " " + _("Test SC2 Client API Connection") + " ")
        self.test_listener.clicked.connect(self.testClientAPI)

        text = _(
            "Activate this option if you are using a two computer "
            "setup with StarCraft Casting Tool running on a different"
            " PC than your SC2 client. Open the Battle.net launcher "
            "on the latter PC, click 'Options', 'Game Settings', and "
            "under SC2, check 'Additional Command Line Arguments', and "
            "enter '-clientapi 6119'. Finally set as network"
            " address below: '[Your SC2 PC IP]:6119'."
        )

        label = QLabel(text)
        label.setAlignment(Qt.AlignJustify)
        label.setOpenExternalLinks(True)
        label.setWordWrap(True)
        label.setMargin(5)
        layout.addWidget(label, 1, 0, 1, 3)

        layout.addWidget(self.cb_usesc2listener, 0, 0, 1, 3)
        layout.addWidget(QLabel(
            _("Network Address") + ": "), 3, 0)
        layout.addWidget(self.listener_address, 3, 1)
        layout.addWidget(self.test_listener, 3, 2)

        box.setLayout(layout)
        mainLayout.addWidget(box)
        mainLayout.addItem(QSpacerItem(
            0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))
        self.clientapiBox.setLayout(mainLayout)

    def testClientAPI(self):
        """Test for connection to sc2 client api."""
        QApplication.setOverrideCursor(Qt.WaitCursor)
        address = self.listener_address.text().strip()
        url = "http://{}/ui".format(address)
        try:
            r = requests.get(url, timeout=10)
            r.raise_for_status()
            successfull = True
        except Exception:
            successfull = False
            module_logger.error("message")
        finally:
            QApplication.restoreOverrideCursor()

        title = _("Connection Test")

        if successfull:
            QMessageBox.information(
                self, title,
                _('Connection to SC2 client API established!'))
        else:
            QMessageBox.warning(
                self, title,
                _('Unable to connect to SC2 client API.'
                  ' Please make sure that SC2 is currently'
                  ' running on that machine.'))

    def createOcrBox(self):
        """Create forms for OCR."""
        self.ocrBox = QWidget()

        mainLayout = QVBoxLayout()

        box = QGroupBox(
            _("Optical Character Recognition for"
              " Automatic Setting of Ingame Score"))

        layout = QGridLayout()

        self.cb_useocr = QCheckBox(
            " " + _("Activate Optical Character Recognition"))
        self.cb_useocr.setChecked(
            scctool.settings.config.parser.getboolean("SCT", "use_ocr"))
        self.cb_useocr.stateChanged.connect(self.changed)

        self.tesseract = MonitoredLineEdit()
        self.tesseract.setText(
            scctool.settings.config.parser.get("SCT", "tesseract"))
        self.tesseract.textModified.connect(self.changed)
        # self.tesseract.setAlignment(Qt.AlignCenter)
        self.tesseract.setPlaceholderText(
            "C:\\Program Files (x86)\\Tesseract-OCR\\tesseract")
        self.tesseract.setReadOnly(True)
        self.tesseract.setToolTip(_('Tesseract-OCR Executable'))

        self.browse = QPushButton(_("Browse..."))
        self.browse.clicked.connect(self.selectTesseract)

        text = _(
            "Sometimes the order of players given by the SC2-Client-API"
            " differs from the order in the Observer-UI resulting in a"
            " swapped match score. To correct this via Optical Character"
            " Recognition you have to download {} and install and select the"
            " exectuable below, if it is not detected automatically.")
        url = 'https://github.com/UB-Mannheim/tesseract' + \
            '/wiki#tesseract-at-ub-mannheim'
        href = "<a href='{}'>" + "Tesseract-OCR" + "</a>"
        href = href.format(url)

        label = QLabel(text.format(href))
        label.setAlignment(Qt.AlignJustify)
        label.setOpenExternalLinks(True)
        label.setWordWrap(True)
        label.setMargin(5)
        layout.addWidget(label, 1, 0, 1, 2)

        layout.addWidget(self.cb_useocr, 0, 0, 1, 2)
        layout.addWidget(QLabel(
            _("Tesseract-OCR Executable") + ":"), 2, 0)
        layout.addWidget(self.tesseract, 3, 0)
        layout.addWidget(self.browse, 3, 1)

        box.setLayout(layout)
        mainLayout.addWidget(box)
        mainLayout.addItem(QSpacerItem(
            0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))
        self.ocrBox.setLayout(mainLayout)

        if(not scctool.settings.windows):
            self.cb_useocr.setEnabled(False)
            self.cb_useocr.setAttribute(Qt.WA_AlwaysShowToolTips)
            self.cb_useocr.setToolTip(
                _("This feature is only available in Windows."))
            self.tesseract.setEnabled(False)
            self.tesseract.setAttribute(Qt.WA_AlwaysShowToolTips)
            self.tesseract.setToolTip(
                _("This feature is only available in Windows."))
            self.browse.setEnabled(False)
            self.browse.setAttribute(Qt.WA_AlwaysShowToolTips)
            self.browse.setToolTip(
                _("This feature is only available in Windows."))

    def selectTesseract(self):
        """Create forms for tesseract."""
        old_exe = self.tesseract.text()
        default = scctool.settings.config.findTesserAct(old_exe)
        exe, ok = QFileDialog.getOpenFileName(
            self, _("Select Tesseract-OCR Executable"), default,
            _("Tesseract-OCR Executable") + " (tesseract.exe);; "
            + _("Executable") + " (*.exe);; " + _("All files") + " (*)")
        if(ok and exe != old_exe):
            self.tesseract.setText(exe)
            self.changed()

    def createAligulacTab(self):
        """Create the aligulac tab."""
        self.aligulacTab = QWidget()

        layout = QGridLayout()
        self.aligulacTreeview = AligulacTreeView(
            self, self.controller.aligulacManager)

        layout.addWidget(self.aligulacTreeview, 0, 0, 3, 1)

        self.pb_addAligulacID = QPushButton(_("Add Aligluac ID"))
        self.pb_addAligulacID.clicked.connect(
            lambda x, self=self: self.addAligulacID())
        layout.addWidget(self.pb_addAligulacID, 1, 1)

        self.pb_removeAligulacID = QPushButton(_("Remove Aligulac ID"))
        self.pb_removeAligulacID.clicked.connect(self.removeAligulacID)
        layout.addWidget(self.pb_removeAligulacID, 2, 1)

        layout.addItem(QSpacerItem(0, 0, QSizePolicy.Minimum,
                                   QSizePolicy.Minimum),
                       0, 1)

        self.aligulacTab.setLayout(layout)

    def addAligulacID(self, name='', aligulac_id=1):
        """Add an aligulac ID."""
        text, ok = QInputDialog.getText(
            self, _('Player Name'), _('Player Name') + ':', text=name)
        text = text.strip()
        if not ok or not text:
            return
        aligulac_id, ok = QInputDialog.getInt(
            self,
            _('Aligulac ID'), _('Aligulac ID') + ':',
            value=aligulac_id, min=1)
        if not ok:
            return

        self.aligulacTreeview.insertItem(text, aligulac_id)

    def removeAligulacID(self):
        """Remove an selected aligulac ID."""
        self.aligulacTreeview.removeSelected()

    def createMapsBox(self):
        """Create box for map manager."""
        self.mapsize = 300

        self.mapsBox = QWidget()

        layout = QGridLayout()

        self.maplist = QListWidget()
        self.maplist.setSortingEnabled(True)
        for sc2map in scctool.settings.maps:
            self.maplist.addItem(QListWidgetItem(sc2map))
        self.maplist.setCurrentItem(self.maplist.item(0))
        self.maplist.currentItemChanged.connect(self.changePreview)
        # self.maplist.setFixedHeight(self.mapsize)
        self.maplist.setMinimumWidth(150)

        layout.addWidget(self.maplist, 0, 1, 2, 1)
        self.mapPreview = QLabel()
        self.mapPreview.setFixedWidth(self.mapsize)
        self.mapPreview.setFixedHeight(self.mapsize)
        self.mapPreview.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.mapPreview, 0, 0)
        self.mapInfo = QLabel()
        self.mapInfo.setIndent(10)
        layout.addWidget(self.mapInfo, 1, 0)

        self.pb_addMapLiquipedia = QPushButton(_("Add from Liquipedia"))
        self.pb_addMapLiquipedia.clicked.connect(self.addFromLquipedia)
        self.pb_addMap = QPushButton(_("Add from File"))
        self.pb_addMap.clicked.connect(self.addMap)
        self.pb_renameMap = QPushButton(_("Rename"))
        self.pb_renameMap.clicked.connect(self.renameMap)
        self.pb_changeMap = QPushButton(_("Change Image"))
        self.pb_changeMap.clicked.connect(self.changeMap)
        self.pb_removeMap = QPushButton(_("Remove"))
        self.pb_removeMap.clicked.connect(self.deleteMap)

        self.sc_removeMap = QShortcut(QKeySequence("Del"), self.maplist)
        self.sc_removeMap.setAutoRepeat(False)
        self.sc_removeMap.setContext(Qt.WidgetWithChildrenShortcut)
        self.sc_removeMap.activated.connect(self.deleteMap)

        box = QWidget()
        container = QHBoxLayout()

        container.addWidget(self.pb_addMapLiquipedia, 0)
        container.addWidget(self.pb_addMap, 0)
        container.addWidget(QLabel(), 4)
        container.addWidget(self.pb_renameMap, 0)
        container.addWidget(self.pb_changeMap, 0)
        container.addWidget(self.pb_removeMap, 0)
        box.setLayout(container)

        layout.addWidget(box, 2, 0, 1, 2)

        layout.addItem(QSpacerItem(0, 0, QSizePolicy.Minimum,
                                   QSizePolicy.Expanding),
                       3, 0, 1, 2)

        self.changePreview()
        self.mapsBox.setLayout(layout)

    def renameMap(self):
        """Rename maps."""
        item = self.maplist.currentItem()
        mapname = item.text()
        text, ok = QInputDialog.getText(
            self, _('Map Name'),
            _('Map Name') + ':',
            text=mapname)
        if not ok:
            return
        text = text.strip()
        if(text == mapname):
            return
        if text.lower() == 'tbd':
            QMessageBox.critical(
                self,
                _("Error"),
                _('"{}" is not a valid map name.').format(text))
            return
        if(text in scctool.settings.maps):
            buttonReply = QMessageBox.warning(
                self, _("Duplicate Entry"), _(
                    "Map is already in list! Overwrite?"),
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No)
            if buttonReply == QMessageBox.No:
                return

        self.controller.addMap(self.controller.getMapImg(mapname, True), text)
        self.controller.deleteMap(mapname)
        item.setText(text)

    def changeMap(self):
        """Change a map."""
        map = self.maplist.currentItem().text()
        fileName, ok = QFileDialog.getOpenFileName(
            self, _("Select Map Image (> 500x500px recommended)"),
            "", _("Supported Images") + " (*.png *.jpg)")
        if ok:
            base = os.path.basename(fileName)
            name, ext = os.path.splitext(base)
            name = name.replace("_", " ")
            self.controller.deleteMap(map)
            self.controller.addMap(fileName, map)
            self.changePreview()

    def addMap(self):
        """Add a map."""
        fileName, ok = QFileDialog.getOpenFileName(
            self, _("Select Map Image (> 500x500px recommended)"),
            "", _("Supported Images") + " (*.png *.jpg)")
        if ok:
            base = os.path.basename(fileName)
            name, __ = os.path.splitext(base)
            name = name.replace("_", " ")
            map_name, ok = QInputDialog.getText(
                self, _('Map Name'), _('Map Name') + ':', text=name)
            map_name = map_name.strip()
            if ok:
                if map_name.lower() == 'tbd':
                    QMessageBox.critical(
                        self,
                        _("Error"),
                        _('"{}" is not a valid map name.').format(map_name))
                    return

                if(map_name in scctool.settings.maps):
                    buttonReply = QMessageBox.warning(
                        self, _("Duplicate Entry"), _(
                            "Map is already in list! Overwrite?"),
                        QMessageBox.Yes | QMessageBox.No,
                        QMessageBox.No)
                    if buttonReply == QMessageBox.No:
                        return
                    else:
                        self.controller.deleteMap(map_name)

                self.controller.addMap(fileName, map_name)
                items = self.maplist.findItems(map_name, Qt.MatchExactly)
                if len(items) == 0:
                    item = QListWidgetItem(map_name)
                    self.maplist.addItem(item)
                    self.maplist.setCurrentItem(item)
                else:
                    self.maplist.setCurrentItem(items[0])
                self.changePreview()

    def addFromLquipedia(self):
        """Add a map from Liquipedia."""
        grabber = LiquipediaGrabber()
        search_str = ''
        while True:
            search_str, ok = QInputDialog.getText(
                self, _('Map Name'), _('Map Name') + ':', text=search_str)
            search_str.strip()
            try:
                if ok and search_str:
                    if search_str.lower() == 'tbd':
                        QMessageBox.critical(
                            self,
                            _("Error"),
                            _('"{}" is not a valid map name.')
                            .format(search_str))
                        continue
                    try:
                        QApplication.setOverrideCursor(Qt.WaitCursor)
                        sc2map = grabber.get_map(search_str)
                    except MapNotFound:
                        QMessageBox.critical(
                            self,
                            _("Map not found"),
                            _('"{}" was not found on Liquipedia.')
                            .format(search_str))
                        continue
                    finally:
                        QApplication.restoreOverrideCursor()
                    map_name = sc2map.get_name()

                    if(map_name in scctool.settings.maps):
                        buttonReply = QMessageBox.warning(
                            self, _("Duplicate Entry"), _(
                                "Map {} is already in list! Overwrite?"
                                .format(map_name)),
                            QMessageBox.Yes | QMessageBox.No,
                            QMessageBox.No)
                        if buttonReply == QMessageBox.No:
                            break
                        else:
                            self.controller.deleteMap(map_name)

                    try:
                        QApplication.setOverrideCursor(Qt.WaitCursor)
                        images = grabber.get_images(map.get_map_images())
                        image = ""
                        for size in sorted(images):
                            if not image or size <= 2500 * 2500:
                                image = images[size]
                        url = grabber._base_url + image

                        downloader = MapDownloader(self, map_name, url)
                        downloader.download()
                        if map_name not in scctool.settings.maps:
                            scctool.settings.maps.append(map_name)
                        items = self.maplist.findItems(map_name,
                                                       Qt.MatchExactly)
                        if len(items) == 0:
                            item = QListWidgetItem(map_name)
                            self.maplist.addItem(item)
                            self.maplist.setCurrentItem(item)
                        else:
                            self.maplist.setCurrentItem(items[0])
                        self.changePreview()
                    except Exception:
                        raise
                    finally:
                        QApplication.restoreOverrideCursor()
            except Exception as e:
                module_logger.exception("message")
                QMessageBox.critical(self, _("Error"), str(e))
            break

    def deleteMap(self):
        """Delete a map."""
        item = self.maplist.currentItem()
        mapname = item.text()
        buttonReply = QMessageBox.question(
            self, _('Delete map?'),
            _("Delete '{}' permanently?").format(mapname),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No)
        if buttonReply == QMessageBox.Yes:
            self.controller.deleteMap(mapname)
            self.maplist.takeItem(self.maplist.currentRow())

    def changePreview(self):
        """Change the map preview."""
        if self.maplist.count() < 1:
            return

        mapname = self.maplist.currentItem().text()
        if(mapname == "TBD"):
            self.pb_renameMap.setEnabled(False)
            self.pb_removeMap.setEnabled(False)
            self.sc_removeMap.setEnabled(False)
        else:
            self.pb_removeMap.setEnabled(True)
            self.pb_renameMap.setEnabled(True)
            self.sc_removeMap.setEnabled(True)

        file = self.controller.getMapImg(mapname, True)
        pixmap = QPixmap(file)
        height = map.height()
        width = map.width()
        ext = os.path.splitext(file)[1].replace(".", "").upper()
        size = humanize.naturalsize(os.path.getsize(file))
        pixmap = QPixmap(file).scaled(
            self.mapsize, self.mapsize, Qt.KeepAspectRatio)
        self.mapPreview.setPixmap(pixmap)
        text = f"{width}x{height}px, {size}, {ext}"
        self.mapInfo.setText(text)

    def createButtonGroup(self):
        """Create buttons."""
        try:
            layout = QHBoxLayout()

            layout.addWidget(QLabel(""))

            buttonCancel = QPushButton(_('Cancel'))
            buttonCancel.clicked.connect(self.closeWindow)
            layout.addWidget(buttonCancel)

            buttonSave = QPushButton(_('&Save && Close'))
            buttonSave.setToolTip(_("Shortcut: {}").format("Ctrl+S"))
            self.shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
            self.shortcut.setAutoRepeat(False)
            self.shortcut.activated.connect(self.saveCloseWindow)
            buttonSave.clicked.connect(self.saveCloseWindow)
            layout.addWidget(buttonSave)

            self.buttonGroup = layout
        except Exception:
            module_logger.exception("message")

    def saveData(self):
        """Save the data."""
        if(self.__dataChanged):
            scctool.settings.config.parser.set(
                "SCT", "myteams", ", ".join(self.list_favTeams.getData()))
            scctool.settings.config.parser.set(
                "SCT", "commonplayers",
                ", ".join(self.list_favPlayers.getData()))
            scctool.settings.config.parser.set(
                "SCT", "tesseract", self.tesseract.text().strip())
            scctool.settings.config.parser.set(
                "SCT", "use_ocr", str(self.cb_useocr.isChecked()))
            scctool.settings.config.parser.set(
                "SCT", "transparent_match_banner",
                str(self.cb_trans_banner.isChecked()))
            scctool.settings.config.parser.set(
                "SCT", "CtrlShiftS", str(self.cb_ctrlshifts.isChecked()))
            scctool.settings.config.parser.set(
                "SCT", "CtrlShiftC", str(self.cb_ctrlshiftc.isChecked()))
            scctool.settings.config.parser.set(
                "SCT", "swap_myteam", str(self.cb_swapTeams.isChecked()))
            scctool.settings.config.parser.set(
                "SCT", "CtrlN", str(self.cb_ctrln.isChecked()))
            scctool.settings.config.parser.set(
                "SCT", "CtrlX", str(self.cb_ctrlx.isChecked()))
            scctool.settings.config.parser.set(
                "SCT", "CtrlShiftR", str(self.cb_ctrlshiftr.currentText()))
            scctool.settings.config.parser.set(
                "SCT", "blacklist_on", str(self.cb_blacklist.isChecked()))
            scctool.settings.config.parser.set(
                "SCT", "blacklist", ", ".join(self.list_blacklist.getData()))
            scctool.settings.config.parser.set(
                "SCT", "sc2_network_listener_address",
                self.listener_address.text().strip())
            scctool.settings.config.parser.set(
                "SCT", "sc2_network_listener_enabled",
                str(self.cb_usesc2listener.isChecked()))
            self.controller.refreshButtonStatus()
            # self.controller.setCBS()
            self.__dataChanged = False

    def saveCloseWindow(self):
        """Save and close window."""
        self.saveData()
        self.passEvent = True
        self.close()

    def closeWindow(self):
        """Close window."""
        self.passEvent = True
        self.close()

    def closeEvent(self, event):
        """Handle close event."""
        try:
            self.mainWindow.updateAllMapCompleters()
            if(not self.__dataChanged):
                event.accept()
                return
            if(not self.passEvent):
                if(self.isMinimized()):
                    self.showNormal()
                buttonReply = QMessageBox.question(
                    self, _('Save data?'), _("Save data?"),
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No)
                if buttonReply == QMessageBox.Yes:
                    self.saveData()
            event.accept()
        except Exception:
            module_logger.exception("message")
