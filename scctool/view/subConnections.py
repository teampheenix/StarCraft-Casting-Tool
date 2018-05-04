"""Show connections settings sub window."""
import logging
import weakref

from PyQt5.QtCore import QPoint, QSize, Qt
from PyQt5.QtGui import QIcon, QKeySequence
from PyQt5.QtWidgets import (QBoxLayout, QFormLayout, QGroupBox, QHBoxLayout,
                             QLabel, QLineEdit, QMessageBox, QPushButton,
                             QScrollArea, QShortcut, QTabWidget, QVBoxLayout,
                             QWidget)

import scctool.settings
from scctool.view.widgets import Completer, MonitoredLineEdit

# create logger
module_logger = logging.getLogger('scctool.view.subConnections')


class SubwindowConnections(QWidget):
    """Show connections settings sub window."""

    def createWindow(self, mainWindow):
        """Create window."""
        try:
            parent = None
            super().__init__(parent)
            # self.setWindowFlags(Qt.WindowStaysOnTopHint)

            self.setWindowIcon(
                QIcon(scctool.settings.getResFile('twitch.png')))
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
                              * 0.8, self.sizeHint().height()))
            relativeChange = QPoint(mainWindow.size().width() / 2,
                                    mainWindow.size().height() / 3) -\
                QPoint(self.size().width() / 2,
                       self.size().height() / 3)
            self.move(mainWindow.pos() + relativeChange)

            self.setWindowTitle(_("Twitch & Nightbot Connections"))

        except Exception as e:
            module_logger.exception("message")

    def createTabs(self):
        """Create tabs."""
        self.tabs = QTabWidget()

        self.createFormGroupTwitch()
        self.createFormGroupNightbot()

        # Add tabs
        self.tabs.addTab(self.formGroupTwitch, QIcon(
            scctool.settings.getResFile('twitch.png')), _("Twitch"))
        self.tabs.addTab(self.formGroupNightbot, QIcon(
            scctool.settings.getResFile('nightbot.ico')), _("Nightbot"))

    def createFormGroupTwitch(self):
        """Create forms for twitch."""
        self.formGroupTwitch = QWidget()
        layout = QFormLayout()

        self.twitchChannel = MonitoredLineEdit()
        self.twitchChannel.textModified.connect(self.changed)
        self.twitchChannel.setText(
            scctool.settings.config.parser.get("Twitch", "channel"))
        self.twitchChannel.setAlignment(Qt.AlignCenter)
        self.twitchChannel.setPlaceholderText(
            _("Name of the Twitch channel that should be updated"))
        self.twitchChannel.setToolTip(
            _('The connected twitch user needs to have editor rights for this channel.'))
        layout.addRow(QLabel(
            "Twitch-Channel:"), self.twitchChannel)

        container = QHBoxLayout()

        self.twitchToken = MonitoredLineEdit()
        self.twitchToken.textModified.connect(self.changed)
        self.twitchToken.setText(
            scctool.settings.config.parser.get("Twitch", "oauth"))
        self.twitchToken.setAlignment(Qt.AlignCenter)
        self.twitchToken.setPlaceholderText(
            _("Press 'Get' to generate a token"))
        self.twitchToken.setEchoMode(QLineEdit.Password)
        self.twitchToken.setToolTip(_("Press 'Get' to generate a new token."))
        container.addWidget(self.twitchToken)

        self.pb_getTwitch = QPushButton(_('Get'))
        self.pb_getTwitch.setFixedWidth(100)
        self.pb_getTwitch.clicked.connect(self.controller.getTwitchToken)
        container.addWidget(self.pb_getTwitch)

        layout.addRow(QLabel(_("Access-Token:")), container)

        container = QHBoxLayout()

        self.twitchTemplate = MonitoredLineEdit()
        self.twitchTemplate.textModified.connect(self.changed)
        self.twitchTemplate.setText(
            scctool.settings.config.parser.get("Twitch", "title_template"))
        self.twitchTemplate.setAlignment(Qt.AlignCenter)
        self.twitchTemplate.setPlaceholderText("(League) – (Team1) vs (Team2)")
        self.twitchTemplate.setToolTip(
            _('Available placeholders:') + " " +
            ', '.join(self.controller.placeholders.available()))

        completer = Completer(
            self.controller.placeholders.available(), self.twitchTemplate)

        self.twitchTemplate.setCompleter(completer)

        container.addWidget(self.twitchTemplate)

        button = QPushButton(_('Test'))
        button.setFixedWidth(100)
        button.clicked.connect(
            lambda: self.testPlaceholder(self.twitchTemplate.text()))
        container.addWidget(button)

        label = QLabel(_("Title Template:"))
        label.setFixedWidth(100)
        layout.addRow(label, container)

        self.formGroupTwitch.setLayout(layout)

    def createFormGroupNightbot(self):
        """Create forms for nightbot."""
        self.formGroupNightbot = QWidget()
        mainLayout = QVBoxLayout()
        tokenBox = QGroupBox("Access-Token")
        container = QHBoxLayout()

        self.nightbotToken = MonitoredLineEdit()
        self.nightbotToken.textModified.connect(self.changed)
        self.nightbotToken.setText(
            scctool.settings.config.parser.get("Nightbot", "token"))
        self.nightbotToken.setAlignment(Qt.AlignCenter)
        self.nightbotToken.setEchoMode(QLineEdit.Password)
        self.nightbotToken.setPlaceholderText(
            _("Press 'Get' to generate a token"))
        self.nightbotToken.setToolTip(
            _("Press 'Get' to generate a token."))
        container.addWidget(self.nightbotToken)
        self.pb_getNightbot = QPushButton(_('Get'))
        self.pb_getNightbot.clicked.connect(self.controller.getNightbotToken)
        self.pb_getNightbot.setFixedWidth(100)
        # self.pb_getNightbot.setEnabled(False)
        container.addWidget(self.pb_getNightbot)

        tokenBox.setLayout(container)

        mainLayout.addWidget(tokenBox, 0)

        # scroll area widget contents - layout
        self.scrollLayout = QVBoxLayout()
        self.scrollLayout.setDirection(QBoxLayout.BottomToTop)
        self.scrollLayout.addStretch(0)
        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch(0)
        self.scrollLayout.addLayout(buttonLayout)

        # scroll area widget contents
        self.scrollWidget = QWidget()
        self.scrollWidget.setLayout(self.scrollLayout)

        # scroll area
        self.scrollArea = QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setWidget(self.scrollWidget)
        self.scrollArea.setFixedHeight(180)

        mainLayout.addWidget(self.scrollArea, 1)

        layout = QHBoxLayout()
        layout.addWidget(QLabel(""))
        addButton = QPushButton(_('Add Command'))
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

        scctool.settings.config.parser.set(
            "Twitch", "channel", self.twitchChannel.text().strip())
        scctool.settings.config.parser.set(
            "Twitch", "oauth", self.twitchToken.text().strip())
        scctool.settings.config.parser.set(
            "Twitch", "title_template", self.twitchTemplate.text().strip())

        scctool.settings.nightbot_commands = CommandDropBox.getData()

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
                buttonReply = QMessageBox.question(
                    self, _('Save data?'), _("Do you want to save the data?"),
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No)
                if buttonReply == QMessageBox.Yes:
                    self.saveData()
            self.controller.updateHotkeys()
            CommandDropBox.clean()
            event.accept()
        except Exception as e:
            module_logger.exception("message")

    def testPlaceholder(self, string):
        """Test placeholders."""
        string = self.controller.placeholders.replace(string)
        QMessageBox.information(self, _("Output:"), string)


