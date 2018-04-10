"""Show subwindow with miscellaneous settings."""
import logging
import os.path

import humanize  # pip install humanize
from PyQt5.QtCore import QPoint, QSize, Qt
from PyQt5.QtGui import QIcon, QKeySequence, QPixmap
from PyQt5.QtWidgets import (QCheckBox, QComboBox, QFileDialog, QGridLayout,
                             QGroupBox, QHBoxLayout, QInputDialog, QLabel,
                             QListWidget, QListWidgetItem, QMessageBox,
                             QPushButton, QShortcut, QSizePolicy, QSpacerItem,
                             QTabWidget, QVBoxLayout, QWidget)

import scctool.settings
from scctool.tasks.liquipedia import LiquipediaGrabber, MapNotFound
from scctool.view.widgets import (AliasTreeView, ListTable, MapDownloader,
                                  MonitoredLineEdit)

# create logger
module_logger = logging.getLogger('scctool.view.subMisc')


class SubwindowMisc(QWidget):
    """Show subwindow with miscellaneous settings."""

    def createWindow(self, mainWindow):
        """Create subwindow with miscellaneous settings."""
        try:
            parent = None
            super().__init__(parent)
            # self.setWindowFlags(Qt.WindowStaysOnTopHint)

            self.setWindowIcon(
                QIcon(scctool.settings.getAbsPath('src/settings.png')))
            self.setWindowModality(Qt.ApplicationModal)
            self.mainWindow = mainWindow
            self.passEvent = False
            self.controller = mainWindow.controller
            self.__dataChanged = False

            self.createButtonGroup()
            self.createTabs()

            mainLayout = QVBoxLayout()

            mainLayout.addWidget(self.tabs)
            mainLayout.addLayout(self.buttonGroup)

            self.setLayout(mainLayout)

            self.resize(QSize(mainWindow.size().width()
                              * .80, self.sizeHint().height()))
            relativeChange = QPoint(mainWindow.size().width() / 2,
                                    mainWindow.size().height() / 3)\
                - QPoint(self.size().width() / 2,
                         self.size().height() / 3)
            self.move(mainWindow.pos() + relativeChange)

            self.setWindowTitle(_("Miscellaneous Settings"))

        except Exception as e:
            module_logger.exception("message")

    def createTabs(self):
        """Create tabs."""
        self.tabs = QTabWidget()

        self.createMapsBox()
        self.createFavBox()
        self.createAliasBox()
        self.createOcrBox()
        self.createAlphaBox()

        # Add tabs
        self.tabs.addTab(self.mapsBox, _("Map Manager"))
        self.tabs.addTab(self.favBox, _("Favorites"))
        self.tabs.addTab(self.aliasBox, _("Alias"))
        self.tabs.addTab(self.ocrBox, _("OCR"))
        self.tabs.addTab(self.alphaBox, _("AlphaTL && Ingame Score"))

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
            scctool.settings.config.parser.getboolean("SCT", "transparent_match_banner"))
        self.cb_trans_banner.stateChanged.connect(self.changed)

        layout.addWidget(self.cb_trans_banner)
        box.setLayout(layout)

        mainLayout.addWidget(box)

        box = QGroupBox(_("Set Ingame Score Task"))
        layout = QVBoxLayout()

        self.cb_ctrlx = QCheckBox(
            " " + _('Automatically press Ctrl+X to apply the correct player order ingame.'))
        self.cb_ctrlx.setToolTip(
            _("This will ensure that the player of the first team is always"
              " on the left/top in the ingame Observer UI."))
        self.cb_ctrlx.setChecked(
            scctool.settings.config.parser.getboolean("SCT", "CtrlX"))
        self.cb_ctrlx.stateChanged.connect(self.changed)
        layout.addWidget(self.cb_ctrlx)

        self.cb_ctrln = QCheckBox(
            " " + _('Automatically press Ctrl+N before OCR to display player names.'))
        self.cb_ctrln.setToolTip(
            _("This is recommended for Standard and Gawliq Observer UI."))
        self.cb_ctrln.setChecked(
            scctool.settings.config.parser.getboolean("SCT", "CtrlN"))
        self.cb_ctrln.stateChanged.connect(self.changed)
        layout.addWidget(self.cb_ctrln)

        self.cb_ctrlshifts = QCheckBox(
            " " + _('Automatically press Ctrl+Shift+S to display the ingame score'))
        self.cb_ctrlshifts.setToolTip(
            _("Ctrl+Shift+S is needed for the WCS-Gameheart Oberserver Overlay," +
              " but disables the sound for other overlays."))
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
        layout = QHBoxLayout()

        self.list_favTeams = ListTable(3, scctool.settings.config.getMyTeams())
        self.list_favTeams.dataModified.connect(self.changed)
        self.list_favTeams.setFixedHeight(100)
        layout.addWidget(self.list_favTeams)

        box.setLayout(layout)
        mainLayout.addWidget(box)

        mainLayout.addItem(QSpacerItem(
            0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))

        self.favBox.setLayout(mainLayout)

    def createAliasBox(self):
        """Create favorites box."""
        self.aliasBox = QWidget()
        mainLayout = QGridLayout()

        aliasDesc = _('Player and team aliases are replaced by the actual name when' +
                      ' encountered by the match grabber. Additionally, SC2 player' +
                      ' names listed as aliases are replaced in the intros by the actual' +
                      ' name and used to identify players by the automatic' +
                      ' background tasks "Score Update" and "Set Ingame Score".')
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

        list = self.controller.aliasManager.playerAliasList()
        for player, aliases in list.items():
            self.list_aliasPlayers.insertAliasList(player, aliases)

        list = self.controller.aliasManager.teamAliasList()
        for team, aliases in list.items():
            self.list_aliasTeams.insertAliasList(team, aliases)

        self.aliasBox.setLayout(mainLayout)

    def addAlias(self, widget, scope, name=""):

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

    def createOcrBox(self):
        """Create forms for OCR."""
        self.ocrBox = QWidget()

        mainLayout = QVBoxLayout()

        box = QGroupBox(
            _("Optical Character Recognition for Automatic Setting of Ingame Score"))

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

        text = _("Sometimes the order of players given by the SC2-Client-API differs" +
                 " from the order in the Observer-UI resulting in a swapped match score." +
                 " To correct this via Optical Character Recognition you have to download" +
                 " {} and install and select the exectuable below, if it is not detected" +
                 " automatically.")
        url = 'https://github.com/UB-Mannheim/tesseract/wiki#tesseract-at-ub-mannheim'
        url = "<a href='{}'>" + "Tesseract-OCR" + "</a>"
        url = url.format(url)

        label = QLabel(text.format(url))
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
            _("Tesseract-OCR Executable") + " (tesseract.exe);; " +
            _("Executable") + " (*.exe);; " + _("All files") + " (*)")
        if(ok and exe != old_exe):
            self.tesseract.setText(exe)
            self.changed()

    def createMapsBox(self):
        """Create box for map manager."""
        self.mapsize = 300

        self.mapsBox = QWidget()

        layout = QGridLayout()

        self.maplist = QListWidget()
        self.maplist.setSortingEnabled(True)
        for map in scctool.settings.maps:
            self.maplist.addItem(QListWidgetItem(map))
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
        map = item.text()
        text, ok = QInputDialog.getText(
            self, _('Map Name'), _('Map Name') + ':', text=map)
        if not ok:
            return
        text = text.strip()
        if(text == map):
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

        self.controller.addMap(self.controller.getMapImg(map, True), text)
        self.controller.deleteMap(map)
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
            name, ext = os.path.splitext(base)
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
                            _('"{}" is not a valid map name.').format(search_str))
                        continue
                    try:
                        map = grabber.get_map(search_str)
                    except MapNotFound:
                        QMessageBox.critical(
                            self,
                            _("Map not found"),
                            _('"{}" was not found on Liquipedia.').format(search_str))
                        continue
                    map_name = map.get_name()

                    if(map_name in scctool.settings.maps):
                        buttonReply = QMessageBox.warning(
                            self, _("Duplicate Entry"), _(
                                "Map {} is already in list! Overwrite?".format(map_name)),
                            QMessageBox.Yes | QMessageBox.No,
                            QMessageBox.No)
                        if buttonReply == QMessageBox.No:
                            break
                        else:
                            self.controller.deleteMap(map_name)

                    images = grabber.get_images(map.get_map_images())
                    image = ""
                    for size in sorted(images):
                        if not image or size <= 2000 * 2000:
                            image = images[size]
                    url = grabber._base_url + image

                    downloader = MapDownloader(self, map_name, url)
                    downloader.download()
                    if map_name not in scctool.settings.maps:
                        scctool.settings.maps.append(map_name)
                    items = self.maplist.findItems(map_name, Qt.MatchExactly)
                    if len(items) == 0:
                        item = QListWidgetItem(map_name)
                        self.maplist.addItem(item)
                        self.maplist.setCurrentItem(item)
                    else:
                        self.maplist.setCurrentItem(items[0])
                    self.changePreview()
            except Exception as e:
                module_logger.exception("message")
                QMessageBox.critical(self, _("Error"), str(e))
            finally:
                break

    def deleteMap(self):
        """Delete a map."""
        item = self.maplist.currentItem()
        map = item.text()
        buttonReply = QMessageBox.question(
            self, _('Delete map?'),
            _("Delete '{}' permanently?").format(map),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No)
        if buttonReply == QMessageBox.Yes:
            self.controller.deleteMap(map)
            self.maplist.takeItem(self.maplist.currentRow())

    def changePreview(self):
        """Change the map preview."""
        if self.maplist.count() < 1:
            return

        map = self.maplist.currentItem().text()
        if(map == "TBD"):
            self.pb_renameMap.setEnabled(False)
            self.pb_removeMap.setEnabled(False)
        else:
            self.pb_removeMap.setEnabled(True)
            self.pb_renameMap.setEnabled(True)

        file = self.controller.getMapImg(map, True)
        map = QPixmap(file)
        width = map.height()
        height = map.width()
        ext = os.path.splitext(file)[1].replace(".", "").upper()
        size = humanize.naturalsize(os.path.getsize(file))
        map = QPixmap(file).scaled(
            self.mapsize, self.mapsize, Qt.KeepAspectRatio)
        self.mapPreview.setPixmap(map)
        text = "{}x{}px, {}, {}".format(width, height, str(size), ext)
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
        except Exception as e:
            module_logger.exception("message")

    def saveData(self):
        """Save the data."""
        if(self.__dataChanged):
            scctool.settings.config.parser.set(
                "SCT", "myteams", ", ".join(self.list_favTeams.getData()))
            scctool.settings.config.parser.set(
                "SCT", "commonplayers", ", ".join(self.list_favPlayers.getData()))
            scctool.settings.config.parser.set(
                "SCT", "tesseract", self.tesseract.text().strip())
            scctool.settings.config.parser.set(
                "SCT", "use_ocr", str(self.cb_useocr.isChecked()))
            scctool.settings.config.parser.set(
                "SCT", "transparent_match_banner", str(self.cb_trans_banner.isChecked()))
            scctool.settings.config.parser.set(
                "SCT", "CtrlShiftS", str(self.cb_ctrlshifts.isChecked()))
            scctool.settings.config.parser.set(
                "SCT", "CtrlShiftC", str(self.cb_ctrlshiftc.isChecked()))
            scctool.settings.config.parser.set(
                "SCT", "CtrlN", str(self.cb_ctrln.isChecked()))
            scctool.settings.config.parser.set(
                "SCT", "CtrlX", str(self.cb_ctrlx.isChecked()))
            scctool.settings.config.parser.set(
                "SCT", "CtrlShiftR", str(self.cb_ctrlshiftr.currentText()))

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
            self.mainWindow.updateMapCompleters()
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
        except Exception as e:
            module_logger.exception("message")
