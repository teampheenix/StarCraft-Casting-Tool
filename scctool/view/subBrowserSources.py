import logging

from PyQt5.QtCore import QPoint, QSize, Qt
from PyQt5.QtGui import QIcon, QKeySequence
from PyQt5.QtWidgets import (QCheckBox, QComboBox, QDoubleSpinBox, QFormLayout,
                             QGridLayout, QGroupBox, QHBoxLayout, QInputDialog,
                             QLabel, QListWidget, QListWidgetItem, QMessageBox,
                             QPushButton, QShortcut, QSizePolicy, QSlider,
                             QSpacerItem, QTabWidget, QVBoxLayout, QWidget)

import scctool.settings
import scctool.settings.translation
from scctool.view.widgets import HotkeyLayout, ScopeGroupBox, StyleComboBox

"""Show connections settings sub window."""


# create logger
module_logger = logging.getLogger(__name__)

_ = scctool.settings.translation.gettext


class SubwindowBrowserSources(QWidget):
    """Show connections settings sub window."""
    current_tab = -1

    def createWindow(self, mainWindow, tab=''):
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
            self.createTabs(tab)

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

    def createTabs(self, tab):
        """Create tabs."""
        self.tabs = QTabWidget()

        self.createFormGroupIntro()
        self.createFormGroupMapstats()
        self.createFormGroupMapBox()
        self.createFormGroupMapLandscape()

        # Add tabs
        self.tabs.addTab(self.formGroupIntro, _("Intros"))
        self.tabs.addTab(self.formGroupMapstats, _("Mapstats"))

        self.tabs.addTab(self.formGroupMapBox, _("Box Map Icons"))
        self.tabs.addTab(self.formGroupMapLandscape, _("Landscape Map Icons"))

        table = dict()
        table['intro'] = 0
        table['mapstats'] = 1
        table['mapicons_box'] = 2
        table['mapicons_landscape'] = 3
        self.tabs.setCurrentIndex(
            table.get(tab, SubwindowBrowserSources.current_tab))
        self.tabs.currentChanged.connect(self.tabChanged)

    def tabChanged(self, idx):
        SubwindowBrowserSources.current_tab = idx

    def addHotkey(self, ident, label):
        element = HotkeyLayout(
            self, ident, label,
            scctool.settings.config.parser.get("Intros", ident))
        self.hotkeys[ident] = element
        return element

    def connectHotkeys(self):
        for ident, key in self.hotkeys.items():
            if ident == 'hotkey_debug':
                for ident2, key2 in self.hotkeys.items():
                    if ident == ident2:
                        continue
                    key.modified.connect(key2.check_dublicate)
            key.modified.connect(self.hotkeyChanged)

    def hotkeyChanged(self, key, ident):
        self.changed()

        if(ident == 'hotkey_player1' and self.cb_single_hotkey.isChecked()):
            self.hotkeys['hotkey_player2'].setData(
                self.hotkeys['hotkey_player1'].getKey())

        if not key:
            return

        if((ident == 'hotkey_player1'
            and key == self.hotkeys['hotkey_player2'].getKey()['name'])
           or (ident == 'hotkey_player2'
                and key == self.hotkeys['hotkey_player1'].getKey()['name'])):
            self.cb_single_hotkey.setChecked(True)

        if(ident in ['hotkey_player1', 'hotkey_player2']
           and key == self.hotkeys['hotkey_debug'].getKey()['name']):
            self.hotkeys['hotkey_debug'].clear()

    def singleHotkeyChanged(self):
        checked = self.cb_single_hotkey.isChecked()
        self.hotkeys['hotkey_player2'].setDisabled(checked)
        if checked:
            self.hotkeys['hotkey_player2'].setData(
                self.hotkeys['hotkey_player1'].getKey())
        elif(self.hotkeys['hotkey_player1'].getKey()
             == self.hotkeys['hotkey_player2'].getKey()):
            self.hotkeys['hotkey_player2'].clear()

    def createFormGroupMapstats(self):
        self.formGroupMapstats = QWidget()
        mainLayout = QVBoxLayout()

        box = QGroupBox(_("General"))
        layout = QFormLayout()

        container = QHBoxLayout()
        self.qb_boxStyle = StyleComboBox(
            scctool.settings.casting_html_dir + "/src/css/mapstats",
            "mapstats")
        self.qb_boxStyle.connect2WS(self.controller, 'mapstats')
        label = QLabel(_("Style:"))
        label.setMinimumWidth(120)
        button = QPushButton(_("Show in Browser"))
        button.clicked.connect(lambda: self.openHTML(
            scctool.settings.casting_html_dir + "/mapstats.html"))
        container.addWidget(self.qb_boxStyle, 2)
        container.addWidget(button, 1)
        layout.addRow(label, container)

        self.cb_mappool = QComboBox()
        self.cb_mappool.addItem(_("Current Ladder Map Pool"))
        self.cb_mappool.addItem(_("Custom Map Pool (defined below)"))
        self.cb_mappool.addItem(_("Currently entered Maps only"))
        self.cb_mappool.setCurrentIndex(
            self.controller.mapstatsManager.getMapPoolType())
        self.cb_mappool.currentIndexChanged.connect(self.changed)
        layout.addRow(QLabel(_("Map Pool:")), self.cb_mappool)

        self.cb_autoset_map = QCheckBox(_("Select the next map automatically"))
        self.cb_autoset_map.setChecked(
            scctool.settings.config.parser.getboolean(
                "Mapstats", "autoset_next_map"))
        self.cb_autoset_map.stateChanged.connect(self.changed)
        label = QLabel(_("Next Map:"))
        label.setMinimumWidth(120)
        layout.addRow(label, self.cb_autoset_map)

        self.cb_mark_played = QCheckBox(_("Mark already played maps"))
        self.cb_mark_played.setChecked(
            scctool.settings.config.parser.getboolean(
                "Mapstats", "mark_played"))
        self.cb_mark_played.stateChanged.connect(self.changed)
        label = QLabel(_("Mark:"))
        label.setMinimumWidth(120)
        layout.addRow(label, self.cb_mark_played)

        self.cb_mark_vetoed = QCheckBox(_("Mark vetoed maps"))
        self.cb_mark_vetoed.setChecked(
            scctool.settings.config.parser.getboolean(
                "Mapstats", "mark_vetoed"))
        self.cb_mark_vetoed.stateChanged.connect(self.changed)
        label = QLabel(" ")
        label.setMinimumWidth(120)
        layout.addRow(label, self.cb_mark_vetoed)

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
            QMessageBox.information(
                self,
                _("No maps available"),
                _('All available maps have already been added.'))

    def removeMap(self):
        item = self.maplist.currentItem()
        if item:
            self.maplist.takeItem(self.maplist.currentRow())
            self.__dataChanged = True

    def createFormGroupMapBox(self):
        self.formGroupMapBox = QWidget()
        mainLayout = QVBoxLayout()
        box = QGroupBox(_("General"))
        layout = QFormLayout()

        container = QHBoxLayout()
        self.qb_boxStyle = StyleComboBox(
            scctool.settings.casting_html_dir + "/src/css/mapicons_box",
            "mapicons_box")
        self.qb_boxStyle.connect2WS(self.controller, 'mapicons_box')
        label = QLabel(_("Style:"))
        label.setMinimumWidth(120)
        button = QPushButton(_("Show in Browser"))
        button.clicked.connect(lambda: self.openHTML(
            scctool.settings.casting_html_dir + "/mapicons_box_1.html"))
        container.addWidget(self.qb_boxStyle, 2)
        container.addWidget(button, 1)
        layout.addRow(label, container)

        self.sb_padding_box = QDoubleSpinBox()
        self.sb_padding_box.setRange(0, 50)
        self.sb_padding_box.setDecimals(1)
        self.sb_padding_box.setValue(
            scctool.settings.config.parser.getfloat("MapIcons", "padding_box"))
        self.sb_padding_box.setSuffix(" " + _("Pixel"))
        self.sb_padding_box.valueChanged.connect(
            lambda x: self.changePadding('box', x))
        layout.addRow(QLabel(
            _("Icon Padding:") + " "), self.sb_padding_box)
        box.setLayout(layout)
        mainLayout.addWidget(box)

        options = self.controller.matchControl.scopes
        self.scope_box = dict()
        for idx in range(0, 3):
            self.scope_box[idx] = ScopeGroupBox(
                _("Icon Set {} Scope".format(idx + 1)),
                options,
                scctool.settings.config.parser.get(
                    "MapIcons", "scope_box_{}".format(idx + 1)),
                self)
            self.scope_box[idx].dataModified.connect(self.changed)
            mainLayout.addWidget(self.scope_box[idx])

        mainLayout.addItem(QSpacerItem(
            0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))
        self.formGroupMapBox.setLayout(mainLayout)

    def createFormGroupMapLandscape(self):
        self.formGroupMapLandscape = QWidget()
        mainLayout = QVBoxLayout()
        box = QGroupBox(_("General"))
        layout = QFormLayout()

        container = QHBoxLayout()
        self.qb_boxStyle = StyleComboBox(
            scctool.settings.casting_html_dir + "/src/css/mapicons_landscape",
            "mapicons_landscape")
        self.qb_boxStyle.connect2WS(self.controller, 'mapicons_landscape')
        label = QLabel(_("Style:"))
        label.setMinimumWidth(120)
        button = QPushButton(_("Show in Browser"))
        button.clicked.connect(lambda: self.openHTML(
            scctool.settings.casting_html_dir + "/mapicons_landscape_1.html"))
        container.addWidget(self.qb_boxStyle, 2)
        container.addWidget(button, 1)
        layout.addRow(label, container)

        self.sb_padding_landscape = QDoubleSpinBox()
        self.sb_padding_landscape.setRange(0, 50)
        self.sb_padding_landscape.setDecimals(1)
        self.sb_padding_landscape.setValue(
            scctool.settings.config.parser.getfloat(
                "MapIcons", "padding_landscape"))
        self.sb_padding_landscape.setSuffix(" " + _("Pixel"))
        self.sb_padding_landscape.valueChanged.connect(
            lambda x: self.changePadding('landscape', x))
        layout.addRow(QLabel(
            _("Icon Padding:") + " "), self.sb_padding_landscape)
        box.setLayout(layout)
        mainLayout.addWidget(box)

        options = self.controller.matchControl.scopes
        self.scope_landscape = dict()
        for idx in range(0, 3):
            self.scope_landscape[idx] = ScopeGroupBox(
                _("Icon Set {} Scope".format(idx + 1)),
                options,
                scctool.settings.config.parser.get(
                    "MapIcons", "scope_landscape_{}".format(idx + 1)),
                self)
            self.scope_landscape[idx].dataModified.connect(self.changed)
            mainLayout.addWidget(self.scope_landscape[idx])

        mainLayout.addItem(QSpacerItem(
            0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))
        self.formGroupMapLandscape.setLayout(mainLayout)

    def createFormGroupIntro(self):
        """Create forms for websocket connection to intro."""
        self.formGroupIntro = QWidget()
        mainLayout = QVBoxLayout()

        box = QGroupBox(_("Style"))
        layout = QHBoxLayout()
        styleqb = StyleComboBox(
            scctool.settings.casting_html_dir + "/src/css/intro",
            "intro")
        styleqb.connect2WS(self.controller, 'intro')
        button = QPushButton(_("Show in Browser"))
        button.clicked.connect(lambda: self.openHTML(
            scctool.settings.casting_html_dir + "/intro.html"))
        layout.addWidget(styleqb, 2)
        layout.addWidget(button, 1)
        box.setLayout(layout)
        mainLayout.addWidget(box)

        self.hotkeyBox = QGroupBox(_("Hotkeys"))
        layout = QVBoxLayout()
        self.controller.websocketThread.unregister_hotkeys(force=True)

        self.cb_single_hotkey = QCheckBox(
            _("Use a single hotkey for both players"))
        self.cb_single_hotkey.stateChanged.connect(self.singleHotkeyChanged)
        layout.addWidget(self.cb_single_hotkey)

        self.hotkeys = dict()
        layout.addLayout(self.addHotkey("hotkey_player1", _("Player 1")))
        layout.addLayout(self.addHotkey("hotkey_player2", _("Player 2")))
        layout.addLayout(self.addHotkey("hotkey_debug", _("Debug")))

        self.cb_single_hotkey.setChecked(
            self.hotkeys['hotkey_player1'].getKey()
            == self.hotkeys['hotkey_player2'].getKey())
        self.connectHotkeys()
        label = QLabel(_("Player 1 is always the player your observer"
                         " camera is centered on at start of a game."))
        layout.addWidget(label)
        self.hotkeyBox.setLayout(layout)
        mainLayout.addWidget(self.hotkeyBox)

        self.introBox = QGroupBox(_("Animation"))
        layout = QFormLayout()
        self.cb_animation = QComboBox()
        animation = scctool.settings.config.parser.get("Intros", "animation")
        currentIdx = 0
        idx = 0
        options = dict()
        options['Fly-In'] = _("Fly-In")
        options['Slide'] = _("Slide")
        options['Fanfare'] = _("Fanfare")
        for key, item in options.items():
            self.cb_animation.addItem(item, key)
            if(key == animation):
                currentIdx = idx
            idx += 1
        self.cb_animation.setCurrentIndex(currentIdx)
        self.cb_animation.currentIndexChanged.connect(self.changed)
        label = QLabel(_("Animation:") + " ")
        label.setMinimumWidth(120)
        layout.addRow(label, self.cb_animation)
        self.sb_displaytime = QDoubleSpinBox()
        self.sb_displaytime.setRange(0, 10)
        self.sb_displaytime.setDecimals(1)
        self.sb_displaytime.setValue(
            scctool.settings.config.parser.getfloat("Intros", "display_time"))
        self.sb_displaytime.setSuffix(" " + _("Seconds"))
        self.sb_displaytime.valueChanged.connect(self.changed)
        layout.addRow(QLabel(
            _("Display Duration:") + " "), self.sb_displaytime)
        self.sl_sound = QSlider(Qt.Horizontal)
        self.sl_sound.setMinimum(0)
        self.sl_sound.setMaximum(20)
        self.sl_sound.setValue(
            scctool.settings.config.parser.getint("Intros", "sound_volume"))
        self.sl_sound.setTickPosition(QSlider.TicksBothSides)
        self.sl_sound.setTickInterval(1)
        self.sl_sound.valueChanged.connect(self.changed)
        layout.addRow(QLabel(
            _("Sound Volume:") + " "), self.sl_sound)
        self.introBox.setLayout(layout)
        mainLayout.addWidget(self.introBox)

        self.ttsBox = QGroupBox(_("Text-to-Speech"))
        layout = QFormLayout()

        self.cb_tts_active = QCheckBox()
        self.cb_tts_active.setChecked(
            scctool.settings.config.parser.getboolean("Intros", "tts_active"))
        self.cb_tts_active.stateChanged.connect(self.changed)
        label = QLabel(_("Activate Text-to-Speech:") + " ")
        label.setMinimumWidth(120)
        layout.addRow(label, self.cb_tts_active)

        self.icons = {}
        self.icons['MALE'] = QIcon(scctool.settings.getResFile('male.png'))
        self.icons['FEMALE'] = QIcon(scctool.settings.getResFile('female.png'))
        self.cb_tts_voice = QComboBox()

        currentIdx = 0
        idx = 0
        tts_voices = self.controller.tts.getVoices()
        tts_voice = scctool.settings.config.parser.get("Intros", "tts_voice")
        for voice in tts_voices:
            self.cb_tts_voice.addItem(
                self.icons[voice['ssmlGender']],
                '   ' + voice['name'],
                voice['name'])
            if(voice['name'] == tts_voice):
                currentIdx = idx
            idx += 1
        self.cb_tts_voice.setCurrentIndex(currentIdx)
        self.cb_tts_voice.currentIndexChanged.connect(self.changed)
        layout.addRow(QLabel(
            _("Voice:") + " "), self.cb_tts_voice)
        self.ttsBox.setStyleSheet("QComboBox { combobox-popup: 0; }")
        self.ttsBox.setLayout(layout)
        mainLayout.addWidget(self.ttsBox)

        self.sb_tts_pitch = QDoubleSpinBox()
        self.sb_tts_pitch.setRange(-20, 20)
        self.sb_tts_pitch.setDecimals(2)
        self.sb_tts_pitch.setValue(
            scctool.settings.config.parser.getfloat("Intros", "tts_pitch"))
        self.sb_tts_pitch.valueChanged.connect(self.changed)
        layout.addRow(QLabel(
            _("Pitch:") + " "), self.sb_tts_pitch)

        self.sb_tts_rate = QDoubleSpinBox()
        self.sb_tts_rate.setRange(0.25, 4.00)
        self.sb_tts_rate.setSingleStep(0.1)
        self.sb_tts_rate.setDecimals(2)
        self.sb_tts_rate.setValue(
            scctool.settings.config.parser.getfloat("Intros", "tts_rate"))
        self.sb_tts_rate.valueChanged.connect(self.changed)
        layout.addRow(QLabel(
            _("Rate:") + " "), self.sb_tts_rate)

        self.cb_tts_scope = QComboBox()
        scope = scctool.settings.config.parser.get("Intros", "tts_scope")
        currentIdx = 0
        idx = 0
        options = self.controller.tts.getOptions()
        for key, item in options.items():
            self.cb_tts_scope.addItem(item['desc'], key)
            if(key == scope):
                currentIdx = idx
            idx += 1
        self.cb_tts_scope.setCurrentIndex(currentIdx)
        self.cb_tts_scope.currentIndexChanged.connect(self.changed)
        layout.addRow(QLabel(
            _("Line:") + " "), self.cb_tts_scope)

        self.sl_tts_sound = QSlider(Qt.Horizontal)
        self.sl_tts_sound.setMinimum(0)
        self.sl_tts_sound.setMaximum(20)
        self.sl_tts_sound.setValue(
            scctool.settings.config.parser.getint("Intros", "tts_volume"))
        self.sl_tts_sound.setTickPosition(QSlider.TicksBothSides)
        self.sl_tts_sound.setTickInterval(1)
        self.sl_tts_sound.valueChanged.connect(self.changed)
        layout.addRow(QLabel(
            _("Sound Volume:") + " "), self.sl_tts_sound)

        text = _(
            "Text-to-Speech provided by Google-Cloud is paid for "
            "by StarCraft Casting Tool Patrons. To keep this service up "
            "consider becoming a <a href='{patreon}'>Patron</a> yourself. "
            "You can test all voices at {tts}.")

        patreon = 'https://www.patreon.com/StarCraftCastingTool'

        url = 'https://cloud.google.com/text-to-speech/'
        tts = "<a href='{}'>cloud.google.com/text-to-speech</a>"
        tts = tts.format(url)

        label = QLabel(text.format(patreon=patreon, tts=tts))
        label.setAlignment(Qt.AlignJustify)
        label.setOpenExternalLinks(True)
        label.setWordWrap(True)
        label.setMargin(5)
        layout.addRow(label)

        mainLayout.addItem(QSpacerItem(
            0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))
        self.formGroupIntro.setLayout(mainLayout)

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
        if(self.__dataChanged):
            self.saveWebsocketdata()

            maps = list()
            for i in range(self.maplist.count()):
                maps.append(str(self.maplist.item(i).text()).strip())

            self.controller.mapstatsManager.setCustomMapPool(maps)
            self.controller.mapstatsManager.setMapPoolType(
                self.cb_mappool.currentIndex())

            scctool.settings.config.parser.set(
                "Mapstats",
                "autoset_next_map",
                str(self.cb_autoset_map.isChecked()))

            scctool.settings.config.parser.set(
                "Mapstats",
                "mark_played",
                str(self.cb_mark_played.isChecked()))

            scctool.settings.config.parser.set(
                "Mapstats",
                "mark_vetoed",
                str(self.cb_mark_vetoed.isChecked()))

            self.controller.mapstatsManager.sendMapPool()
            self.mainWindow.updateAllMapButtons()

            for idx in range(0, 3):
                scctool.settings.config.parser.set(
                    "MapIcons", "scope_box_{}".format(idx + 1),
                    self.scope_box[idx].getScope())
                scctool.settings.config.parser.set(
                    "MapIcons", "scope_landscape_{}".format(idx + 1),
                    self.scope_landscape[idx].getScope())
            self.controller.matchMetaDataChanged()
            self.__dataChanged = False
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
            "Intros", "animation", self.cb_animation.currentData().strip())
        scctool.settings.config.parser.set(
            "Intros", "tts_voice", self.cb_tts_voice.currentData().strip())
        scctool.settings.config.parser.set(
            "Intros", "tts_scope", self.cb_tts_scope.currentData().strip())
        scctool.settings.config.parser.set(
            "Intros", "tts_active", str(self.cb_tts_active.isChecked()))
        scctool.settings.config.parser.set(
            "Intros", "tts_volume", str(self.sl_tts_sound.value()))
        scctool.settings.config.parser.set(
            "Intros", "tts_pitch", str(self.sb_tts_pitch.value()))
        scctool.settings.config.parser.set(
            "Intros", "tts_rate", str(self.sb_tts_rate.value()))

    def openHTML(self, file):
        """Open file in browser."""
        self.controller.openURL(scctool.settings.getAbsPath(file))

    def changePadding(self, scope, padding):
        scctool.settings.config.parser.set(
            "MapIcons", "padding_{}".format(scope),
            str(padding))
        self.controller.websocketThread.changePadding(
            "mapicons_{}".format(scope), padding)

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