class CommandDropBox(QGroupBox):
    _instances = set()
    _todelete = set()

    def __init__(self, controller, cmd="", msg="", parent=None):
        super().__init__(parent)
        self.controller = controller
        self._instances.add(weakref.ref(self))
        self.ident = len(self._instances)
        layout = QHBoxLayout()

        self.command = MonitoredLineEdit()
        self.command.setText(cmd)
        self.command.setAlignment(Qt.AlignCenter)
        self.command.setPlaceholderText(("!command"))
        layout.addWidget(self.command)

        self.message = MonitoredLineEdit()
        self.message.setText(msg)
        self.message.setAlignment(Qt.AlignCenter)
        self.message.setPlaceholderText(_('message, e.g.,') + ' (URL)')
        self.message.setToolTip(
            _('Available placeholders:') + ' ' +
            ', '.join(self.controller.placeholders.available()))
        completer = Completer(
            self.controller.placeholders.available(), self.message)

        self.message.setCompleter(completer)
        layout.addWidget(self.message)

        self.pushButton1 = QPushButton(_('Test'))
        self.pushButton1.clicked.connect(
            lambda: self.testPlaceholder(self.message.text()))
        layout.addWidget(self.pushButton1)

        self.pushButton2 = QPushButton(_('Delete'))
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
        super().setTitle(title)
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
        QMessageBox.information(self, _("Output:"), string)

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
