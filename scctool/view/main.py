"""Define the main window."""
import gettext
import logging

import markdown2
from PyQt5.QtCore import QLocale, QSettings, Qt, QTranslator
from PyQt5.QtGui import QIcon, QKeySequence, QPalette
from PyQt5.QtWidgets import (QAction, QApplication, QCheckBox, QComboBox,
                             QCompleter, QFormLayout, QGridLayout, QGroupBox,
                             QHBoxLayout, QLabel, QLineEdit, QMainWindow,
                             QMenu, QMessageBox, QPushButton, QShortcut,
                             QSizePolicy, QSlider, QSpacerItem, QTabWidget,
                             QToolButton, QVBoxLayout, QWidget)

import scctool.settings
import scctool.settings.config
from scctool.view.subConnections import SubwindowConnections
from scctool.view.subLogos import SubwindowLogos
from scctool.view.subMarkdown import SubwindowMarkdown
from scctool.view.subMisc import SubwindowMisc
from scctool.view.subStyles import SubwindowStyles
from scctool.view.widgets import (BusyProgressBar, IconPushButton, MapLineEdit,
                                  MonitoredLineEdit)

# create logger
module_logger = logging.getLogger('scctool.view.main')


class MainWindow(QMainWindow):
    """Show the main window of SCCT."""

    EXIT_CODE_REBOOT = -123

    def __init__(self, controller, app, translator, showChangelog):
        """Init the main window."""
        try:
            super().__init__()

            self.tlock = TriggerLock()
            self.controller = controller
            self.translator = translator

            with self.tlock:
                self.createFormMatchDataBox()
            self.createTabs()
            self.createHorizontalGroupBox()
            self.createBackgroundTasksBox()

            self.createMenuBar()

            mainLayout = QVBoxLayout()
            mainLayout.addWidget(self.tabs, 0)
            mainLayout.addWidget(self.fromMatchDataBox, 1)
            mainLayout.addWidget(self.backgroundTasksBox, 0)
            mainLayout.addWidget(self.horizontalGroupBox, 0)

            self.setWindowTitle(
                "StarCraft Casting Tool v{}".format(scctool.__version__))

            self.window = QWidget()
            self.window.setLayout(mainLayout)
            self.setCentralWidget(self.window)

            # self.size
            self.statusBar()

            self.progressBar = BusyProgressBar()

            # self.progressBar.setMaximumHeight(20)
            self.progressBar.setMaximumWidth(160)
            self.progressBar.setMinimumWidth(160)
            self.progressBar.setVisible(False)
            self.progressBar.setText("")
            self.statusBar().addPermanentWidget(self.progressBar)

            self.app = app
            self.controller.setView(self)
            self.controller.refreshButtonStatus()

            self.processEvents()
            self.settings = QSettings(
                "team pheeniX", "StarCraft Casting Tool")
            self.restoreGeometry(self.settings.value(
                "geometry", self.saveGeometry()))
            self.restoreState(self.settings.value(
                "windowState", self.saveState()))

            self.mysubwindows = dict()

            self.show()

            if showChangelog:
                self.openChangelog()

        except Exception as e:
            module_logger.exception("message")

    def showAbout(self):
        """Show subwindow with about info."""
        html = markdown2.markdown_path(
            scctool.settings.getAbsPath("src/about.md"))

        html = html.replace("%VERSION%", scctool.__version__)
        if(not scctool.__new_version__):
            new_version = _("StarCraft Casting Tool is up to date.")
        else:
            new_version = _("The new version {} is available!").format(
                scctool.__latest_version__)
        html = html.replace('%NEW_VERSION%', new_version)

        # use self as parent here
        QMessageBox.about(
            self, _("StarCraft Casting Tool - About"), html)

    def closeEvent(self, event):
        """Close and clean up window."""
        try:
            try:
                for name, window in self.mysubwindows.items():
                    if(window and window.isVisible()):
                        window.close()
            finally:
                self.settings.setValue("geometry", self.saveGeometry())
                self.settings.setValue("windowState", self.saveState())
                self.controller.cleanUp()
                QMainWindow.closeEvent(self, event)
                # event.accept()
        except Exception as e:
            module_logger.exception("message")

    def createMenuBar(self):
        """Create the menu bar."""
        try:
            menubar = self.menuBar()
            settingsMenu = menubar.addMenu(_('Settings'))
            apiAct = QAction(QIcon(scctool.settings.getAbsPath(
                'src/connection.png')), _('Connections'), self)
            apiAct.setToolTip(
                _('Edit Intro-Settings and API-Settings for Twitch and Nightbot'))
            apiAct.triggered.connect(self.openApiDialog)
            settingsMenu.addAction(apiAct)
            styleAct = QAction(QIcon(scctool.settings.getAbsPath(
                'src/pantone.png')), _('Styles'), self)
            styleAct.setToolTip('')
            styleAct.triggered.connect(self.openStyleDialog)
            settingsMenu.addAction(styleAct)
            miscAct = QAction(QIcon(scctool.settings.getAbsPath(
                'src/settings.png')), _('Misc'), self)
            miscAct.setToolTip('')
            miscAct.triggered.connect(self.openMiscDialog)
            settingsMenu.addAction(miscAct)

            infoMenu = menubar.addMenu(_('Info && Links'))

            myAct = QAction(QIcon(scctool.settings.getAbsPath(
                'src/about.png')), _('About'), self)
            myAct.triggered.connect(self.showAbout)
            infoMenu.addAction(myAct)

            myAct = QAction(QIcon(scctool.settings.getAbsPath(
                'src/readme.ico')), _('Readme'), self)
            myAct.triggered.connect(self.openReadme)
            infoMenu.addAction(myAct)

            myAct = QAction(QIcon(scctool.settings.getAbsPath(
                'src/update.png')), _('Check for new version'), self)
            myAct.triggered.connect(lambda: self.controller.checkVersion(True))
            infoMenu.addAction(myAct)

            myAct = QAction(QIcon(scctool.settings.getAbsPath(
                'src/changelog.png')), _('Changelog'), self)
            myAct.triggered.connect(self.openChangelog)
            infoMenu.addAction(myAct)

            infoMenu.addSeparator()

            websiteAct = QAction(
                QIcon(
                    scctool.settings.getAbsPath('src/scct.ico')),
                'StarCraft Casting Tool', self)
            websiteAct.triggered.connect(lambda: self.controller.openURL(
                "https://teampheenix.github.io/StarCraft-Casting-Tool/"))
            infoMenu.addAction(websiteAct)

            discordAct = QAction(
                QIcon(
                    scctool.settings.getAbsPath('src/discord.png')),
                'Discord', self)
            discordAct.triggered.connect(lambda: self.controller.openURL(
                "https://discord.gg/G9hFEfh"))
            infoMenu.addAction(discordAct)

            ixAct = QAction(QIcon(scctool.settings.getAbsPath(
                'src/icon.png')), 'team pheeniX', self)
            ixAct.triggered.connect(
                lambda:  self.controller.openURL("http://team-pheenix.de"))
            infoMenu.addAction(ixAct)

            alphaAct = QAction(QIcon(scctool.settings.getAbsPath(
                'src/alpha.png')), 'AlphaTL', self)
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
                'src/donate.ico')), _('Donate'), self)
            myAct.triggered.connect(lambda: self.controller.openURL(
                "https://streamlabs.com/scpressure"))
            infoMenu.addAction(myAct)

            langMenu = menubar.addMenu(_('Language'))

            language = scctool.settings.config.parser.get("SCT", "language")

            myAct = QAction(QIcon(scctool.settings.getAbsPath(
                'src/de.png')), 'Deutsch', self, checkable=True)
            myAct.setChecked(language == 'de_DE')
            myAct.triggered.connect(lambda: self.changeLanguage('de_DE'))
            langMenu.addAction(myAct)

            myAct = QAction(QIcon(scctool.settings.getAbsPath(
                'src/en.png')), 'English', self, checkable=True)
            myAct.setChecked(language == 'en_US')
            myAct.triggered.connect(lambda: self.changeLanguage('en_US'))
            langMenu.addAction(myAct)

            myAct = QAction(QIcon(scctool.settings.getAbsPath(
                'src/fr.png')), 'Français', self, checkable=True)
            myAct.setChecked(language == 'fr_FR')
            myAct.triggered.connect(lambda: self.changeLanguage('fr_FR'))
            langMenu.addAction(myAct)

            myAct = QAction(QIcon(scctool.settings.getAbsPath(
                'src/ru.png')), 'Pусский', self, checkable=True)
            myAct.setChecked(language == 'ru_RU')
            myAct.triggered.connect(lambda: self.changeLanguage('ru_RU'))
            langMenu.addAction(myAct)

        except Exception as e:
            module_logger.exception("message")

    def openApiDialog(self):
        """Open subwindow with connection settings."""
        self.mysubwindows['connections'] = SubwindowConnections()
        self.mysubwindows['connections'].createWindow(self)
        self.mysubwindows['connections'].show()

    def openStyleDialog(self):
        """Open subwindow with style settings."""
        self.mysubwindows['styles'] = SubwindowStyles()
        self.mysubwindows['styles'].createWindow(self)
        self.mysubwindows['styles'].show()

    def openMiscDialog(self):
        """Open subwindow with misc settings."""
        self.mysubwindows['misc'] = SubwindowMisc()
        self.mysubwindows['misc'].createWindow(self)
        self.mysubwindows['misc'].show()

    def openReadme(self):
        """Open subwindow with readme viewer."""
        self.mysubwindows['readme'] = SubwindowMarkdown()
        self.mysubwindows['readme'].createWindow(
            self, _("Readme"), "src/readme.ico", "README.md")
        self.mysubwindows['readme'].show()

    def openChangelog(self):
        """Open subwindow with readme viewer."""
        self.mysubwindows['changelog'] = SubwindowMarkdown()
        self.mysubwindows['changelog'].createWindow(
            self, "StarCraft Casting Tool " + _("Changelog"),
            "src/changelog.png", "CHANGELOG.md")
        self.mysubwindows['changelog'].show()

    def changeLanguage(self, language):
        """Change the language."""
        try:
            lang = gettext.translation(
                'messages', localedir='locales', languages=[language])
            lang.install()
        except Exception:
            lang = gettext.NullTranslations()

        self.app.removeTranslator(self.translator)
        self.translator = QTranslator(self.app)
        self.translator.load(QLocale(language),
                             "qtbase", "_",  scctool.settings.getAbsPath('locales'), ".qm")
        self.app.installTranslator(self.translator)

        scctool.settings.config.parser.set("SCT", "language", language)
        self.restart()

    def createTabs(self):
        """Create tabs in main window."""
        try:
            # Initialize tab screen
            self.tabs = QTabWidget()
            self.tab1 = QWidget()
            self.tab2 = QWidget()
            # self.tabs.resize(300,200)

            # Add tabs
            self.tabs.addTab(self.tab1, _("Match Grabber for AlphaTL && RSTL"))
            self.tabs.addTab(self.tab2, _("Custom Match"))

            # Create first tab
            self.tab1.layout = QVBoxLayout()

            self.le_url = QLineEdit()
            self.le_url.setAlignment(Qt.AlignCenter)

            self.le_url.setPlaceholderText("http://alpha.tl/match/3000")
            self.le_url.returnPressed.connect(self.refresh_click)

            completer = QCompleter(
                ["http://alpha.tl/match/",
                 "http://hdgame.net/en/tournaments/list/tournament/rstl-13/"], self.le_url)
            completer.setCaseSensitivity(Qt.CaseInsensitive)
            completer.setCompletionMode(
                QCompleter.UnfilteredPopupCompletion)
            completer.setWrapAround(True)
            self.le_url.setCompleter(completer)
            minWidth = self.scoreWidth + 2 * self.raceWidth + \
                2 * self.mimumLineEditWidth + 4 * 6
            self.le_url.setMinimumWidth(minWidth)

            self.pb_openBrowser = QPushButton(
                _("Open in Browser"))
            self.pb_openBrowser.clicked.connect(self.openBrowser_click)
            width = (self.scoreWidth + 2 * self.raceWidth + 2 *
                     self.mimumLineEditWidth + 4 * 6) / 2 - 2
            self.pb_openBrowser.setMinimumWidth(width)

            container = QHBoxLayout()
            label = QLabel()
            label.setFixedWidth(self.labelWidth)
            container.addWidget(label, 0)
            label = QLabel(_("Match-URL:"))
            label.setMinimumWidth(80)
            container.addWidget(label, 0)
            container.addWidget(self.le_url, 1)
            button = QPushButton()
            pixmap = QIcon(
                scctool.settings.getAbsPath('src/alpha.png'))
            button.setIcon(pixmap)
            button.clicked.connect(
                lambda: self.controller.openURL("http://alpha.tl/"))
            container.addWidget(button, 0)
            button = QPushButton()
            pixmap = QIcon(
                scctool.settings.getAbsPath('src/rstl.png'))
            button.setIcon(pixmap)
            button.clicked.connect(
                lambda: self.controller.openURL("http://hdgame.net/en/"))
            container.addWidget(button, 0)

            self.tab1.layout = QFormLayout()
            self.tab1.layout.addRow(container)

            container = QHBoxLayout()

            # self.pb_download = QPushButton("Download Images from URL")
            # container.addWidget(self.pb_download)
            label = QLabel()
            label.setFixedWidth(self.labelWidth)
            container.addWidget(label, 0)
            label = QLabel()
            label.setMinimumWidth(80)
            container.addWidget(label, 0)
            self.pb_refresh = QPushButton(
                _("Load Data from URL"))
            self.pb_refresh.clicked.connect(self.refresh_click)
            container.addWidget(self.pb_openBrowser, 3)
            container.addWidget(self.pb_refresh, 3)

            self.tab1.layout.addRow(container)
            self.tab1.setLayout(self.tab1.layout)

            # Create second tab

            self.tab2.layout = QVBoxLayout()

            container = QHBoxLayout()

            label = QLabel()
            label.setMinimumWidth(self.labelWidth)
            container.addWidget(label, 0)

            label = QLabel(_("Match Format:"))
            label.setMinimumWidth(80)
            container.addWidget(label, 0)

            container.addWidget(QLabel(_("Best of")), 0)

            self.cb_bestof = QComboBox()
            for idx in range(0, scctool.settings.max_no_sets):
                self.cb_bestof.addItem(str(idx + 1))
            self.cb_bestof.setCurrentIndex(3)
            string = _('"Best of 6/4": First, a Bo5/3 is played and the ace map ' +
                       'gets extended to a Bo3 if needed; Best of 2: Bo3 with ' +
                       'only two maps played.')
            self.cb_bestof.setToolTip(string)
            self.cb_bestof.setMaximumWidth(40)
            self.cb_bestof.currentIndexChanged.connect(self.changeBestOf)
            container.addWidget(self.cb_bestof, 0)

            container.addWidget(QLabel(_(" but at least")), 0)

            self.cb_minSets = QComboBox()

            self.cb_minSets.setToolTip(
                _('Minimum number of maps played (even if the match is decided already)'))
            self.cb_minSets.setMaximumWidth(40)
            container.addWidget(self.cb_minSets, 0)
            container.addWidget(
                QLabel(" " + _("maps") + "  "), 0)
            self.cb_minSets.currentIndexChanged.connect(
                lambda idx: self.highlightApplyCustom())

            self.cb_allkill = QCheckBox(_("All-Kill Format"))
            self.cb_allkill.setChecked(False)
            self.cb_allkill.setToolTip(
                _('Winner stays and is automatically placed into the next set'))
            self.cb_allkill.stateChanged.connect(self.allkill_change)
            container.addWidget(self.cb_allkill, 0)

            self.cb_solo = QCheckBox(_("1vs1"))
            self.cb_solo.setChecked(False)
            self.cb_solo.setToolTip(
                _('Select for solo (non-team matches)'))
            container.addWidget(self.cb_solo, 0)
            self.cb_solo.stateChanged.connect(
                lambda idx: self.highlightApplyCustom())

            label = QLabel("")
            container.addWidget(label, 1)

            self.applycustom_is_highlighted = False

            # act = QAction(QIcon(scctool.settings.getAbsPath(
            #    'src/connection.png')), _('Connections'), self)
            # act.setToolTip(
            #    _('Edit Intro-Settings and API-Settings for Twitch and Nightbot'))
            # act.triggered.connect(self.openApiDialog)

            self.pb_applycustom = QToolButton()
            action = QAction(_("Apply Format"))
            action.triggered.connect(self.applycustom_click)
            self.pb_applycustom.setDefaultAction(action)
            self.custom_menu = QMenu(self.pb_applycustom)
            for format in self.controller.matchData.getCustomFormats():
                action = self.custom_menu.addAction(format)
                action.triggered.connect(
                    lambda x, format=format: self.applyCustomFormat(format))
            self.pb_applycustom.setMenu(self.custom_menu)
            self.pb_applycustom.setPopupMode(QToolButton.MenuButtonPopup)

            self.pb_applycustom.setFixedWidth(150)
            container.addWidget(self.pb_applycustom, 0)

            self.tab2.layout.addLayout(container)

            container = QHBoxLayout()

            label = QLabel()
            label.setMinimumWidth(self.labelWidth)
            container.addWidget(label, 0)

            label = QLabel(_("Match-URL:"))
            label.setMinimumWidth(80)
            container.addWidget(label, 0)

            self.le_url_custom = MonitoredLineEdit()
            self.le_url_custom.setAlignment(Qt.AlignCenter)
            self.le_url_custom.setToolTip(
                _('Optionally specify the Match-URL, e.g., for Nightbot commands'))
            self.le_url_custom.setPlaceholderText(
                _("Specify the Match-URL of your Custom Match"))

            completer = QCompleter(
                ["http://"], self.le_url_custom)
            completer.setCaseSensitivity(Qt.CaseInsensitive)
            completer.setCompletionMode(
                QCompleter.UnfilteredPopupCompletion)
            completer.setWrapAround(True)
            self.le_url_custom.setCompleter(completer)
            self.le_url_custom.setMinimumWidth(360)
            self.le_url_custom.textModified.connect(self.highlightApplyCustom)

            container.addWidget(self.le_url_custom, 11)

            label = QLabel("")
            container.addWidget(label, 1)

            self.pb_resetdata = QPushButton(
                _("Reset Match Data"))
            self.pb_resetdata.setFixedWidth(150)
            self.pb_resetdata.clicked.connect(self.resetdata_click)
            container.addWidget(self.pb_resetdata, 0)

            self.tab2.layout.addLayout(container)

            self.tab2.setLayout(self.tab2.layout)

        except Exception as e:
            module_logger.exception("message")

    def allkill_change(self):
        try:
            self.controller.matchData.setAllKill(self.cb_allkill.isChecked())
        except Exception as e:
            module_logger.exception("message")

    def changeBestOf(self, bestof):
        """Change the minimum sets combo box on change of BoX."""
        bestof = bestof + 1
        self.cb_minSets.clear()
        self.highlightApplyCustom()
        for idx in range(0, bestof):
            self.cb_minSets.addItem(str(idx + 1))
            if bestof == 2:
                self.cb_minSets.setCurrentIndex(1)
            else:
                self.cb_minSets.setCurrentIndex((bestof - 1) / 2)

    def updateMapCompleters(self):
        """Update the auto completers for maps."""
        for i in range(self.max_no_sets):
            list = scctool.settings.maps
            list.remove("TBD")
            list.sort()
            list.append("TBD")
            completer = QCompleter(list, self.le_map[i])
            completer.setCaseSensitivity(Qt.CaseInsensitive)
            completer.setCompletionMode(
                QCompleter.UnfilteredPopupCompletion)
            completer.setWrapAround(True)
            self.le_map[i].setCompleter(completer)

    def updatePlayerCompleters(self):
        """Refresh the completer for the player line edits."""
        list = scctool.settings.config.getMyPlayers(
            True) + ["TBD"] + self.controller.historyManager.getPlayerList()
        for player_idx in range(self.max_no_sets):
            for team_idx in range(2):
                completer = QCompleter(
                    list, self.le_player[team_idx][player_idx])
                completer.setCaseSensitivity(
                    Qt.CaseInsensitive)
                completer.setCompletionMode(
                    QCompleter.InlineCompletion)
                completer.setWrapAround(True)
                self.le_player[team_idx][player_idx].setCompleter(
                    completer)

    def updateTeamCompleters(self):
        """Refresh the completer for the team line edits."""
        list = scctool.settings.config.getMyTeams() + \
            ["TBD"] + self.controller.historyManager.getTeamList()
        for team_idx in range(2):
            completer = QCompleter(
                list, self.le_team[team_idx])
            completer.setCaseSensitivity(Qt.CaseInsensitive)
            completer.setCompletionMode(
                QCompleter.InlineCompletion)
            completer.setWrapAround(True)
            self.le_team[team_idx].setCompleter(completer)

    def createFormMatchDataBox(self):
        """Create the froms for the match data."""
        try:

            self.max_no_sets = scctool.settings.max_no_sets
            self.scoreWidth = 35
            self.raceWidth = 45
            self.labelWidth = 15
            self.mimumLineEditWidth = 130

            self.fromMatchDataBox = QGroupBox(_("Match Data"))
            layout2 = QVBoxLayout()

            self.le_league = MonitoredLineEdit()
            self.le_league.setText("League TBD")
            self.le_league.setAlignment(Qt.AlignCenter)
            self.le_league.setPlaceholderText("League TBD")
            self.le_league.textModified.connect(self.league_changed)
            policy = QSizePolicy()
            policy.setHorizontalStretch(3)
            policy.setHorizontalPolicy(QSizePolicy.Expanding)
            policy.setVerticalStretch(1)
            policy.setVerticalPolicy(QSizePolicy.Fixed)
            self.le_league.setSizePolicy(policy)

            self.le_team = [MonitoredLineEdit() for y in range(2)]
            self.le_player = [[MonitoredLineEdit() for x in range(
                self.max_no_sets)] for y in range(2)]
            self.cb_race = [[QComboBox() for x in range(self.max_no_sets)]
                            for y in range(2)]
            self.sl_score = [QSlider(Qt.Horizontal)
                             for y in range(self.max_no_sets)]
            self.le_map = [MapLineEdit() for y in range(self.max_no_sets)]
            self.label_set = [QLabel()
                              for y in range(self.max_no_sets)]
            self.setContainer = [QHBoxLayout()
                                 for y in range(self.max_no_sets)]

            container = QHBoxLayout()
            for team_idx in range(2):
                self.le_team[team_idx].setText("TBD")
                self.le_team[team_idx].setAlignment(
                    Qt.AlignCenter)
                self.le_team[team_idx].setPlaceholderText(
                    "Team " + str(team_idx + 1))
                policy = QSizePolicy()
                policy.setHorizontalStretch(4)
                policy.setHorizontalPolicy(
                    QSizePolicy.Expanding)
                policy.setVerticalStretch(1)
                policy.setVerticalPolicy(QSizePolicy.Fixed)
                self.le_team[team_idx].setSizePolicy(policy)
                self.le_team[team_idx].setMinimumWidth(self.mimumLineEditWidth)
                self.le_team[team_idx].textModified.connect(
                    lambda team_idx=team_idx: self.team_changed(team_idx))

            self.qb_logo1 = IconPushButton()
            self.qb_logo1.setFixedWidth(self.raceWidth)
            self.qb_logo1.clicked.connect(lambda: self.logoDialog(1))
            logo = self.controller.logoManager.getTeam1()
            self.qb_logo1.setIcon(QIcon(logo.provideQPixmap()))

            self.qb_logo2 = IconPushButton()
            self.qb_logo2.setFixedWidth(self.raceWidth)
            self.qb_logo2.clicked.connect(lambda: self.logoDialog(2))
            logo = self.controller.logoManager.getTeam2()
            self.qb_logo2.setIcon(QIcon(logo.provideQPixmap()))

            self.sl_team = QSlider(Qt.Horizontal)
            self.sl_team.setMinimum(-1)
            self.sl_team.setMaximum(1)
            self.sl_team.setValue(0)
            self.sl_team.setTickPosition(
                QSlider.TicksBothSides)
            self.sl_team.setTickInterval(1)
            self.sl_team.valueChanged.connect(lambda x: self.sl_changed(-1, x))
            self.sl_team.setToolTip(_('Choose your team'))
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

            label = QLabel(_("League:"))
            label.setAlignment(Qt.AlignCenter)
            policy = QSizePolicy()
            policy.setHorizontalStretch(4)
            policy.setHorizontalPolicy(QSizePolicy.Expanding)
            policy.setVerticalStretch(1)
            policy.setVerticalPolicy(QSizePolicy.Fixed)
            label.setSizePolicy(policy)
            container.addWidget(label, 0, 1, 1, 1)

            label = QLabel(_("Maps \ Teams:"))
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
                self.le_map[player_idx].textModified.connect(
                    lambda player_idx=player_idx: self.map_changed(player_idx))
                for team_idx in range(2):
                    self.cb_race[team_idx][player_idx].currentIndexChanged.connect(
                        lambda idx, t=team_idx, p=player_idx: self.race_changed(t, p))
                    self.le_player[team_idx][player_idx].textModified.connect(
                        lambda t=team_idx, p=player_idx: self.player_changed(t, p))
                    self.le_player[team_idx][player_idx].setText("TBD")
                    self.le_player[team_idx][player_idx].setAlignment(
                        Qt.AlignCenter)
                    self.le_player[team_idx][player_idx].setPlaceholderText(
                        _("Player {} of team {}").format(player_idx + 1, team_idx + 1))
                    self.le_player[team_idx][player_idx].setMinimumWidth(
                        self.mimumLineEditWidth)

                    for i in range(4):
                        self.cb_race[team_idx][player_idx].addItem(
                            QIcon(scctool.settings.getAbsPath(
                                "src/" + str(i) + ".png")), "")

                    self.cb_race[team_idx][player_idx].setFixedWidth(
                        self.raceWidth)

                self.sl_score[player_idx].setMinimum(-1)
                self.sl_score[player_idx].setMaximum(1)
                self.sl_score[player_idx].setValue(0)
                self.sl_score[player_idx].setTickPosition(
                    QSlider.TicksBothSides)
                self.sl_score[player_idx].setTickInterval(1)
                self.sl_score[player_idx].valueChanged.connect(
                    lambda x, player_idx=player_idx: self.sl_changed(player_idx, x))
                self.sl_score[player_idx].setToolTip(_('Set the score'))
                self.sl_score[player_idx].setFixedWidth(self.scoreWidth)

                self.le_map[player_idx].setText("TBD")
                self.le_map[player_idx].setAlignment(
                    Qt.AlignCenter)
                self.le_map[player_idx].setPlaceholderText(
                    _("Map {}").format(player_idx + 1))
                self.le_map[player_idx].setMinimumWidth(
                    self.mimumLineEditWidth)

                # self.le_map[player_idx].setReadOnly(True)

                self.setContainer[player_idx] = QHBoxLayout()
                self.label_set[player_idx].setText("#" + str(player_idx + 1))
                self.label_set[player_idx].setAlignment(
                    Qt.AlignCenter)
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
                0, 0, QSizePolicy.Minimum,
                QSizePolicy.Expanding))
            self.fromMatchDataBox.setLayout(layout2)

            self.updateMapCompleters()
            self.updatePlayerCompleters()
            self.updateTeamCompleters()

        except Exception as e:
            module_logger.exception("message")

    def createHorizontalGroupBox(self):
        """Create horizontal group box for tasks."""
        try:
            self.horizontalGroupBox = QGroupBox(_("Tasks"))
            layout = QHBoxLayout()

            self.pb_twitchupdate = QPushButton(
                _("Update Twitch Title"))
            self.pb_twitchupdate.clicked.connect(self.updatetwitch_click)

            self.pb_nightbotupdate = QPushButton(
                _("Update Nightbot"))
            self.pb_nightbotupdate.clicked.connect(self.updatenightbot_click)

            self.pb_resetscore = QPushButton(_("Reset Score"))
            self.pb_resetscore.clicked.connect(self.resetscore_click)

            self.pb_obsupdate = QPushButton(
                _("Update OB&S Data"))
            self.pb_obsupdate.clicked.connect(self.updateobs_click)
            self.pb_obsupdate.setToolTip(_("Shortcut: {}").format("Ctrl+S"))
            self.shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
            self.shortcut.setAutoRepeat(False)
            self.shortcut.activated.connect(self.updateobs_click)

            self.defaultButtonPalette = self.pb_obsupdate.palette()
            self.obsupdate_is_highlighted = False

            layout.addWidget(self.pb_twitchupdate)
            layout.addWidget(self.pb_nightbotupdate)
            layout.addWidget(self.pb_resetscore)
            layout.addWidget(self.pb_obsupdate)

            self.horizontalGroupBox.setLayout(layout)
        except Exception as e:
            module_logger.exception("message")

    def createBackgroundTasksBox(self):
        """Create group box for background tasks."""
        try:
            self.backgroundTasksBox = QGroupBox(
                _("Background Tasks"))

            self.cb_autoUpdate = QCheckBox(
                _("Auto Score Update"))
            self.cb_autoUpdate.setChecked(False)
            string = _('Automatically detects the outcome of SC2 matches that are ' +
                       'played/observed in your SC2-client and updates the score accordingly.')
            self.cb_autoUpdate.setToolTip(string)
            self.cb_autoUpdate.stateChanged.connect(self.autoUpdate_change)

            self.cb_playerIntros = QCheckBox(
                _("Provide Player Intros"))
            self.cb_playerIntros.setChecked(False)
            self.cb_playerIntros.setToolTip(
                _('Update player intros files via SC2-Client-API'))
            self.cb_playerIntros.stateChanged.connect(self.playerIntros_change)

            self.cb_autoToggleScore = QCheckBox(
                _("Set Ingame Score"))
            self.cb_autoToggleScore.setChecked(False)
            string = _('Automatically sets the score of your ingame' +
                       ' UI-interface at the begining of a game.')
            self.cb_autoToggleScore.setToolTip(string)
            self.cb_autoToggleScore.stateChanged.connect(
                self.autoToggleScore_change)

            self.cb_autoToggleProduction = QCheckBox(
                _("Toggle Production Tab"))
            self.cb_autoToggleProduction.setChecked(False)
            string = _('Automatically toggles the production tab of your' +
                       ' ingame UI-interface at the begining of a game.')
            self.cb_autoToggleProduction.setToolTip(string)
            self.cb_autoToggleProduction.stateChanged.connect(
                self.autoToggleProduction_change)

            self.cb_autoTwitch = QCheckBox(
                _("Auto Twitch Update"))
            self.cb_autoTwitch.setChecked(False)
            self.cb_autoTwitch.stateChanged.connect(self.autoTwitch_change)

            self.cb_autoNightbot = QCheckBox(
                _("Auto Nightbot Update"))
            self.cb_autoNightbot.setChecked(False)
            self.cb_autoNightbot.stateChanged.connect(
                self.autoNightbot_change)

            if(not scctool.settings.windows):
                self.cb_autoToggleScore.setEnabled(False)
                self.cb_autoToggleScore.setAttribute(
                    Qt.WA_AlwaysShowToolTips)
                self.cb_autoToggleScore.setToolTip(_('Only Windows'))
                self.cb_autoToggleProduction.setEnabled(False)
                self.cb_autoToggleProduction.setAttribute(
                    Qt.WA_AlwaysShowToolTips)
                self.cb_autoToggleProduction.setToolTip(_('Only Windows'))

            layout = QGridLayout()

            layout.addWidget(self.cb_playerIntros, 0, 0)
            layout.addWidget(self.cb_autoTwitch, 0, 1)
            layout.addWidget(self.cb_autoNightbot, 0, 2)

            layout.addWidget(self.cb_autoUpdate, 1, 0)
            layout.addWidget(self.cb_autoToggleScore, 1, 1)
            layout.addWidget(self.cb_autoToggleProduction, 1, 2)

            self.backgroundTasksBox.setLayout(layout)

        except Exception as e:
            module_logger.exception("message")

    def autoTwitch_change(self):
        """Handle change of auto twitch check box."""
        try:
            if(self.cb_autoTwitch.isChecked()):
                self.controller.autoRequestsThread.activateTask('twitch')
            else:
                self.controller.autoRequestsThread.deactivateTask('twitch')
        except Exception as e:
            module_logger.exception("message")

    def autoNightbot_change(self):
        """Handle change of auto twitch check box."""
        try:
            if(self.cb_autoNightbot.isChecked()):
                self.controller.autoRequestsThread.activateTask('nightbot')
            else:
                self.controller.autoRequestsThread.deactivateTask('nightbot')
        except Exception as e:
            module_logger.exception("message")

    def autoUpdate_change(self):
        """Handle change of auto score update check box."""
        try:
            if(self.cb_autoUpdate.isChecked()):
                self.controller.runSC2ApiThread("updateScore")
            else:
                self.controller.stopSC2ApiThread("updateScore")
        except Exception as e:
            module_logger.exception("message")

    def playerIntros_change(self):
        """Handle change of player intros check box."""
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
        """Handle change of toggle score check box."""
        try:
            if(self.cb_autoToggleScore.isChecked()):
                self.controller.runSC2ApiThread("toggleScore")
            else:
                self.controller.stopSC2ApiThread("toggleScore")
        except Exception as e:
            module_logger.exception("message")

    def autoToggleProduction_change(self):
        """Handle change of toggle production tab check box."""
        try:
            if(self.cb_autoToggleProduction.isChecked()):
                self.controller.runSC2ApiThread("toggleProduction")
            else:
                self.controller.stopSC2ApiThread("toggleProduction")
        except Exception as e:
            module_logger.exception("message")

    def applyCustomFormat(self, format):
        """Handle click to apply custom format."""
        QApplication.setOverrideCursor(
            Qt.WaitCursor)
        try:
            with self.tlock:
                self.controller.matchData.applyCustomFormat(format)
                self.controller.updateForms()
                self.resizeWindow()
                self.highlightOBSupdate(force=True)
            self.highlightApplyCustom(False)
        except Exception as e:
            module_logger.exception("message")
        finally:
            QApplication.restoreOverrideCursor()

    def applycustom_click(self):
        """Handle click to apply custom match."""
        QApplication.setOverrideCursor(
            Qt.WaitCursor)
        try:
            with self.tlock:
                self.statusBar().showMessage(_('Applying Custom Match...'))
                msg = self.controller.applyCustom(int(self.cb_bestof.currentText()),
                                                  self.cb_allkill.isChecked(),
                                                  self.cb_solo.isChecked(),
                                                  int(self.cb_minSets.currentText()),
                                                  self.le_url_custom.text().strip())
                self.statusBar().showMessage(msg)
            self.highlightApplyCustom(False)
        except Exception as e:
            module_logger.exception("message")
        finally:
            QApplication.restoreOverrideCursor()

    def resetdata_click(self):
        """Handle click to reset the data."""
        QApplication.setOverrideCursor(
            Qt.WaitCursor)
        try:
            with self.tlock:
                msg = self.controller.resetData()
                self.statusBar().showMessage(msg)
        except Exception as e:
            module_logger.exception("message")
        finally:
            QApplication.restoreOverrideCursor()

    def refresh_click(self):
        """Handle click to refresh/load data from an URL."""
        QApplication.setOverrideCursor(
            Qt.WaitCursor)
        try:
            url = self.le_url.text()
            with self.tlock:
                self.statusBar().showMessage(_('Reading {}...').format(url))
                msg = self.controller.refreshData(url)
                self.statusBar().showMessage(msg)
        except Exception as e:
            module_logger.exception("message")
        finally:
            QApplication.restoreOverrideCursor()

    def openBrowser_click(self):
        """Handle request to open URL in browser."""
        try:
            url = self.le_url.text()
            self.controller.openURL(url)
        except Exception as e:
            module_logger.exception("message")

    def updatenightbot_click(self):
        """Handle click to change nightbot command."""
        try:
            self.statusBar().showMessage(_('Updating Nightbot Command...'))
            msg = self.controller.updateNightbotCommand()
            self.statusBar().showMessage(msg)
        except Exception as e:
            module_logger.exception("message")

    def updatetwitch_click(self):
        """Handle click to change twitch title."""
        try:
            self.statusBar().showMessage(_('Updating Twitch Title...'))
            msg = self.controller.updateTwitchTitle()
            self.statusBar().showMessage(msg)
        except Exception as e:
            module_logger.exception("message")

    def updateobs_click(self):
        """Handle click to apply changes to OBS_data."""
        try:
            self.statusBar().showMessage(_('Updating OBS Data...'))
            self.controller.updateOBS()
            if not self.controller.resetWarning():
                self.statusBar().showMessage('')
        except Exception as e:
            module_logger.exception("message")

    def resetscore_click(self, myteam=False):
        """Handle click to reset the score."""
        try:
            self.statusBar().showMessage(_('Resetting Score...'))
            with self.tlock:
                for set_idx in range(self.max_no_sets):
                    self.sl_score[set_idx].setValue(0)
                    self.controller.matchData.setMapScore(
                        set_idx, 0, overwrite=True)
                if myteam:
                    self.sl_team.setValue(0)
                    self.controller.matchData.setMyTeam(0)
                self.controller.updateOBS()
                if not self.controller.resetWarning():
                    self.statusBar().showMessage('')
        except Exception as e:
            module_logger.exception("message")

    def setScore(self, idx, score, allkill=True):
        """Handle change of the score."""
        try:
            if(self.sl_score[idx].value() == 0):
                self.statusBar().showMessage(_('Updating Score...'))
                with self.tlock:
                    self.sl_score[idx].setValue(score)
                    self.controller.matchData.setMapScore(idx, score, True)
                    if allkill:
                        self.controller.allkillUpdate()
                    if not self.controller.resetWarning():
                        self.statusBar().showMessage('')
                return True
            else:
                return False
        except Exception as e:
            module_logger.exception("message")

    def league_changed(self):
        if not self.tlock.trigger():
            return
        self.controller.matchData.setLeague(self.le_league.text())
        self.highlightOBSupdate()

    def sl_changed(self, set_idx, value):
        """Handle a new score value."""
        try:
            if self.tlock.trigger():
                if set_idx == -1:
                    self.controller.matchData.setMyTeam(value)
                else:
                    self.controller.matchData.setMapScore(set_idx, value, True)
                    self.controller.allkillUpdate()
                self.controller.updateOBS()
        except Exception as e:
            module_logger.exception("message")

    def player_changed(self, team_idx, player_idx):
        """Handle a change of player names."""
        if not self.tlock.trigger():
            return
        try:
            player = self.le_player[team_idx][player_idx].text().strip()
            race = self.cb_race[team_idx][player_idx].currentIndex()
            if(player_idx == 0 and self.controller.matchData.getSolo()):
                for player_idx in range(1, self.max_no_sets):
                    self.le_player[team_idx][player_idx].setText(player)
            self.controller.historyManager.insertPlayer(player, race)
            self.controller.matchData.setPlayer(
                team_idx, player_idx, self.le_player[team_idx][player_idx].text())

            if race == 0:
                new_race = scctool.settings.race2idx(
                    self.controller.historyManager.getRace(player))
                if new_race != 0:
                    self.cb_race[team_idx][player_idx].setCurrentIndex(
                        new_race)
            elif player.lower() == "tbd":
                self.cb_race[team_idx][player_idx].setCurrentIndex(0)
            self.updatePlayerCompleters()
        except Exception as e:
            module_logger.exception("message")
        finally:
            self.highlightOBSupdate()

    def race_changed(self, team_idx, player_idx):
        """Handle a change of player names."""
        if not self.tlock.trigger():
            return
        player = self.le_player[team_idx][player_idx].text().strip()
        race = self.cb_race[team_idx][player_idx].currentIndex()
        self.controller.historyManager.insertPlayer(player, race)
        self.controller.matchData.setRace(team_idx, player_idx, scctool.settings.idx2race(
            self.cb_race[team_idx][player_idx].currentIndex()))
        try:
            if(player_idx == 0 and self.controller.matchData.getSolo()):
                idx = self.cb_race[team_idx][0].currentIndex()
                for player_idx in range(1, self.max_no_sets):
                    self.cb_race[team_idx][player_idx].setCurrentIndex(idx)

        except Exception as e:
            module_logger.exception("message")
        finally:
            self.highlightOBSupdate()

    def team_changed(self, team_idx):
        if not self.tlock.trigger():
            return
        team = self.le_team[team_idx].text().strip()
        self.controller.historyManager.insertTeam(team)
        self.updateTeamCompleters()
        self.controller.matchData.setTeam(team_idx, team)
        self.highlightOBSupdate()
        self.controller.matchData.autoSetMyTeam()
        self.sl_team.setValue(self.controller.matchData.getMyTeam())

    def map_changed(self, set_idx):
        if not self.tlock.trigger():
            return
        self.controller.matchData.setMap(set_idx, self.le_map[set_idx].text())
        self.highlightOBSupdate()

    def highlightOBSupdate(self, highlight=True, force=False):
        if not force and not self.tlock.trigger():
            return
        try:
            if self.obsupdate_is_highlighted == highlight:
                return highlight
        except AttributeError:
            return False

        if highlight:
            myPalette = self.pb_obsupdate.palette()
            myPalette.setColor(QPalette.Background,
                               Qt.darkBlue)
            myPalette.setColor(QPalette.ButtonText,
                               Qt.darkBlue)
            self.pb_obsupdate.setPalette(myPalette)
        else:
            self.pb_obsupdate.setPalette(self.defaultButtonPalette)

        self.obsupdate_is_highlighted = highlight
        return highlight

    def highlightApplyCustom(self, highlight=True, force=False):
        if not force and not self.tlock.trigger():
            return
        try:
            if self.applycustom_is_highlighted == highlight:
                return highlight
        except AttributeError:
            return False

        if highlight:
            myPalette = self.pb_applycustom.palette()
            myPalette.setColor(QPalette.Background,
                               Qt.darkBlue)
            myPalette.setColor(QPalette.ButtonText,
                               Qt.darkBlue)
            self.pb_applycustom.setPalette(myPalette)
        else:
            self.pb_applycustom.setPalette(self.defaultButtonPalette)

        self.applycustom_is_highlighted = highlight
        return highlight

    def logoDialog(self, team):
        """Open dialog for team logo."""
        self.controller.logoManager.resetLogoChanged()
        self.mysubwindows['icons'] = SubwindowLogos()
        self.mysubwindows['icons'].createWindow(self, self.controller, team)
        self.mysubwindows['icons'].show()

    def resizeWindow(self):
        """Resize the window height to size hint."""
        if(not self.isMaximized()):
            self.processEvents()
            self.resize(self.width(), self.sizeHint().height())

    def processEvents(self):
        """Process ten PyQt5 events."""
        for i in range(0, 10):
            self.app.processEvents()

    def restart(self):
        """Restart the main window."""
        self.close()
        self.app.exit(self.EXIT_CODE_REBOOT)


class TriggerLock():
    def __init__(self):
        self.__trigger = True

    def __enter__(self):
        self.__trigger = False

    def __exit__(self, type, value, traceback):
        self.__trigger = True

    def trigger(self):
        return bool(self.__trigger)
