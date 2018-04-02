"""Show connections settings sub window."""
import logging
import PyQt5

from scctool.view.widgets import MonitoredLineEdit, Completer, HotkeyLayout

import scctool.settings
import keyboard
import weakref

# create logger
module_logger = logging.getLogger('scctool.view.subConnections')


class SubwindowConnections(PyQt5.QtWidgets.QWidget):
    """Show connections settings sub window."""

    def createWindow(self, mainWindow):
        """Create window."""
        try:
            parent = None
            super(SubwindowConnections, self).__init__(parent)
            # self.setWindowFlags(PyQt5.QtCore.Qt.WindowStaysOnTopHint)

            self.setWindowIcon(
                PyQt5.QtGui.QIcon(scctool.settings.getAbsPath('src/connection.png')))
            self.setWindowModality(PyQt5.QtCore.Qt.ApplicationModal)
            self.mainWindow = mainWindow
            self.passEvent = False
            self.controller = mainWindow.controller
            self.__dataChanged = False

            self.createButtonGroup()
            self.createTabs()

            mainLayout = PyQt5.QtWidgets.QVBoxLayout()

            mainLayout.addWidget(self.tabs)
            mainLayout.addLayout(self.buttonGroup)

            self.setLayout(mainLayout)

            self.resize(PyQt5.QtCore.QSize(mainWindow.size().width()
                                           * 0.8, self.sizeHint().height()))
            relativeChange = PyQt5.QtCore.QPoint(mainWindow.size().width() / 2,
                                                 mainWindow.size().height() / 3) -\
                PyQt5.QtCore.QPoint(self.size().width() / 2,
                                    self.size().height() / 3)
            self.move(mainWindow.pos() + relativeChange)

            self.setWindowTitle(_("Connections"))

        except Exception as e:
            module_logger.exception("message")

    def createTabs(self):
        """Create tabs."""
        self.tabs = PyQt5.QtWidgets.QTabWidget()

        self.createFormGroupWebsocket()
        self.createFormGroupTwitch()
        self.createFormGroupNightbot()

        # Add tabs
        self.tabs.addTab(self.formGroupWebsocket, _("Intros && Hotkeys"))
        self.tabs.addTab(self.formGroupTwitch, _("Twitch"))
        self.tabs.addTab(self.formGroupNightbot, _("Nightbot"))

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

    def createFormGroupWebsocket(self):
        """Create forms for OBS websocket connection."""
        self.formGroupWebsocket = PyQt5.QtWidgets.QWidget()
        mainLayout = PyQt5.QtWidgets.QVBoxLayout()

        self.hotkeyBox = PyQt5.QtWidgets.QGroupBox(_("Intro Hotkeys"))
        layout = PyQt5.QtWidgets.QVBoxLayout()

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

        self.introBox = PyQt5.QtWidgets.QGroupBox(_("Intro Settings"))
        layout = PyQt5.QtWidgets.QFormLayout()
        self.sl_sound = PyQt5.QtWidgets.QSlider(PyQt5.QtCore.Qt.Horizontal)
        self.sl_sound.setMinimum(0)
        self.sl_sound.setMaximum(10)
        self.sl_sound.setValue(
            scctool.settings.config.parser.getint("Intros", "sound_volume"))
        self.sl_sound.setTickPosition(PyQt5.QtWidgets.QSlider.TicksBothSides)
        self.sl_sound.setTickInterval(1)
        self.sl_sound.valueChanged.connect(self.changed)
        layout.addRow(PyQt5.QtWidgets.QLabel(
            _("Sound Volume:") + " "), self.sl_sound)
        self.sb_displaytime = PyQt5.QtWidgets.QDoubleSpinBox()
        self.sb_displaytime.setRange(0, 10)
        self.sb_displaytime.setDecimals(1)
        self.sb_displaytime.setValue(
            scctool.settings.config.parser.getfloat("Intros", "display_time"))
        self.sb_displaytime.setSuffix(" " + _("Seconds"))
        self.sb_displaytime.valueChanged.connect(self.changed)
        layout.addRow(PyQt5.QtWidgets.QLabel(
            _("Display Duration:") + " "), self.sb_displaytime)
        self.cb_animation = PyQt5.QtWidgets.QComboBox()
        animation = scctool.settings.config.parser.get("Intros", "animation")
        currentIdx = 0
        idx = 0
        for item in ["Fly-In", "Slide", "Fanfare"]:
            self.cb_animation.addItem(item)
            if(item == animation):
                currentIdx = idx
            idx += 1
        self.cb_animation.setCurrentIndex(currentIdx)
        layout.addRow(PyQt5.QtWidgets.QLabel(
            _("Animation:") + " "), self.cb_animation)
        self.introBox.setLayout(layout)
        mainLayout.addWidget(self.introBox)

        mainLayout.addItem(PyQt5.QtWidgets.QSpacerItem(
            0, 0, PyQt5.QtWidgets.QSizePolicy.Minimum, PyQt5.QtWidgets.QSizePolicy.Expanding))
        self.formGroupWebsocket.setLayout(mainLayout)

    def createFormGroupTwitch(self):
        """Create forms for twitch."""
        self.formGroupTwitch = PyQt5.QtWidgets.QWidget()
        layout = PyQt5.QtWidgets.QFormLayout()

        self.twitchChannel = MonitoredLineEdit()
        self.twitchChannel.textModified.connect(self.changed)
        self.twitchChannel.setText(
            scctool.settings.config.parser.get("Twitch", "channel"))
        self.twitchChannel.setAlignment(PyQt5.QtCore.Qt.AlignCenter)
        self.twitchChannel.setPlaceholderText(
            _("Name of the Twitch channel that should be updated"))
        self.twitchChannel.setToolTip(
            _('The connected twitch user needs to have editor rights for this channel.'))
        layout.addRow(PyQt5.QtWidgets.QLabel(
            "Twitch-Channel:"), self.twitchChannel)

        container = PyQt5.QtWidgets.QHBoxLayout()

        self.twitchToken = MonitoredLineEdit()
        self.twitchToken.textModified.connect(self.changed)
        self.twitchToken.setText(
            scctool.settings.config.parser.get("Twitch", "oauth"))
        self.twitchToken.setAlignment(PyQt5.QtCore.Qt.AlignCenter)
        self.twitchToken.setPlaceholderText(
            _("Press 'Get' to generate a token"))
        self.twitchToken.setEchoMode(PyQt5.QtWidgets.QLineEdit.Password)
        self.twitchToken.setToolTip(_("Press 'Get' to generate a new token."))
        container.addWidget(self.twitchToken)

        self.pb_getTwitch = PyQt5.QtWidgets.QPushButton(_('Get'))
        self.pb_getTwitch.setFixedWidth(100)
        self.pb_getTwitch.clicked.connect(self.controller.getTwitchToken)
        container.addWidget(self.pb_getTwitch)

        layout.addRow(PyQt5.QtWidgets.QLabel(_("Access-Token:")), container)

        container = PyQt5.QtWidgets.QHBoxLayout()

        self.twitchTemplate = MonitoredLineEdit()
        self.twitchTemplate.textModified.connect(self.changed)
        self.twitchTemplate.setText(
            scctool.settings.config.parser.get("Twitch", "title_template"))
        self.twitchTemplate.setAlignment(PyQt5.QtCore.Qt.AlignCenter)
        self.twitchTemplate.setPlaceholderText("(League) – (Team1) vs (Team2)")
        self.twitchTemplate.setToolTip(
            _('Available placeholders:') + " " +
            ', '.join(self.controller.placeholders.available()))

        completer = Completer(
            self.controller.placeholders.available(), self.twitchTemplate)

        self.twitchTemplate.setCompleter(completer)

        container.addWidget(self.twitchTemplate)

        button = PyQt5.QtWidgets.QPushButton(_('Test'))
        button.setFixedWidth(100)
        button.clicked.connect(
            lambda: self.testPlaceholder(self.twitchTemplate.text()))
        container.addWidget(button)

        label = PyQt5.QtWidgets.QLabel(_("Title Template:"))
        label.setFixedWidth(100)
        layout.addRow(label, container)

        self.formGroupTwitch.setLayout(layout)

    def createFormGroupNightbot(self):
        """Create forms for nightbot."""
        self.formGroupNightbot = PyQt5.QtWidgets.QWidget()
        mainLayout = PyQt5.QtWidgets.QVBoxLayout()
        tokenBox = PyQt5.QtWidgets.QGroupBox("Access-Token")
        container = PyQt5.QtWidgets.QHBoxLayout()

        self.nightbotToken = MonitoredLineEdit()
        self.nightbotToken.textModified.connect(self.changed)
        self.nightbotToken.setText(
            scctool.settings.config.parser.get("Nightbot", "token"))
        self.nightbotToken.setAlignment(PyQt5.QtCore.Qt.AlignCenter)
        self.nightbotToken.setEchoMode(PyQt5.QtWidgets.QLineEdit.Password)
        self.nightbotToken.setPlaceholderText(
            _("Press 'Get' to generate a token"))
        self.nightbotToken.setToolTip(
            _("Press 'Get' to generate a token."))
        container.addWidget(self.nightbotToken)
        self.pb_getNightbot = PyQt5.QtWidgets.QPushButton(_('Get'))
        self.pb_getNightbot.clicked.connect(self.controller.getNightbotToken)
        self.pb_getNightbot.setFixedWidth(100)
        # self.pb_getNightbot.setEnabled(False)
        container.addWidget(self.pb_getNightbot)

        tokenBox.setLayout(container)

        mainLayout.addWidget(tokenBox, 0)

        # scroll area widget contents - layout
        self.scrollLayout = PyQt5.QtWidgets.QVBoxLayout()
        self.scrollLayout.setDirection(PyQt5.QtWidgets.QBoxLayout.BottomToTop)
        self.scrollLayout.addStretch(0)
        buttonLayout = PyQt5.QtWidgets.QHBoxLayout()
        buttonLayout.addStretch(0)
        self.scrollLayout.addLayout(buttonLayout)

        # scroll area widget contents
        self.scrollWidget = PyQt5.QtWidgets.QWidget()
        self.scrollWidget.setLayout(self.scrollLayout)

        # scroll area
        self.scrollArea = PyQt5.QtWidgets.QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setWidget(self.scrollWidget)
        self.scrollArea.setFixedHeight(180)

        mainLayout.addWidget(self.scrollArea, 1)

        layout = PyQt5.QtWidgets.QHBoxLayout()
        layout.addWidget(PyQt5.QtWidgets.QLabel(""))
        addButton = PyQt5.QtWidgets.QPushButton(_('Add Command'))
        addButton.clicked.connect(lambda: self.addCommand())
        layout.addWidget(addButton)

        mainLayout.addLayout(layout, 0)

        data = scctool.settings.nightbot_commands

        if len(data) == 0:
            self.addCommand()
        else:
            for cmd, msg in data.items():
                self.addCommand(cmd, msg)

        self.formGroupNightbot.setLayout(mainLayout)

    def addCommand(self, cmd="", msg=""):
        if msg != "__DELETE__":
            dropbox = CommandDropBox(self.controller, cmd=cmd, msg=msg)
            dropbox.connect(self.changed)
            self.scrollLayout.insertWidget(1, dropbox)
        else:
            CommandDropBox.addDeletedCommand(cmd)

    def createButtonGroup(self):
        """Create buttons."""
        try:
            layout = PyQt5.QtWidgets.QHBoxLayout()

            layout.addWidget(PyQt5.QtWidgets.QLabel(""))

            buttonCancel = PyQt5.QtWidgets.QPushButton(_('Cancel'))
            buttonCancel.clicked.connect(self.closeWindow)
            layout.addWidget(buttonCancel)

            buttonSave = PyQt5.QtWidgets.QPushButton(_('Save && Close'))
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

        scctool.settings.config.parser.set(
            "Twitch", "channel", self.twitchChannel.text().strip())
        scctool.settings.config.parser.set(
            "Twitch", "oauth", self.twitchToken.text().strip())
        scctool.settings.config.parser.set(
            "Twitch", "title_template", self.twitchTemplate.text().strip())

        scctool.settings.nightbot_commands = CommandDropBox.getData()

        self.saveWebsocketdata()

        self.controller.refreshButtonStatus()

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
                CommandDropBox.clean()
                event.accept()
                return
            if(not self.passEvent):
                if(self.isMinimized()):
                    self.showNormal()
                buttonReply = PyQt5.QtWidgets.QMessageBox.question(
                    self, _('Save data?'), _("Do you want to save the data?"),
                    PyQt5.QtWidgets.QMessageBox.Yes | PyQt5.QtWidgets.QMessageBox.No,
                    PyQt5.QtWidgets.QMessageBox.No)
                if buttonReply == PyQt5.QtWidgets.QMessageBox.Yes:
                    self.saveData()
            self.controller.updateHotkeys()
            CommandDropBox.clean()
            event.accept()
        except Exception as e:
            module_logger.exception("message")

    def testPlaceholder(self, string):
        """Test placeholders."""
        string = self.controller.placeholders.replace(string)
        PyQt5.QtWidgets.QMessageBox.information(self, _("Output:"), string)


