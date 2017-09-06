"""Show connections settings sub window."""
import logging
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from scctool.view.widgets import *

import scctool.settings
import scctool.tasks.obs
import base64

# create logger
module_logger = logging.getLogger('scctool.view.subConnections')


class SubwindowConnections(QWidget):
    """Show connections settings sub window."""

    def createWindow(self, mainWindow):

        try:
            parent = None
            super(SubwindowConnections, self).__init__(parent)
            # self.setWindowFlags(Qt.WindowStaysOnTopHint)

            self.setWindowIcon(
                QIcon(scctool.settings.getAbsPath('src/connection.png')))
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
                              * 0.7, self.sizeHint().height()))
            relativeChange = QPoint(mainWindow.size().width() / 2,
                                    mainWindow.size().height() / 3) -\
                QPoint(self.size().width() / 2, self.size().height() / 3)
            self.move(mainWindow.pos() + relativeChange)

            self.setWindowTitle("Connections")

        except Exception as e:
            module_logger.exception("message")

    def createTabs(self):
        self.tabs = QTabWidget()

        self.createFormGroupFTP()
        self.createFormGroupOBS()
        self.createFormGroupTwitch()
        self.createFormGroupNightbot()

        # Add tabs
        self.tabs.addTab(self.formGroupFTP, "FTP")
        self.tabs.addTab(self.formGroupNightbot, "Nightbot")
        self.tabs.addTab(self.formGroupOBS, "OBS via Websocket Plugin")
        self.tabs.addTab(self.formGroupTwitch, "Twitch")

    def createFormGroupFTP(self):
        self.formGroupFTP = QWidget()
        layout = QFormLayout()

        self.ftpServer = MonitoredLineEdit()
        self.ftpServer.textModified.connect(self.changed)
        self.ftpServer.setText(
            scctool.settings.config.parser.get("FTP", "server").strip())
        self.ftpServer.setAlignment(Qt.AlignCenter)
        self.ftpServer.setPlaceholderText("FTP server address")
        self.ftpServer.setToolTip('')
        layout.addRow(QLabel("Host:"), self.ftpServer)

        self.ftpUser = MonitoredLineEdit()
        self.ftpUser.textModified.connect(self.changed)
        self.ftpUser.setText(
            scctool.settings.config.parser.get("FTP", "user").strip())
        self.ftpUser.setAlignment(Qt.AlignCenter)
        self.ftpUser.setPlaceholderText("FTP username")
        self.ftpUser.setToolTip('')
        layout.addRow(QLabel("Username:"), self.ftpUser)

        self.ftpPwd = MonitoredLineEdit()
        self.ftpPwd.textModified.connect(self.changed)
        self.ftpPwd.setText(base64.b64decode(scctool.settings.config.parser.get(
            "FTP", "passwd").strip().encode()).decode("utf8"))
        self.ftpPwd.setAlignment(Qt.AlignCenter)
        self.ftpPwd.setPlaceholderText("FTP password")
        self.ftpPwd.setToolTip('')
        self.ftpPwd.setEchoMode(QLineEdit.Password)
        label = QLabel("Password:")
        # label.setFixedWidth(100)
        layout.addRow(label, self.ftpPwd)

        self.ftpDir = MonitoredLineEdit()
        self.ftpDir.textModified.connect(self.changed)
        self.ftpDir.setText(
            scctool.settings.config.parser.get("FTP", "dir").strip())
        self.ftpDir.setAlignment(Qt.AlignCenter)
        self.ftpDir.setPlaceholderText("currently using root directory")
        self.ftpDir.setToolTip('')
        layout.addRow(QLabel("Directory:"), self.ftpDir)

        container = QHBoxLayout()
        self.pb_testFTP = QPushButton('Test && Setup FTP server')
        self.pb_testFTP.clicked.connect(self.testFTP)
        container.addWidget(self.pb_testFTP)

        layout.addRow(QLabel(""), container)

        self.formGroupFTP.setLayout(layout)

    def testFTP(self):

        self.saveFtpData()
        window = FTPsetup(self.controller, self)

    def testOBS(self):
        self.saveOBSdata()
        msg = scctool.tasks.obs.testConnection()
        QMessageBox.warning(self, "OBS Websocket Connection Test", msg)

    def createFormGroupOBS(self):
        self.formGroupOBS = QWidget()
        layout = QFormLayout()

        self.obsPort = MonitoredLineEdit()
        self.obsPort.textModified.connect(self.changed)
        self.obsPort.setText(scctool.settings.config.parser.get("OBS", "port"))
        self.obsPort.setAlignment(Qt.AlignCenter)
        self.obsPort.setPlaceholderText("Server Port (Default: 4444)")
        self.obsPort.setToolTip('')
        layout.addRow(QLabel("Server Port:"), self.obsPort)

        self.obsPasswd = MonitoredLineEdit()
        self.obsPasswd.textModified.connect(self.changed)
        self.obsPasswd.setText(base64.b64decode(scctool.settings.config.parser.get(
            "OBS", "passwd").strip().encode()).decode("utf8"))
        self.obsPasswd.setEchoMode(QLineEdit.Password)
        self.obsPasswd.setAlignment(Qt.AlignCenter)
        self.obsPasswd.setPlaceholderText("recommended")
        self.obsPasswd.setToolTip('')
        label = QLabel("Password:")
        # label.setFixedWidth(100)
        layout.addRow(label, self.obsPasswd)

        self.obsSources = MonitoredLineEdit()
        self.obsSources.textModified.connect(self.changed)
        self.obsSources.setText(
            scctool.settings.config.parser.get("OBS", "sources"))
        self.obsSources.setAlignment(Qt.AlignCenter)
        self.obsSources.setPlaceholderText("Intro1, Intro2")
        string = 'Name of the OBS-sources that should automatically' +\
                 ' be hidden 4.5 sec after they become visible.'
        self.obsSources.setToolTip(string)
        layout.addRow(QLabel("Sources:"), self.obsSources)

        self.obsActive = QCheckBox(" Automatic hide sources")
        self.obsActive.setChecked(
            scctool.settings.config.parser.getboolean("OBS", "active"))
        self.obsActive.setToolTip('')
        self.obsActive.stateChanged.connect(self.changed)
        layout.addRow(QLabel("Active:"), self.obsActive)

        self.pb_testOBS = QPushButton('Test Connection to OBS')
        self.pb_testOBS.clicked.connect(self.testOBS)
        layout.addRow(QLabel(), self.pb_testOBS)

        self.formGroupOBS.setLayout(layout)

    def createFormGroupTwitch(self):
        self.formGroupTwitch = QWidget()
        layout = QFormLayout()

        self.twitchChannel = MonitoredLineEdit()
        self.twitchChannel.textModified.connect(self.changed)
        self.twitchChannel.setText(
            scctool.settings.config.parser.get("Twitch", "channel"))
        self.twitchChannel.setAlignment(Qt.AlignCenter)
        self.twitchChannel.setPlaceholderText(
            "Name of the Twitch channel that should be updated")
        self.twitchChannel.setToolTip(
            'The connected twitch user needs to have editor rights for this channel.')
        layout.addRow(QLabel("Twitch-Channel:"), self.twitchChannel)

        container = QHBoxLayout()

        self.twitchToken = MonitoredLineEdit()
        self.twitchToken.textModified.connect(self.changed)
        self.twitchToken.setText(
            scctool.settings.config.parser.get("Twitch", "oauth"))
        self.twitchToken.setAlignment(Qt.AlignCenter)
        self.twitchToken.setPlaceholderText("Press 'Get' to generate a token")
        self.twitchToken.setEchoMode(QLineEdit.Password)
        self.twitchToken.setToolTip("Press 'Get' to generate a new token.")
        container.addWidget(self.twitchToken)

        self.pb_getTwitch = QPushButton('Get')
        self.pb_getTwitch.setFixedWidth(100)
        self.pb_getTwitch.clicked.connect(self.controller.getTwitchToken)
        container.addWidget(self.pb_getTwitch)

        layout.addRow(QLabel("Access-Token:"), container)

        container = QHBoxLayout()

        self.twitchTemplate = MonitoredLineEdit()
        self.twitchTemplate.textModified.connect(self.changed)
        self.twitchTemplate.setText(
            scctool.settings.config.parser.get("Twitch", "title_template"))
        self.twitchTemplate.setAlignment(Qt.AlignCenter)
        self.twitchTemplate.setPlaceholderText("(League) – (Team1) vs (Team2)")
        self.twitchTemplate.setToolTip(
            'Avaiable placeholders: ' + ', '.join(self.controller.placeholders.available()))

        completer = Completer(
            self.controller.placeholders.available(), self.twitchTemplate)

        self.twitchTemplate.setCompleter(completer)

        container.addWidget(self.twitchTemplate)

        button = QPushButton('Test')
        button.setFixedWidth(100)
        button.clicked.connect(
            lambda: self.testPlaceholder(self.twitchTemplate.text()))
        container.addWidget(button)

        label = QLabel("Title Template:")
        label.setFixedWidth(100)
        layout.addRow(label, container)

        self.formGroupTwitch.setLayout(layout)

    def createFormGroupNightbot(self):
        self.formGroupNightbot = QWidget()
        layout = QFormLayout()
        container = QHBoxLayout()

        self.nightbotToken = MonitoredLineEdit()
        self.nightbotToken.textModified.connect(self.changed)
        self.nightbotToken.setText(
            scctool.settings.config.parser.get("NightBot", "token"))
        self.nightbotToken.setAlignment(Qt.AlignCenter)
        self.nightbotToken.setEchoMode(QLineEdit.Password)
        self.nightbotToken.setPlaceholderText(
            "Press 'Get' to generate a token")
        self.nightbotToken.setToolTip("Press 'Get' to generate a new token.")

        self.nightbotCommand = MonitoredLineEdit()
        self.nightbotCommand.textModified.connect(self.changed)
        self.nightbotCommand.setText(
            scctool.settings.config.parser.get("NightBot", "command"))
        self.nightbotCommand.setPlaceholderText("!matchlink")
        self.nightbotCommand.setAlignment(Qt.AlignCenter)

        container.addWidget(self.nightbotToken)
        self.pb_getNightbot = QPushButton('Get')
        self.pb_getNightbot.clicked.connect(self.controller.getNightbotToken)
        self.pb_getNightbot.setFixedWidth(100)
        # self.pb_getNightbot.setEnabled(False)
        container.addWidget(self.pb_getNightbot)

        layout.addRow(QLabel("Access-Token:"), container)
        label = QLabel("Command:")
        label.setFixedWidth(100)
        layout.addRow(label, self.nightbotCommand)

        container = QHBoxLayout()

        self.nightbotMsg = MonitoredLineEdit()
        self.nightbotMsg.textModified.connect(self.changed)
        self.nightbotMsg.setText(
            scctool.settings.config.parser.get("NightBot", "message"))
        self.nightbotMsg.setAlignment(Qt.AlignCenter)
        self.nightbotMsg.setPlaceholderText("(URL)")
        self.nightbotMsg.setToolTip(
            'Avaiable placeholders: ' + ', '.join(self.controller.placeholders.available()))

        completer = Completer(
            self.controller.placeholders.available(), self.nightbotMsg)

        self.nightbotMsg.setCompleter(completer)

        container.addWidget(self.nightbotMsg)
        button = QPushButton('Test')
        button.setFixedWidth(100)
        button.clicked.connect(
            lambda: self.testPlaceholder(self.nightbotMsg.text()))
        container.addWidget(button)

        layout.addRow(QLabel("Message:"), container)

        self.formGroupNightbot.setLayout(layout)

    def createButtonGroup(self):
        try:
            layout = QHBoxLayout()

            layout.addWidget(QLabel(""))

            buttonCancel = QPushButton('Cancel')
            buttonCancel.clicked.connect(self.closeWindow)
            layout.addWidget(buttonCancel)

            buttonSave = QPushButton('Save && Close')
            buttonSave.clicked.connect(self.saveCloseWindow)
            layout.addWidget(buttonSave)

            self.buttonGroup = layout
        except Exception as e:
            module_logger.exception("message")

    def testPlaceholder(self, string):

        string = self.controller.placeholders.replace(string)
        QMessageBox.information(self, "Output:", string)

    def changed(self):
        self.__dataChanged = True

    def saveData(self):
        if(self.__dataChanged):

            self.saveFtpData()

            scctool.settings.config.parser.set(
                "Twitch", "channel", self.twitchChannel.text().strip())
            scctool.settings.config.parser.set(
                "Twitch", "oauth", self.twitchToken.text().strip())
            scctool.settings.config.parser.set(
                "Twitch", "title_template", self.twitchTemplate.text().strip())
            scctool.settings.config.parser.set(
                "NightBot", "token", self.nightbotToken.text().strip())
            scctool.settings.config.parser.set(
                "NightBot", "command", self.nightbotCommand.text().strip())
            scctool.settings.config.parser.set(
                "NightBot", "message", self.nightbotMsg.text().strip())

            self.saveOBSdata()

            self.controller.refreshButtonStatus()

    def saveFtpData(self):
        scctool.settings.config.parser.set(
            "FTP", "server", self.ftpServer.text().strip())
        scctool.settings.config.parser.set(
            "FTP", "user", self.ftpUser.text().strip())
        scctool.settings.config.parser.set("FTP", "passwd", base64.b64encode(
            self.ftpPwd.text().strip().encode()).decode("utf8"))
        scctool.settings.config.parser.set(
            "FTP", "dir", self.ftpDir.text().strip())

    def saveOBSdata(self):
        scctool.settings.config.parser.set(
            "OBS", "port", self.obsPort.text().strip())
        scctool.settings.config.parser.set("OBS", "passwd", base64.b64encode(
            self.obsPasswd.text().strip().encode()).decode("utf8"))
        scctool.settings.config.parser.set(
            "OBS", "active", str(self.obsActive.isChecked()))
        scctool.settings.config.parser.set(
            "OBS", "sources", self.obsSources.text().strip())

    def saveCloseWindow(self):
        self.saveData()
        self.passEvent = True
        self.close()

    def closeWindow(self):
        self.passEvent = True
        self.close()

    def closeEvent(self, event):
        try:
            if(not self.__dataChanged):
                event.accept()
                return
            if(not self.passEvent):
                if(self.isMinimized()):
                    self.showNormal()
                buttonReply = QMessageBox.question(
                    self, 'Save data?', "Do you want to save the data?",
                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if buttonReply == QMessageBox.Yes:
                    self.saveData()
            event.accept()
        except Exception as e:
            module_logger.exception("message")
