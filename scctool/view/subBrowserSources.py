"""Show connections settings sub window."""
import logging

import keyboard
from PyQt5.QtCore import QPoint, QSize, Qt
from PyQt5.QtGui import QIcon, QKeySequence
from PyQt5.QtWidgets import (QComboBox, QDoubleSpinBox, QFormLayout,
                             QGridLayout, QGroupBox, QHBoxLayout, QInputDialog,
                             QLabel, QListWidget, QListWidgetItem, QMessageBox,
                             QPushButton, QShortcut, QSizePolicy, QSlider,
                             QSpacerItem, QTabWidget, QVBoxLayout, QWidget)

import scctool.settings
from scctool.view.widgets import HotkeyLayout

# create logger
module_logger = logging.getLogger('scctool.view.subConnections')


class SubwindowBrowserSources(QWidget):
    """Show connections settings sub window."""

    def createWindow(self, mainWindow):
        """Create window."""
        try:
            parent = None
            super().__init__(parent)
            # self.setWindowFlags(Qt.WindowStaysOnTopHint)

            self.setWindowIcon(
                QIcon(scctool.settings.getResFile('browser.png')))
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

            self.resize(QSize(mainWindow.size().width() * 0.8,
                              self.sizeHint().height()))
            relativeChange = QPoint(mainWindow.size().width() / 2,
                                    mainWindow.size().height() / 3) -\
                QPoint(self.size().width() / 2,
                       self.size().height() / 3)
            self.move(mainWindow.pos() + relativeChange)

            self.setWindowTitle(_("Browser Sources"))

        except Exception as e:
            module_logger.exception("message")

    def createTabs(self):
        """Create tabs."""
        self.tabs = QTabWidget()

        self.createFormGroupWebsocket()
        self.createFormGroupMapstats()
        self.createFormGroupMapBox()
        self.createFormGroupMapLandscape()

        # Add tabs
        self.tabs.addTab(self.formGroupWebsocket, _("Intros"))
        self.tabs.addTab(self.formGroupMapstats, _("Mapstats"))

        self.tabs.addTab(self.formGroupMapBox, _("Box Map Icons"))
        self.tabs.addTab(self.formGroupMapLandscape, _("Landscape Map Icons"))

    def addHotkey(self, ident, label):
        element = HotkeyLayout(
            self, label,
            scctool.settings.config.parser.get("Intros", ident))
        self.hotkeys[ident] = element
        return element

    def connectHotkeys(self):
        for ident, key in self.hotkeys.items():
            for ident2, key2 in self.hotkeys.items():
                if ident == ident2:
                    continue
                key.modified.connect(key2.check_dublicate)
            key.modified.connect(self.changed)

    def createFormGroupMapstats(self):
        self.formGroupMapstats = QWidget()
        mainLayout = QVBoxLayout()

        box = QGroupBox(_("Map Pool to be displayed"))
        layout = QVBoxLayout()
        self.cb_mappool = QComboBox()
        self.cb_mappool.addItem(_("Current Ladder Map Pool"))
        self.cb_mappool.addItem(_("Custom Map Pool (defined below)"))
        self.cb_mappool.addItem(_("Currently entered Maps only"))
        self.cb_mappool.setCurrentIndex(
            self.controller.mapstatsManager.getMapPoolType())
        self.cb_mappool.currentIndexChanged.connect(self.changed)
        layout.addWidget(self.cb_mappool)
        box.setLayout(layout)

        mainLayout.addWidget(box)

        box = QGroupBox(_("Custom Map Pool"))
        layout = QGridLayout()
        self.maplist = QListWidget()
        self.maplist.setSortingEnabled(True)

        ls = list(self.controller.mapstatsManager.getCustomMapPool())
        self.maplist.addItems(ls)
        self.maplist.setCurrentItem(self.maplist.item(0))

        layout.addWidget(self.maplist, 0, 0, 3, 1)

        qb_add = QPushButton()
        pixmap = QIcon(
            scctool.settings.getResFile('add.png'))
        qb_add.setIcon(pixmap)
        qb_add.clicked.connect(self.addMap)
        layout.addWidget(qb_add, 0, 1)

        qb_remove = QPushButton()
        pixmap = QIcon(
            scctool.settings.getResFile('delete.png'))
        qb_remove.clicked.connect(self.removeMap)
        qb_remove.setIcon(pixmap)
        layout.addWidget(qb_remove, 1, 1)

        self.sc_removeMap = QShortcut(QKeySequence("Del"), self)
        self.sc_removeMap.setAutoRepeat(False)
        self.sc_removeMap.activated.connect(self.removeMap)

        box.setLayout(layout)
        mainLayout.addWidget(box)

        mainLayout.addItem(QSpacerItem(
            0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))
        self.formGroupMapstats.setLayout(mainLayout)

    def addMap(self):
        maplist = list(scctool.settings.maps)
        maplist.remove('TBD')
        for i in range(self.maplist.count()):
            map = str(self.maplist.item(i).text())
            if map in maplist:
                maplist.remove(map)

        if len(maplist) > 0:
            map, ok = QInputDialog.getItem(
                self, _('Add Map'),
                _('Please select a map') + ':',
                maplist, editable=False)

            if ok:
                self.__dataChanged = True
                item = QListWidgetItem(map)
                self.maplist.addItem(item)
                self.maplist.setCurrentItem(item)
        else:
            QMessageBox.information(self, _(
                "No maps available"), _('All available maps have already been added.'))

    def removeMap(self):
        item = self.maplist.currentItem()
        if item:
            self.maplist.takeItem(self.maplist.currentRow())
            self.__dataChanged = True

    def createFormGroupMapBox(self):
        self.formGroupMapBox = QWidget()
        mainLayout = QVBoxLayout()
        mainLayout.addItem(QSpacerItem(
            0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))
        self.formGroupMapBox.setLayout(mainLayout)

    def createFormGroupMapLandscape(self):
        self.formGroupMapLandscape = QWidget()
        mainLayout = QVBoxLayout()
        mainLayout.addItem(QSpacerItem(
            0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))
        self.formGroupMapLandscape.setLayout(mainLayout)

    def createFormGroupWebsocket(self):
        """Create forms for OBS websocket connection."""
        self.formGroupWebsocket = QWidget()
        mainLayout = QVBoxLayout()

        self.hotkeyBox = QGroupBox(_("Intro Hotkeys"))
        layout = QVBoxLayout()

        try:
            keyboard.unhook_all()
        except AttributeError:
            pass
        self.hotkeys = dict()
        layout.addLayout(self.addHotkey("hotkey_player1", _("Player 1")))
        layout.addLayout(self.addHotkey("hotkey_player2", _("Player 2")))
        layout.addLayout(self.addHotkey("hotkey_debug", _("Debug")))
        self.connectHotkeys()
        self.hotkeyBox.setLayout(layout)
        mainLayout.addWidget(self.hotkeyBox)

        self.introBox = QGroupBox(_("Intro Settings"))
        layout = QFormLayout()
        self.sl_sound = QSlider(Qt.Horizontal)
        self.sl_sound.setMinimum(0)
        self.sl_sound.setMaximum(10)
        self.sl_sound.setValue(
            scctool.settings.config.parser.getint("Intros", "sound_volume"))
        self.sl_sound.setTickPosition(QSlider.TicksBothSides)
        self.sl_sound.setTickInterval(1)
        self.sl_sound.valueChanged.connect(self.changed)
        layout.addRow(QLabel(
            _("Sound Volume:") + " "), self.sl_sound)
        self.sb_displaytime = QDoubleSpinBox()
        self.sb_displaytime.setRange(0, 10)
        self.sb_displaytime.setDecimals(1)
        self.sb_displaytime.setValue(
            scctool.settings.config.parser.getfloat("Intros", "display_time"))
        self.sb_displaytime.setSuffix(" " + _("Seconds"))
        self.sb_displaytime.valueChanged.connect(self.changed)
        layout.addRow(QLabel(
            _("Display Duration:") + " "), self.sb_displaytime)
        self.cb_animation = QComboBox()
        animation = scctool.settings.config.parser.get("Intros", "animation")
        currentIdx = 0
        idx = 0
        for item in ["Fly-In", "Slide", "Fanfare"]:
            self.cb_animation.addItem(item)
            if(item == animation):
                currentIdx = idx
            idx += 1
        self.cb_animation.setCurrentIndex(currentIdx)
        layout.addRow(QLabel(
            _("Animation:") + " "), self.cb_animation)
        self.introBox.setLayout(layout)
        mainLayout.addWidget(self.introBox)

        mainLayout.addItem(QSpacerItem(
            0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))
        self.formGroupWebsocket.setLayout(mainLayout)

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

    def changed(self, *values):
        """Handle changed data."""
        self.__dataChanged = True

    def saveData(self):
        """Save the data to config."""

        self.saveWebsocketdata()

        maps = list()
        for i in range(self.maplist.count()):
            maps.append(str(self.maplist.item(i).text()).strip())

        self.controller.mapstatsManager.setCustomMapPool(maps)
        self.controller.mapstatsManager.setMapPoolType(
            self.cb_mappool.currentIndex())
            
        self.controller.mapstatsManager.sendMapPool()
        self.controller.updateMapButtons()

        # self.controller.refreshButtonStatus()

    def saveWebsocketdata(self):
        """Save Websocket data."""
        for ident, key in self.hotkeys.items():
            string = scctool.settings.config.dumpHotkey(key.getKey())
            scctool.settings.config.parser.set("Intros", ident, string)
        scctool.settings.config.parser.set(
            "Intros", "display_time", str(self.sb_displaytime.value()))
        scctool.settings.config.parser.set(
            "Intros", "sound_volume", str(self.sl_sound.value()))
        scctool.settings.config.parser.set(
            "Intros", "animation", self.cb_animation.currentText().strip())

    def saveCloseWindow(self):
        """Save and close window."""
        self.saveData()
        self.closeWindow()

    def closeWindow(self):
        """Close window without save."""
        self.passEvent = True
        self.close()

    def closeEvent(self, event):
        """Handle close event."""
        try:
            if(not self.__dataChanged):
                self.controller.updateHotkeys()
                event.accept()
                return
            if(not self.passEvent):
                if(self.isMinimized()):
                    self.showNormal()
                buttonReply = QMessageBox.question(
                    self, _('Save data?'), _("Do you want to save the data?"),
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No)
                if buttonReply == QMessageBox.Yes:
                    self.saveData()
            self.controller.updateHotkeys()
            event.accept()
        except Exception as e:
            module_logger.exception("message")