class CommandDropBox(PyQt5.QtWidgets.QGroupBox):
    _instances = set()
    _todelete = set()

    def __init__(self, controller, cmd="", msg="", parent=None):
        super(CommandDropBox, self).__init__(parent)
        self.controller = controller
        self._instances.add(weakref.ref(self))
        self.ident = len(self._instances)
        layout = PyQt5.QtWidgets.QHBoxLayout()

        self.command = MonitoredLineEdit()
        self.command.setText(cmd)
        self.command.setAlignment(PyQt5.QtCore.Qt.AlignCenter)
        self.command.setPlaceholderText(("!command"))
        layout.addWidget(self.command)

        self.message = MonitoredLineEdit()
        self.message.setText(msg)
        self.message.setAlignment(PyQt5.QtCore.Qt.AlignCenter)
        self.message.setPlaceholderText(_('message, e.g.,') + ' (URL)')
        self.message.setToolTip(
            _('Available placeholders:') + ' ' +
            ', '.join(self.controller.placeholders.available()))
        completer = Completer(
            self.controller.placeholders.available(), self.message)

        self.message.setCompleter(completer)
        layout.addWidget(self.message)

        self.pushButton1 = PyQt5.QtWidgets.QPushButton(_('Test'))
        self.pushButton1.clicked.connect(
            lambda: self.testPlaceholder(self.message.text()))
        layout.addWidget(self.pushButton1)

        self.pushButton2 = PyQt5.QtWidgets.QPushButton(_('Delete'))
        self.pushButton2.clicked.connect(self.remove)
        layout.addWidget(self.pushButton2)
        self.setLayout(layout)

        for ref in self._instances:
            obj = ref()
            if obj is not None:
                obj.setTitle()

    def connect(self, handler):
        self.command.textModified.connect(handler)
        self.message.textModified.connect(handler)

    def setTitle(self):
        title = "Command {}".format(self.ident)
        super(CommandDropBox, self).setTitle(title)
        self.pushButton2.setDisabled(len(self._instances) == 1)

    def adjustIdent(self, removedIdent):
        if removedIdent < self.ident:
            self.ident -= 1
        self.setTitle()

    def remove(self):
        self.parent().layout().removeWidget(self)
        cmd = self.command.text().strip()
        if cmd:
            self._todelete.add(cmd)
        self.deleteLater()
        self._instances.remove(weakref.ref(self))
        for ref in self._instances:
            obj = ref()
            if obj is not None:
                obj.adjustIdent(self.ident)

    def testPlaceholder(self, string):
        """Test placeholders."""
        string = self.controller.placeholders.replace(string)
        PyQt5.QtWidgets.QMessageBox.information(self, _("Output:"), string)

    @classmethod
    def addDeletedCommand(cls, cmd):
        cls._todelete.add(cmd.strip())

    @classmethod
    def getData(cls):
        data = dict()
        for cmd in cls._todelete:
            data[cmd] = "__DELETE__"
        for inst_ref in cls._instances:
            inst = inst_ref()
            if inst is not None:
                cmd = inst.command.text().strip()
                msg = inst.message.text().strip()
                if cmd and msg:
                    data[cmd] = msg
        return data

    @classmethod
    def clean(cls):
        cls._instances = set()
        cls._todelete = set()
