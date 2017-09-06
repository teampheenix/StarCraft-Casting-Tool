"""Define the main window."""
import logging
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtQml import *

import scctool.settings
import scctool.settings.config
import scctool.tasks.obs
import shutil
import os
import markdown2

from scctool.view.widgets import *
from scctool.view.subConnections import SubwindowConnections
from scctool.view.subStyles import SubwindowStyles
from scctool.view.subMisc import SubwindowMisc
from scctool.view.subReadme import SubwindowReadme

# create logger
module_logger = logging.getLogger('scctool.view.main')


class MainWindow(QMainWindow):
    def __init__(self, controller, app):
        try:
            super(MainWindow, self).__init__()

            self.trigger = True
            self.controller = controller

            self.createFormMatchDataBox()
            self.createTabs()
            self.createHorizontalGroupBox()
            self.createSC2APIGroupBox()

            self.createMenuBar()

            mainLayout = QVBoxLayout()
            mainLayout.addWidget(self.tabs, 2)
            mainLayout.addWidget(self.fromMatchDataBox, 7)
            mainLayout.addWidget(self.SC2APIGroupBox, 1)
            mainLayout.addWidget(self.horizontalGroupBox, 1)

            self.setWindowTitle("StarCraft Casting Tool " +
                                controller.versionControl.current)

            self.window = QWidget()
            self.window.setLayout(mainLayout)
            self.setCentralWidget(self.window)

            # self.size
            self.statusBar()

            self.progressBar = BusyProgressBar()

            # self.progressBar.setMaximumHeight(20)
            self.progressBar.setMaximumWidth(160)
            self.progressBar.setMinimumWidth(160)
            self.progressBar.setText("FTP Transfer in progress...")
            self.progressBar.setVisible(False)
            self.statusBar().addPermanentWidget(self.progressBar)

            self.app = app
            self.controller.setView(self)
            self.controller.refreshButtonStatus()

            self.processEvents()
            self.settings = QSettings("team pheeniX", "Starcraft Casting Tool")
            self.restoreGeometry(self.settings.value(
                "geometry", self.saveGeometry()))
            self.restoreState(self.settings.value(
                "windowState", self.saveState()))

            self.mysubwindow1 = None
            self.mysubwindow2 = None
            self.mysubwindow3 = None
            self.mysubwindow4 = None

            self.show()
            self.controller.testVersion()
        except Exception as e:
            module_logger.exception("message")

    def showAbout(self):

        html = markdown2.markdown_path(
            scctool.settings.getAbsPath("src/about.md"))
        version = self.controller.versionControl.current

        html = html.replace("%VERSION%", version)
        if(not self.controller.versionControl.isNewAvaiable(False)):
            new_version = "Starcraft Casting Tool is up to date."
        else:
            new_version = self.controller.versionControl.latest.replace(
                "v", "")
            new_version = "The new version {} is available!".format(
                new_version)
        html = html.replace('%NEW_VERSION%', new_version)

        # use self as parent here
        QMessageBox.about(self, "Starcraft Casting Tool - About", html)

    def closeEvent(self, event):
        try:
            try:
                if(self.mysubwindow1 and self.mysubwindow1.isVisible()):
                    self.mysubwindow1.close()
                if(self.mysubwindow2 and self.mysubwindow2.isVisible()):
                    self.mysubwindow2.close()
                if(self.mysubwindow3 and self.mysubwindow3.isVisible()):
                    self.mysubwindow3.close()
                if(self.mysubwindow4 and self.mysubwindow4.isVisible()):
                    self.mysubwindow4.close()
            finally:
                self.settings.setValue("geometry", self.saveGeometry())
                self.settings.setValue("windowState", self.saveState())
                self.controller.cleanUp()
                QMainWindow.closeEvent(self, event)
                # event.accept()
        except Exception as e:
            module_logger.exception("message")

    def createMenuBar(self):
        try:
            menubar = self.menuBar()
            settingsMenu = menubar.addMenu('Settings')
            apiAct = QAction(QIcon(scctool.settings.getAbsPath(
                'src/connection.png')), 'Connections', self)
            apiAct.setToolTip(
                'Edit FTP-Settings and API-Settings for Twitch and Nightbot')
            apiAct.triggered.connect(self.openApiDialog)
            settingsMenu.addAction(apiAct)
            styleAct = QAction(QIcon(scctool.settings.getAbsPath(
                'src/pantone.png')), 'Styles', self)
            styleAct.setToolTip('')
            styleAct.triggered.connect(self.openStyleDialog)
            settingsMenu.addAction(styleAct)
            miscAct = QAction(QIcon(scctool.settings.getAbsPath(
                'src/settings.png')), 'Misc', self)
            miscAct.setToolTip('')
            miscAct.triggered.connect(self.openMiscDialog)
            settingsMenu.addAction(miscAct)

            infoMenu = menubar.addMenu('Info && Links')

            myAct = QAction(QIcon(scctool.settings.getAbsPath(
                'src/about.png')), 'About', self)
            myAct.triggered.connect(self.showAbout)
            infoMenu.addAction(myAct)

            myAct = QAction(QIcon(scctool.settings.getAbsPath(
                'src/readme.ico')), 'Readme', self)
            myAct.triggered.connect(self.openReadme)
            infoMenu.addAction(myAct)

            websiteAct = QAction(QIcon(scctool.settings.getAbsPath('src/github.ico')),
                                 'StarCraft Casting Tool', self)
            websiteAct.triggered.connect(lambda: self.controller.openURL(
                "https://github.com/teampheenix/StarCraft-Casting-Tool"))
            infoMenu.addAction(websiteAct)

            infoMenu.addSeparator()

            ixAct = QAction(QIcon(scctool.settings.getAbsPath(
                'src/icon.png')), 'team pheeniX', self)
            ixAct.triggered.connect(
                lambda:  self.controller.openURL("http://team-pheenix.de"))
            infoMenu.addAction(ixAct)

            alphaAct = QAction(QIcon(scctool.settings.getAbsPath(
                               'src/alphatl.ico')), 'AlphaTL', self)
            alphaAct.triggered.connect(
                lambda: self.controller.openURL("http://alpha.tl"))
            infoMenu.addAction(alphaAct)

            rstlAct = QAction(QIcon(scctool.settings.getAbsPath(
                              'src/rstl.png')), 'RSTL', self)
            rstlAct.triggered.connect(
                lambda: self.controller.openURL("http://hdgame.net/en/"))
            infoMenu.addAction(rstlAct)

            infoMenu.addSeparator()

            myAct = QAction(QIcon(scctool.settings.getAbsPath(
                'src/donate.ico')), 'Donate', self)
            myAct.triggered.connect(lambda: self.controller.openURL(
                "https://streamlabs.com/scpressure"))
            infoMenu.addAction(myAct)

        except Exception as e:
            module_logger.exception("message")

    def openApiDialog(self):
        self.mysubwindow1 = SubwindowConnections()
        self.mysubwindow1.createWindow(self)
        self.mysubwindow1.show()

    def openStyleDialog(self):
        self.mysubwindow2 = SubwindowStyles()
        self.mysubwindow2.createWindow(self)
        self.mysubwindow2.show()

    def openMiscDialog(self):
        self.mysubwindow3 = SubwindowMisc()
        self.mysubwindow3.createWindow(self)
        self.mysubwindow3.show()

    def openReadme(self):
        self.mysubwindow4 = SubwindowReadme()
        self.mysubwindow4.createWindow(self)
        self.mysubwindow4.show()

    def createTabs(self):
        try:
            # Initialize tab screen
            self.tabs = QTabWidget()
            self.tab1 = QWidget()
            self.tab2 = QWidget()
            # self.tabs.resize(300,200)

            # Add tabs
            self.tabs.addTab(self.tab1, "Match Grabber for AlphaTL && RSTL")
            self.tabs.addTab(self.tab2, "Custom Match")

            # Create first tab
            self.tab1.layout = QVBoxLayout()

            self.le_url = QLineEdit()
            self.le_url.setAlignment(Qt.AlignCenter)

            self.le_url.setPlaceholderText("http://alpha.tl/match/2392")

            completer = QCompleter(
                ["http://alpha.tl/match/",
                 "http://hdgame.net/en/tournaments/list/tournament/rstl-12/"], self.le_url)
            completer.setCaseSensitivity(Qt.CaseInsensitive)
            completer.setCompletionMode(QCompleter.UnfilteredPopupCompletion)
            completer.setWrapAround(True)
            self.le_url.setCompleter(completer)
            minWidth = self.scoreWidth + 2 * self.raceWidth + \
                2 * self.mimumLineEditWidth + 4 * 6
            self.le_url.setMinimumWidth(minWidth)

            self.pb_openBrowser = QPushButton("Open in Browser")
            self.pb_openBrowser.clicked.connect(self.openBrowser_click)
            width = (self.scoreWidth + 2 * self.raceWidth + 2 *
                     self.mimumLineEditWidth + 4 * 6) / 2 - 2
            self.pb_openBrowser.setMinimumWidth(width)

            container = QHBoxLayout()
            label = QLabel()
            label.setFixedWidth(self.labelWidth * 2)
            container.addWidget(label, 0)
            label = QLabel("Match-URL:")
            label.setMinimumWidth(80)
            container.addWidget(label, 0)
            container.addWidget(self.le_url, 1)

            self.tab1.layout = QFormLayout()
            self.tab1.layout.addRow(container)

            container = QHBoxLayout()

            # self.pb_download = QPushButton("Download Images from URL")
            # container.addWidget(self.pb_download)
            label = QLabel()
            label.setFixedWidth(self.labelWidth * 2)
            container.addWidget(label, 0)
            label = QLabel()
            label.setMinimumWidth(80)
            container.addWidget(label, 0)
            self.pb_refresh = QPushButton("Load Data from URL")
            self.pb_refresh.clicked.connect(self.refresh_click)
            container.addWidget(self.pb_openBrowser, 3)
            container.addWidget(self.pb_refresh, 3)

            self.tab1.layout.addRow(container)
            self.tab1.setLayout(self.tab1.layout)

            # Create second tab

            self.tab2.layout = QVBoxLayout()

            container = QHBoxLayout()

            label = QLabel()
            label.setMinimumWidth(self.labelWidth * 2)
            container.addWidget(label, 0)

            label = QLabel("Match Format:")
            label.setMinimumWidth(80)
            container.addWidget(label, 0)

            container.addWidget(QLabel("Best of"), 0)

            self.cb_bestof = QComboBox()
            for idx in range(0, scctool.settings.max_no_sets):
                self.cb_bestof.addItem(str(idx + 1))
            self.cb_bestof.setCurrentIndex(3)
            string = '"Best of 6/4": First, a Bo5/3 is played and the ace map gets ' +\
                     'extended to a Bo3 if needed; Best of 2: Bo3 with only two maps played.'
            self.cb_bestof.setToolTip(string)
            self.cb_bestof.setMaximumWidth(40)
            container.addWidget(self.cb_bestof, 0)

            container.addWidget(QLabel(" but at least"), 0)

            self.cb_minSets = QComboBox()
            for idx in range(0, scctool.settings.max_no_sets):
                self.cb_minSets.addItem(str(idx + 1))
            self.cb_minSets.setCurrentIndex(0)

            self.cb_minSets.setToolTip(
                'Minimum number of maps played (even if the match is decided already)')
            self.cb_minSets.setMaximumWidth(50)
            container.addWidget(self.cb_minSets, 0)
            container.addWidget(QLabel(" maps "), 0)

            self.cb_allkill = QCheckBox("All-Kill Format")
            self.cb_allkill.setChecked(False)
            self.cb_allkill.setToolTip(
                'Winner stays and is automatically placed into the next set')
            container.addWidget(self.cb_allkill, 0)

            label = QLabel("")
            container.addWidget(label, 1)

            self.pb_applycustom = QPushButton("Apply Format")
            self.pb_applycustom.clicked.connect(self.applycustom_click)
            self.pb_applycustom.setFixedWidth(150)
            container.addWidget(self.pb_applycustom, 0)

            self.tab2.layout.addLayout(container)

            container = QHBoxLayout()

            label = QLabel()
            label.setMinimumWidth(self.labelWidth * 2)
            container.addWidget(label, 0)

            label = QLabel("Match-URL:")
            label.setMinimumWidth(80)
            container.addWidget(label, 0)

            self.le_url_custom = QLineEdit()
            self.le_url_custom.setAlignment(Qt.AlignCenter)
            self.le_url_custom.setToolTip(
                'Optionally specify the Match-URL, e.g., for NightBot commands')
            self.le_url_custom.setPlaceholderText(
                "Specify the Match-URL of your Custom Match")

            completer = QCompleter(["http://"], self.le_url_custom)
            completer.setCaseSensitivity(Qt.CaseInsensitive)
            completer.setCompletionMode(QCompleter.UnfilteredPopupCompletion)
            completer.setWrapAround(True)
            self.le_url_custom.setCompleter(completer)
            self.le_url_custom.setMinimumWidth(310)

            container.addWidget(self.le_url_custom, 10)

            label = QLabel("")
            container.addWidget(label, 1)

            self.pb_resetdata = QPushButton("Reset Match Data")
            self.pb_resetdata.setFixedWidth(150)
            self.pb_resetdata.clicked.connect(self.resetdata_click)
            container.addWidget(self.pb_resetdata, 0)

            self.tab2.layout.addLayout(container)

            self.tab2.setLayout(self.tab2.layout)

        except Exception as e:
            module_logger.exception("message")

    def updateMapCompleters(self):
        for i in range(self.max_no_sets):
            completer = QCompleter(scctool.settings.maps, self.le_map[i])
            completer.setCaseSensitivity(Qt.CaseInsensitive)
            completer.setCompletionMode(QCompleter.InlineCompletion)
            completer.setWrapAround(True)
            self.le_map[i].setCompleter(completer)

    def createFormMatchDataBox(self):
        try:

            self.max_no_sets = scctool.settings.max_no_sets
            self.scoreWidth = 35
            self.raceWidth = 45
            self.labelWidth = 15
            self.mimumLineEditWidth = 130

            self.fromMatchDataBox = QGroupBox("Match Data")
            layout2 = QVBoxLayout()

            self.le_league = QLineEdit()
            self.le_league.setText("League TBD")
            self.le_league.setAlignment(Qt.AlignCenter)
            self.le_league.setPlaceholderText("League TBD")
            policy = QSizePolicy()
            policy.setHorizontalStretch(3)
            policy.setHorizontalPolicy(QSizePolicy.Expanding)
            policy.setVerticalStretch(1)
            policy.setVerticalPolicy(QSizePolicy.Fixed)
            self.le_league.setSizePolicy(policy)

            self.le_team = [QLineEdit() for y in range(2)]
            self.le_player = [[QLineEdit() for x in range(
                self.max_no_sets)] for y in range(2)]
            self.cb_race = [[QComboBox() for x in range(self.max_no_sets)]
                            for y in range(2)]
            self.sl_score = [QSlider(Qt.Horizontal)
                             for y in range(self.max_no_sets)]
            self.le_map = [MapLineEdit() for y in range(self.max_no_sets)]
            self.label_set = [QLabel() for y in range(self.max_no_sets)]
            self.setContainer = [QHBoxLayout()
                                 for y in range(self.max_no_sets)]

            container = QHBoxLayout()
            for team_idx in range(2):
                self.le_team[team_idx].setText("TBD")
                self.le_team[team_idx].setAlignment(Qt.AlignCenter)
                self.le_team[team_idx].setPlaceholderText(
                    "Team " + str(team_idx + 1))
                completer = QCompleter(
                    scctool.settings.config.getMyTeams() + ["TBD"], self.le_team[team_idx])
                completer.setCaseSensitivity(Qt.CaseInsensitive)
                completer.setCompletionMode(QCompleter.InlineCompletion)
                completer.setWrapAround(True)
                self.le_team[team_idx].setCompleter(completer)
                policy = QSizePolicy()
                policy.setHorizontalStretch(4)
                policy.setHorizontalPolicy(QSizePolicy.Expanding)
                policy.setVerticalStretch(1)
                policy.setVerticalPolicy(QSizePolicy.Fixed)
                self.le_team[team_idx].setSizePolicy(policy)
                self.le_team[team_idx].setMinimumWidth(self.mimumLineEditWidth)

            self.qb_logo1 = IconPushButton()
            self.qb_logo1.setFixedWidth(self.raceWidth)
            self.qb_logo1.clicked.connect(lambda: self.logoDialog(1))
            pixmap = QIcon(self.controller.linkFile(
                scctool.settings.OBSdataDir + '/logo1'))
            self.qb_logo1.setIcon(pixmap)

            self.qb_logo2 = IconPushButton()
            self.qb_logo2.setFixedWidth(self.raceWidth)
            self.qb_logo2.clicked.connect(lambda: self.logoDialog(2))
            pixmap = QIcon(self.controller.linkFile(
                scctool.settings.OBSdataDir + '/logo2'))
            self.qb_logo2.setIcon(pixmap)

            self.sl_team = QSlider(Qt.Horizontal)
            self.sl_team.setMinimum(-1)
            self.sl_team.setMaximum(1)
            self.sl_team.setValue(0)
            self.sl_team.setTickPosition(QSlider.TicksBothSides)
            self.sl_team.setTickInterval(1)
            self.sl_team.valueChanged.connect(self.sl_changed)
            self.sl_team.setToolTip('Choose your team')
            self.sl_team.setMinimumHeight(5)
            self.sl_team.setFixedWidth(self.scoreWidth)
            policy = QSizePolicy()
            policy.setHorizontalStretch(0)
            policy.setHorizontalPolicy(QSizePolicy.Fixed)
            policy.setVerticalStretch(1)
            policy.setVerticalPolicy(QSizePolicy.Fixed)
            self.sl_team.setSizePolicy(policy)

            container = QGridLayout()

            label = QLabel("")
            label.setFixedWidth(self.labelWidth)
            container.addWidget(label, 0, 0, 2, 1)

            label = QLabel("League:")
            label.setAlignment(Qt.AlignCenter)
            policy = QSizePolicy()
            policy.setHorizontalStretch(4)
            policy.setHorizontalPolicy(QSizePolicy.Expanding)
            policy.setVerticalStretch(1)
            policy.setVerticalPolicy(QSizePolicy.Fixed)
            label.setSizePolicy(policy)
            container.addWidget(label, 0, 1, 1, 1)

            label = QLabel("Maps \ Teams:")
            label.setAlignment(Qt.AlignCenter)
            policy = QSizePolicy()
            policy.setHorizontalStretch(4)
            policy.setHorizontalPolicy(QSizePolicy.Expanding)
            policy.setVerticalStretch(1)
            policy.setVerticalPolicy(QSizePolicy.Fixed)
            label.setSizePolicy(policy)
            container.addWidget(label, 1, 1, 1, 1)

            container.addWidget(self.qb_logo1, 0, 2, 2, 1)
            container.addWidget(self.le_league, 0, 3, 1, 3)
            container.addWidget(self.le_team[0], 1, 3, 1, 1)
            container.addWidget(self.sl_team, 1, 4, 1, 1)
            container.addWidget(self.le_team[1], 1, 5, 1, 1)
            container.addWidget(self.qb_logo2, 0, 6, 2, 1)

            layout2.addLayout(container)

            for player_idx in range(self.max_no_sets):
                for team_idx in range(2):
                    self.le_player[team_idx][player_idx].setText("TBD")
                    self.le_player[team_idx][player_idx].setAlignment(
                        Qt.AlignCenter)
                    self.le_player[team_idx][player_idx].setPlaceholderText(
                        "Player " + str(player_idx + 1) + " of Team " + str(team_idx + 1))
                    completer = QCompleter(scctool.settings.config.getMyPlayers(
                        True), self.le_player[team_idx][player_idx])
                    completer.setCaseSensitivity(Qt.CaseInsensitive)
                    completer.setCompletionMode(QCompleter.InlineCompletion)
                    completer.setWrapAround(True)
                    self.le_player[team_idx][player_idx].setCompleter(
                        completer)
                    self.le_player[team_idx][player_idx].setMinimumWidth(
                        self.mimumLineEditWidth)

                    for i in range(4):
                        self.cb_race[team_idx][player_idx].addItem(
                            QIcon("src/" + str(i) + ".png"), "")

                    self.cb_race[team_idx][player_idx].setFixedWidth(
                        self.raceWidth)

                self.sl_score[player_idx].setMinimum(-1)
                self.sl_score[player_idx].setMaximum(1)
                self.sl_score[player_idx].setValue(0)
                self.sl_score[player_idx].setTickPosition(
                    QSlider.TicksBothSides)
                self.sl_score[player_idx].setTickInterval(1)
                self.sl_score[player_idx].valueChanged.connect(self.sl_changed)
                self.sl_score[player_idx].setToolTip('Set the score')
                self.sl_score[player_idx].setFixedWidth(self.scoreWidth)

                self.le_map[player_idx].setText("TBD")
                self.le_map[player_idx].setAlignment(Qt.AlignCenter)
                self.le_map[player_idx].setPlaceholderText(
                    "Map " + str(player_idx + 1))
                self.le_map[player_idx].setMinimumWidth(
                    self.mimumLineEditWidth)

                # self.le_map[player_idx].setReadOnly(True)

                self.setContainer[player_idx] = QHBoxLayout()
                self.label_set[player_idx].setText("#" + str(player_idx + 1))
                self.label_set[player_idx].setAlignment(Qt.AlignCenter)
                self.label_set[player_idx].setFixedWidth(self.labelWidth)
                self.setContainer[player_idx].addWidget(
                    self.label_set[player_idx], 0)
                self.setContainer[player_idx].addWidget(
                    self.le_map[player_idx], 4)
                self.setContainer[player_idx].addWidget(
                    self.cb_race[0][player_idx], 0)
                self.setContainer[player_idx].addWidget(
                    self.le_player[0][player_idx], 4)
                self.setContainer[player_idx].addWidget(
                    self.sl_score[player_idx], 0)
                self.setContainer[player_idx].addWidget(
                    self.le_player[1][player_idx], 4)
                self.setContainer[player_idx].addWidget(
                    self.cb_race[1][player_idx], 0)
                layout2.addLayout(self.setContainer[player_idx])

            layout2.addItem(QSpacerItem(
                0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))
            self.fromMatchDataBox.setLayout(layout2)

            self.updateMapCompleters()

        except Exception as e:
            module_logger.exception("message")

    def createHorizontalGroupBox(self):
        try:
            self.horizontalGroupBox = QGroupBox("Tasks")
            layout = QHBoxLayout()

            self.pb_twitchupdate = QPushButton("Update Twitch Title")
            self.pb_twitchupdate.clicked.connect(self.updatetwitch_click)

            self.pb_nightbotupdate = QPushButton("Update NightBot")
            self.pb_nightbotupdate.clicked.connect(self.updatenightbot_click)

            self.pb_resetscore = QPushButton("Reset Score")
            self.pb_resetscore.clicked.connect(self.resetscore_click)

            self.pb_obsupdate = QPushButton("Update OBS Data")
            self.pb_obsupdate.clicked.connect(self.updateobs_click)

            layout.addWidget(self.pb_twitchupdate)
            layout.addWidget(self.pb_nightbotupdate)
            layout.addWidget(self.pb_resetscore)
            layout.addWidget(self.pb_obsupdate)

            self.horizontalGroupBox.setLayout(layout)
        except Exception as e:
            module_logger.exception("message")

    def createSC2APIGroupBox(self):
        try:
            self.SC2APIGroupBox = QGroupBox("Automatic Background Tasks")
            layout = QHBoxLayout()

            self.cb_autoFTP = QCheckBox("FTP Upload")
            self.cb_autoFTP.setChecked(False)
            string = 'Automatically uploads all streaming data' +\
                     ' in the background to a specified FTP server.'
            self.cb_autoFTP.setToolTip(string)
            self.cb_autoFTP.stateChanged.connect(self.autoFTP_change)

            self.cb_autoUpdate = QCheckBox("Score Update")
            self.cb_autoUpdate.setChecked(False)
            string = 'Automatically detects the outcome of SC2 matches that are ' + \
                     'played/observed in your SC2-client and updates the score accordingly.'
            self.cb_autoUpdate.setToolTip(string)
            self.cb_autoUpdate.stateChanged.connect(self.autoUpdate_change)

            self.cb_playerIntros = QCheckBox("Player Intros")
            self.cb_playerIntros.setChecked(False)
            self.cb_playerIntros.setToolTip(
                'Update player intros files via SC2-Client-API')
            self.cb_playerIntros.stateChanged.connect(self.playerIntros_change)

            self.cb_autoToggleScore = QCheckBox("Ingame Score")
            self.cb_autoToggleScore.setChecked(False)
            string = 'Automatically sets the score of your ingame' +\
                     ' UI-interface at the begining of a game.'
            self.cb_autoToggleScore.setToolTip(string)
            self.cb_autoToggleScore.stateChanged.connect(
                self.autoToggleScore_change)

            self.cb_autoToggleProduction = QCheckBox("Production Tab")
            self.cb_autoToggleProduction.setChecked(False)
            string = 'Automatically toggles the production tab of your' + \
                     ' ingame UI-interface at the begining of a game.'
            self.cb_autoToggleProduction.setToolTip(string)
            self.cb_autoToggleProduction.stateChanged.connect(
                self.autoToggleProduction_change)

            if(not scctool.settings.windows):
                self.cb_autoToggleScore.setEnabled(False)
                self.cb_autoToggleScore.setAttribute(Qt.WA_AlwaysShowToolTips)
                self.cb_autoToggleScore.setToolTip('Only Windows')
                self.cb_autoToggleProduction.setEnabled(False)
                self.cb_autoToggleProduction.setAttribute(
                    Qt.WA_AlwaysShowToolTips)
                self.cb_autoToggleProduction.setToolTip('Only Windows')

            layout.addWidget(self.cb_autoFTP, 3)
            layout.addWidget(self.cb_autoUpdate, 3)
            layout.addWidget(self.cb_playerIntros, 3)
            layout.addWidget(self.cb_autoToggleScore, 3)
            layout.addWidget(self.cb_autoToggleProduction, 3)

            self.SC2APIGroupBox.setLayout(layout)
        except Exception as e:
            module_logger.exception("message")

    def autoFTP_change(self):
        try:
            scctool.settings.config.parser.set(
                "FTP", "upload", str(self.cb_autoFTP.isChecked()))
            if(self.cb_autoFTP.isChecked()):
                signal = self.controller.ftpUploader.connect()
                signal.connect(self.ftpSignal)
                self.controller.matchData.allChanged()
            else:
                self.controller.ftpUploader.disconnect()
        except Exception as e:
            module_logger.exception("message")

    def ftpSignal(self, signal):

        if(signal == -2):
            QMessageBox.warning(self, "Login error",
                                'FTP server login incorrect!')
            self.cb_autoFTP.setChecked(False)
        elif(signal == -3):
            self.progressBar.setVisible(False)
        else:
            self.progressBar.setVisible(True)

    def autoUpdate_change(self):
        try:
            if(self.cb_autoUpdate.isChecked()):
                self.controller.runSC2ApiThread("updateScore")
            else:
                self.controller.stopSC2ApiThread("updateScore")
        except Exception as e:
            module_logger.exception("message")

    def playerIntros_change(self):
        try:
            if(self.cb_playerIntros.isChecked()):
                self.controller.runSC2ApiThread("playerIntros")
                self.controller.runWebsocketThread()
            else:
                self.controller.stopSC2ApiThread("playerIntros")
                self.controller.stopWebsocketThread()
        except Exception as e:
            module_logger.exception("message")

    def autoToggleScore_change(self):
        try:
            if(self.cb_autoToggleScore.isChecked()):
                self.controller.runSC2ApiThread("toggleScore")
            else:
                self.controller.stopSC2ApiThread("toggleScore")
        except Exception as e:
            module_logger.exception("message")

    def autoToggleProduction_change(self):
        try:
            if(self.cb_autoToggleProduction.isChecked()):
                self.controller.runSC2ApiThread("toggleProduction")
            else:
                self.controller.stopSC2ApiThread("toggleProduction")
        except Exception as e:
            module_logger.exception("message")

    def applycustom_click(self):
        try:
            url = self.le_url.text()
            self.trigger = False
            self.statusBar().showMessage('Applying Custom Match...')
            msg = self.controller.applyCustom(int(self.cb_bestof.currentText()),
                                              self.cb_allkill.isChecked(),
                                              int(self.cb_minSets.currentText()),
                                              self.le_url_custom.text().strip())
            self.statusBar().showMessage(msg)
            self.trigger = True
        except Exception as e:
            module_logger.exception("message")

    def resetdata_click(self):
        try:
            self.trigger = False
            msg = self.controller.resetData()
            self.statusBar().showMessage(msg)
            self.trigger = True
        except Exception as e:
            module_logger.exception("message")

    def refresh_click(self):
        try:
            url = self.le_url.text()
            self.trigger = False
            self.statusBar().showMessage('Reading ' + url + '...')
            msg = self.controller.refreshData(url)
            self.statusBar().showMessage(msg)
            self.trigger = True
        except Exception as e:
            module_logger.exception("message")

    def openBrowser_click(self):
        try:
            url = self.le_url.text()
            self.controller.openURL(url)
        except Exception as e:
            module_logger.exception("message")

    def updatenightbot_click(self):
        try:
            self.statusBar().showMessage('Updating NightBot Command...')
            msg = self.controller.updateNightbotCommand()
            self.statusBar().showMessage(msg)
        except Exception as e:
            module_logger.exception("message")

    def updatetwitch_click(self):
        try:
            url = self.le_url.text()
            self.statusBar().showMessage('Updating Twitch Title...')
            msg = self.controller.updateTwitchTitle()
            self.statusBar().showMessage(msg)
        except Exception as e:
            module_logger.exception("message")

    def updateobs_click(self):
        try:
            url = self.le_url.text()
            self.statusBar().showMessage('Updating OBS Data...')
            self.controller.updateOBS()
            if not self.controller.resetWarning():
                self.statusBar().showMessage('')
        except Exception as e:
            module_logger.exception("message")

    def resetscore_click(self):
        try:
            self.statusBar().showMessage('Resetting Score...')
            self.trigger = False
            for player_idx in range(self.max_no_sets):
                self.sl_score[player_idx].setValue(0)
            self.controller.updateOBS()
            if not self.controller.resetWarning():
                self.statusBar().showMessage('')
            self.trigger = True
        except Exception as e:
            module_logger.exception("message")

    def setScore(self, idx, score):
        try:
            if(self.sl_score[idx].value() == 0):
                self.statusBar().showMessage('Updating Score...')
                self.trigger = False
                self.sl_score[idx].setValue(score)
                self.controller.updateOBS()
                if not self.controller.resetWarning():
                    self.statusBar().showMessage('')
                self.trigger = True
                return True
            else:
                return False
        except Exception as e:
            module_logger.exception("message")

    def sl_changed(self):
        try:
            if(self.trigger):
                self.controller.allkillUpdate()
                self.controller.updateOBS()
        except Exception as e:
            module_logger.exception("message")

    def logoDialog(self, button):

        # options = QFileDialog.Options()
        # options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(
            self, "Select Team Logo", "", "Support Images (*.png *.jpg)")
        if fileName:
            try:
                os.remove(scctool.settings.OBSdataDir +
                          "/logo" + str(button) + ".png")
            except:
                pass
            try:
                os.remove(scctool.settings.OBSdataDir +
                          "/logo" + str(button) + ".jpg")
            except:
                pass

            base, ext = os.path.splitext(fileName)
            ext = ext.split("?")[0]
            fname = scctool.settings.OBSdataDir + "/logo" + str(button) + ext

            shutil.copy(fileName, fname)
            self.controller.updateLogos()
            self.controller.ftpUploader.cwd(scctool.settings.OBSdataDir)
            self.controller.ftpUploader.upload(
                fname, "logo" + str(button) + ext)
            self.controller.ftpUploader.cwd("..")
            self.controller.matchData.metaChanged()
            self.controller.matchData.updateScoreIcon()

    def resizeWindow(self):
        if(not self.isMaximized()):
            self.processEvents()
            self.resize(self.width(), self.sizeHint().height())

    def processEvents(self):
        for i in range(0, 10):
            self.app.processEvents()
