"""Show connections settings sub window."""
import logging
import PyQt5

from scctool.view.widgets import MonitoredLineEdit, FTPsetup, Completer

import scctool.settings
import scctool.tasks.obs
import base64

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
                                           * 0.7, self.sizeHint().height()))
            relativeChange = PyQt5.QtCore.QPoint(mainWindow.size().width() / 2,
                                                 mainWindow.size().height() / 3) -\
                PyQt5.QtCore.QPoint(self.size().width() / 2,
                                    self.size().height() / 3)
            self.move(mainWindow.pos() + relativeChange)

            self.setWindowTitle("Connections")

        except Exception as e:
            module_logger.exception("message")

    def createTabs(self):
        """Create tabs."""
        self.tabs = PyQt5.QtWidgets.QTabWidget()

        self.createFormGroupFTP()
        self.createFormGroupOBS()
        self.createFormGroupTwitch()
        self.createFormGroupNightbot()

        # Add tabs
        self.tabs.addTab(self.formGroupFTP, "FTP")
        self.tabs.addTab(self.formGroupTwitch, "Twitch")
        self.tabs.addTab(self.formGroupNightbot, "Nightbot")
        self.tabs.addTab(self.formGroupOBS, "OBS via Websocket Plugin")

    def createFormGroupFTP(self):
        """Create form group for FTP."""
        self.formGroupFTP = PyQt5.QtWidgets.QWidget()
        layout = PyQt5.QtWidgets.QFormLayout()

        self.ftpServer = MonitoredLineEdit()
        self.ftpServer.textModified.connect(self.changed)
        self.ftpServer.setText(
            scctool.settings.config.parser.get("FTP", "server").strip())
        self.ftpServer.setAlignment(PyQt5.QtCore.Qt.AlignCenter)
        self.ftpServer.setPlaceholderText("FTP server address")
        self.ftpServer.setToolTip('')
        layout.addRow(PyQt5.QtWidgets.QLabel("Host:"), self.ftpServer)

        self.ftpUser = MonitoredLineEdit()
        self.ftpUser.textModified.connect(self.changed)
        self.ftpUser.setText(
            scctool.settings.config.parser.get("FTP", "user").strip())
        self.ftpUser.setAlignment(PyQt5.QtCore.Qt.AlignCenter)
        self.ftpUser.setPlaceholderText("FTP username")
        self.ftpUser.setToolTip('')
        layout.addRow(PyQt5.QtWidgets.QLabel("Username:"), self.ftpUser)

        self.ftpPwd = MonitoredLineEdit()
        self.ftpPwd.textModified.connect(self.changed)
        self.ftpPwd.setText(base64.b64decode(scctool.settings.config.parser.get(
            "FTP", "passwd").strip().encode()).decode("utf8"))
        self.ftpPwd.setAlignment(PyQt5.QtCore.Qt.AlignCenter)
        self.ftpPwd.setPlaceholderText("FTP password")
        self.ftpPwd.setToolTip('')
        self.ftpPwd.setEchoMode(PyQt5.QtWidgets.QLineEdit.Password)
        label = PyQt5.QtWidgets.QLabel("Password:")
        # label.setFixedWidth(100)
        layout.addRow(label, self.ftpPwd)

        self.ftpDir = MonitoredLineEdit()
        self.ftpDir.textModified.connect(self.changed)
        self.ftpDir.setText(
            scctool.settings.config.parser.get("FTP", "dir").strip())
        self.ftpDir.setAlignment(PyQt5.QtCore.Qt.AlignCenter)
        self.ftpDir.setPlaceholderText("currently using root directory")
        self.ftpDir.setToolTip('')
        layout.addRow(PyQt5.QtWidgets.QLabel("Directory:"), self.ftpDir)

        container = PyQt5.QtWidgets.QHBoxLayout()
        self.pb_testFTP = PyQt5.QtWidgets.QPushButton(
            'Test && Setup FTP server')
        self.pb_testFTP.clicked.connect(self.testFTP)
        container.addWidget(self.pb_testFTP)

        layout.addRow(PyQt5.QtWidgets.QLabel(""), container)

        self.formGroupFTP.setLayout(layout)

    def testFTP(self):
        """Test FTP settings."""
        self.saveFtpData()
        FTPsetup(self.controller, self)

    def testOBS(self):
        """Test OBS websocket settings."""
        self.saveOBSdata()
        msg = scctool.tasks.obs.testConnection()
        PyQt5.QtWidgets.QMessageBox.warning(
            self, "OBS Websocket Connection Test", msg)

    def createFormGroupOBS(self):
        """Create forms for OBS websocket connection."""
        self.formGroupOBS = PyQt5.QtWidgets.QWidget()
        layout = PyQt5.QtWidgets.QFormLayout()

        self.obsPort = MonitoredLineEdit()
        self.obsPort.textModified.connect(self.changed)
        self.obsPort.setText(scctool.settings.config.parser.get("OBS", "port"))
        self.obsPort.setAlignment(PyQt5.QtCore.Qt.AlignCenter)
        self.obsPort.setPlaceholderText("Server Port (Default: 4444)")
        self.obsPort.setToolTip('')
        layout.addRow(PyQt5.QtWidgets.QLabel("Server Port:"), self.obsPort)

        self.obsPasswd = MonitoredLineEdit()
        self.obsPasswd.textModified.connect(self.changed)
        self.obsPasswd.setText(base64.b64decode(scctool.settings.config.parser.get(
            "OBS", "passwd").strip().encode()).decode("utf8"))
        self.obsPasswd.setEchoMode(PyQt5.QtWidgets.QLineEdit.Password)
        self.obsPasswd.setAlignment(PyQt5.QtCore.Qt.AlignCenter)
        self.obsPasswd.setPlaceholderText("recommended")
        self.obsPasswd.setToolTip('')
        label = PyQt5.QtWidgets.QLabel("Password:")
        # label.setFixedWidth(100)
        layout.addRow(label, self.obsPasswd)

        self.obsSources = MonitoredLineEdit()
        self.obsSources.textModified.connect(self.changed)
        self.obsSources.setText(
            scctool.settings.config.parser.get("OBS", "sources"))
        self.obsSources.setAlignment(PyQt5.QtCore.Qt.AlignCenter)
        self.obsSources.setPlaceholderText("Intro1, Intro2")
        string = 'Name of the OBS-sources that should automatically' +\
                 ' be hidden 4.5 sec after they become visible.'
        self.obsSources.setToolTip(string)
        layout.addRow(PyQt5.QtWidgets.QLabel("Sources:"), self.obsSources)

        self.obsActive = PyQt5.QtWidgets.QCheckBox(" Automatic hide sources")
        self.obsActive.setChecked(
            scctool.settings.config.parser.getboolean("OBS", "active"))
        self.obsActive.setToolTip('')
        self.obsActive.stateChanged.connect(self.changed)
        layout.addRow(PyQt5.QtWidgets.QLabel("Active:"), self.obsActive)

        self.pb_testOBS = PyQt5.QtWidgets.QPushButton('Test Connection to OBS')
        self.pb_testOBS.clicked.connect(self.testOBS)
        layout.addRow(PyQt5.QtWidgets.QLabel(), self.pb_testOBS)

        self.formGroupOBS.setLayout(layout)

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
            "Name of the Twitch channel that should be updated")
        self.twitchChannel.setToolTip(
            'The connected twitch user needs to have editor rights for this channel.')
        layout.addRow(PyQt5.QtWidgets.QLabel(
            "Twitch-Channel:"), self.twitchChannel)

        container = PyQt5.QtWidgets.QHBoxLayout()

        self.twitchToken = MonitoredLineEdit()
        self.twitchToken.textModified.connect(self.changed)
        self.twitchToken.setText(
            scctool.settings.config.parser.get("Twitch", "oauth"))
        self.twitchToken.setAlignment(PyQt5.QtCore.Qt.AlignCenter)
        self.twitchToken.setPlaceholderText("Press 'Get' to generate a token")
        self.twitchToken.setEchoMode(PyQt5.QtWidgets.QLineEdit.Password)
        self.twitchToken.setToolTip("Press 'Get' to generate a new token.")
        container.addWidget(self.twitchToken)

        self.pb_getTwitch = PyQt5.QtWidgets.QPushButton('Get')
        self.pb_getTwitch.setFixedWidth(100)
        self.pb_getTwitch.clicked.connect(self.controller.getTwitchToken)
        container.addWidget(self.pb_getTwitch)

        layout.addRow(PyQt5.QtWidgets.QLabel("Access-Token:"), container)

        container = PyQt5.QtWidgets.QHBoxLayout()

        self.twitchTemplate = MonitoredLineEdit()
        self.twitchTemplate.textModified.connect(self.changed)
        self.twitchTemplate.setText(
            scctool.settings.config.parser.get("Twitch", "title_template"))
        self.twitchTemplate.setAlignment(PyQt5.QtCore.Qt.AlignCenter)
        self.twitchTemplate.setPlaceholderText("(League) – (Team1) vs (Team2)")
        self.twitchTemplate.setToolTip(
            'Avaiable placeholders: ' + ', '.join(self.controller.placeholders.available()))

        completer = Completer(
            self.controller.placeholders.available(), self.twitchTemplate)

        self.twitchTemplate.setCompleter(completer)

        container.addWidget(self.twitchTemplate)

        button = PyQt5.QtWidgets.QPushButton('Test')
        button.setFixedWidth(100)
        button.clicked.connect(
            lambda: self.testPlaceholder(self.twitchTemplate.text()))
        container.addWidget(button)

        label = PyQt5.QtWidgets.QLabel("Title Template:")
        label.setFixedWidth(100)
        layout.addRow(label, container)

        self.formGroupTwitch.setLayout(layout)

    def createFormGroupNightbot(self):
        """Create forms for nightbot."""
        self.formGroupNightbot = PyQt5.QtWidgets.QWidget()
        layout = PyQt5.QtWidgets.QFormLayout()
        container = PyQt5.QtWidgets.QHBoxLayout()

        self.nightbotToken = MonitoredLineEdit()
        self.nightbotToken.textModified.connect(self.changed)
        self.nightbotToken.setText(
            scctool.settings.config.parser.get("Nightbot", "token"))
        self.nightbotToken.setAlignment(PyQt5.QtCore.Qt.AlignCenter)
        self.nightbotToken.setEchoMode(PyQt5.QtWidgets.QLineEdit.Password)
        self.nightbotToken.setPlaceholderText(
            "Press 'Get' to generate a token")
        self.nightbotToken.setToolTip("Press 'Get' to generate a new token.")

        self.nightbotCommand = MonitoredLineEdit()
        self.nightbotCommand.textModified.connect(self.changed)
        self.nightbotCommand.setText(
            scctool.settings.config.parser.get("Nightbot", "command"))
        self.nightbotCommand.setPlaceholderText("!matchlink")
        self.nightbotCommand.setAlignment(PyQt5.QtCore.Qt.AlignCenter)

        container.addWidget(self.nightbotToken)
        self.pb_getNightbot = PyQt5.QtWidgets.QPushButton('Get')
        self.pb_getNightbot.clicked.connect(self.controller.getNightbotToken)
        self.pb_getNightbot.setFixedWidth(100)
        # self.pb_getNightbot.setEnabled(False)
        container.addWidget(self.pb_getNightbot)

        layout.addRow(PyQt5.QtWidgets.QLabel("Access-Token:"), container)
        label = PyQt5.QtWidgets.QLabel("Command:")
        label.setFixedWidth(100)
        layout.addRow(label, self.nightbotCommand)

        container = PyQt5.QtWidgets.QHBoxLayout()

        self.nightbotMsg = MonitoredLineEdit()
        self.nightbotMsg.textModified.connect(self.changed)
        self.nightbotMsg.setText(
            scctool.settings.config.parser.get("Nightbot", "message"))
        self.nightbotMsg.setAlignment(PyQt5.QtCore.Qt.AlignCenter)
        self.nightbotMsg.setPlaceholderText("(URL)")
        self.nightbotMsg.setToolTip(
            'Avaiable placeholders: ' + ', '.join(self.controller.placeholders.available()))

        completer = Completer(
            self.controller.placeholders.available(), self.nightbotMsg)

        self.nightbotMsg.setCompleter(completer)

        container.addWidget(self.nightbotMsg)
        button = PyQt5.QtWidgets.QPushButton('Test')
        button.setFixedWidth(100)
        button.clicked.connect(
            lambda: self.testPlaceholder(self.nightbotMsg.text()))
        container.addWidget(button)

        layout.addRow(PyQt5.QtWidgets.QLabel("Message:"), container)

        self.formGroupNightbot.setLayout(layout)

    def createButtonGroup(self):
        """Create buttons."""
        try:
            layout = PyQt5.QtWidgets.QHBoxLayout()

            layout.addWidget(PyQt5.QtWidgets.QLabel(""))

            buttonCancel = PyQt5.QtWidgets.QPushButton('Cancel')
            buttonCancel.clicked.connect(self.closeWindow)
            layout.addWidget(buttonCancel)

            buttonSave = PyQt5.QtWidgets.QPushButton('Save && Close')
            buttonSave.clicked.connect(self.saveCloseWindow)
            layout.addWidget(buttonSave)

            self.buttonGroup = layout
        except Exception as e:
            module_logger.exception("message")

    def testPlaceholder(self, string):
        """Test placeholders."""
        string = self.controller.placeholders.replace(string)
        PyQt5.QtWidgets.QMessageBox.information(self, "Output:", string)

    def changed(self):
        """Handle changed data."""
        self.__dataChanged = True

    def saveData(self):
        """Save the data to config."""
        if(self.__dataChanged):

            self.saveFtpData()

            scctool.settings.config.parser.set(
                "Twitch", "channel", self.twitchChannel.text().strip())
            scctool.settings.config.parser.set(
                "Twitch", "oauth", self.twitchToken.text().strip())
            scctool.settings.config.parser.set(
                "Twitch", "title_template", self.twitchTemplate.text().strip())
            scctool.settings.config.parser.set(
                "Nightbot", "token", self.nightbotToken.text().strip())
            scctool.settings.config.parser.set(
                "Nightbot", "command", self.nightbotCommand.text().strip())
            scctool.settings.config.parser.set(
                "Nightbot", "message", self.nightbotMsg.text().strip())

            self.saveOBSdata()

            self.controller.refreshButtonStatus()

    def saveFtpData(self):
        """Save FTP data."""
        scctool.settings.config.parser.set(
            "FTP", "server", self.ftpServer.text().strip())
        scctool.settings.config.parser.set(
            "FTP", "user", self.ftpUser.text().strip())
        scctool.settings.config.parser.set("FTP", "passwd", base64.b64encode(
            self.ftpPwd.text().strip().encode()).decode("utf8"))
        scctool.settings.config.parser.set(
            "FTP", "dir", self.ftpDir.text().strip())

    def saveOBSdata(self):
        """Save OBS data."""
        scctool.settings.config.parser.set(
            "OBS", "port", self.obsPort.text().strip())
        scctool.settings.config.parser.set("OBS", "passwd", base64.b64encode(
            self.obsPasswd.text().strip().encode()).decode("utf8"))
        scctool.settings.config.parser.set(
            "OBS", "active", str(self.obsActive.isChecked()))
        scctool.settings.config.parser.set(
            "OBS", "sources", self.obsSources.text().strip())

    def saveCloseWindow(self):
        """Save and close window."""
        self.saveData()
        self.passEvent = True
        self.close()

    def closeWindow(self):
        """Close window without save."""
        self.passEvent = True
        self.close()

    def closeEvent(self, event):
        """Handle close event."""
        try:
            if(not self.__dataChanged):
                event.accept()
                return
            if(not self.passEvent):
                if(self.isMinimized()):
                    self.showNormal()
                buttonReply = PyQt5.QtWidgets.QMessageBox.question(
                    self, 'Save data?', "Do you want to save the data?",
                    PyQt5.QtWidgets.QMessageBox.Yes | PyQt5.QtWidgets.QMessageBox.No,
                    PyQt5.QtWidgets.QMessageBox.No)
                if buttonReply == PyQt5.QtWidgets.QMessageBox.Yes:
                    self.saveData()
            event.accept()
        except Exception as e:
            module_logger.exception("message")
