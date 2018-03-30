"""Define the main window."""
import logging
import PyQt5
# from PyQt5.QtWidgets import *
# from PyQt5.QtCore import *
# from PyQt5.QtGui import *

import scctool.settings
import scctool.settings.config
import shutil
import os
import markdown2
import gettext

from scctool.view.widgets import BusyProgressBar, MapLineEdit, IconPushButton
from scctool.view.subConnections import SubwindowConnections
from scctool.view.subStyles import SubwindowStyles
from scctool.view.subMisc import SubwindowMisc
from scctool.view.subMarkdown import SubwindowMarkdown
from scctool.view.subIcons import SubwindowIcons

# create logger
module_logger = logging.getLogger('scctool.view.main')


class MainWindow(PyQt5.QtWidgets.QMainWindow):
    """Show the main window of SCCT."""

    EXIT_CODE_REBOOT = -123

    def __init__(self, controller, app, translator, showChangelog):
        """Init the main window."""
        try:
            super(MainWindow, self).__init__()

            self.trigger = True
            self.controller = controller
            self.translator = translator

            self.createFormMatchDataBox()
            self.createTabs()
            self.createHorizontalGroupBox()
            self.createBackgroundTasksBox()

            self.createMenuBar()

            mainLayout = PyQt5.QtWidgets.QVBoxLayout()
            mainLayout.addWidget(self.tabs, 0)
            mainLayout.addWidget(self.fromMatchDataBox, 1)
            mainLayout.addWidget(self.backgroundTasksBox, 0)
            mainLayout.addWidget(self.horizontalGroupBox, 0)

            self.setWindowTitle(
                "StarCraft Casting Tool v{}".format(scctool.__version__))

            self.window = PyQt5.QtWidgets.QWidget()
            self.window.setLayout(mainLayout)
            self.setCentralWidget(self.window)

            # self.size
            self.statusBar()

            self.progressBar = BusyProgressBar()

            # self.progressBar.setMaximumHeight(20)
            self.progressBar.setMaximumWidth(160)
            self.progressBar.setMinimumWidth(160)
            self.progressBar.setVisible(False)
            self.progressBar.setText(_("FTP Transfer in progress..."))
            self.statusBar().addPermanentWidget(self.progressBar)

            self.app = app
            self.controller.setView(self)
            self.controller.refreshButtonStatus()

            self.processEvents()
            self.settings = PyQt5.QtCore.QSettings(
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
        PyQt5.QtWidgets.QMessageBox.about(
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
                PyQt5.QtWidgets.QMainWindow.closeEvent(self, event)
                # event.accept()
        except Exception as e:
            module_logger.exception("message")

    def createMenuBar(self):
        """Create the menu bar."""
        try:
            menubar = self.menuBar()
            settingsMenu = menubar.addMenu(_('Settings'))
            apiAct = PyQt5.QtWidgets.QAction(PyQt5.QtGui.QIcon(scctool.settings.getAbsPath(
                'src/connection.png')), _('Connections'), self)
            apiAct.setToolTip(
                _('Edit FTP-Settings and API-Settings for Twitch and Nightbot'))
            apiAct.triggered.connect(self.openApiDialog)
            settingsMenu.addAction(apiAct)
            styleAct = PyQt5.QtWidgets.QAction(PyQt5.QtGui.QIcon(scctool.settings.getAbsPath(
                'src/pantone.png')), _('Styles'), self)
            styleAct.setToolTip('')
            styleAct.triggered.connect(self.openStyleDialog)
            settingsMenu.addAction(styleAct)
            miscAct = PyQt5.QtWidgets.QAction(PyQt5.QtGui.QIcon(scctool.settings.getAbsPath(
                'src/settings.png')), _('Misc'), self)
            miscAct.setToolTip('')
            miscAct.triggered.connect(self.openMiscDialog)
            settingsMenu.addAction(miscAct)

            infoMenu = menubar.addMenu(_('Info && Links'))

            myAct = PyQt5.QtWidgets.QAction(PyQt5.QtGui.QIcon(scctool.settings.getAbsPath(
                'src/about.png')), _('About'), self)
            myAct.triggered.connect(self.showAbout)
            infoMenu.addAction(myAct)
            

            myAct = PyQt5.QtWidgets.QAction(PyQt5.QtGui.QIcon(scctool.settings.getAbsPath(
                'src/readme.ico')), _('Readme'), self)
            myAct.triggered.connect(self.openReadme)
            infoMenu.addAction(myAct)
            
            myAct = PyQt5.QtWidgets.QAction(PyQt5.QtGui.QIcon(scctool.settings.getAbsPath(
                'src/update.png')), _('Check for new version'), self)
            myAct.triggered.connect(lambda: self.controller.checkVersion(True))
            infoMenu.addAction(myAct)
            
            myAct = PyQt5.QtWidgets.QAction(PyQt5.QtGui.QIcon(scctool.settings.getAbsPath(
                'src/changelog.png')), _('Changelog'), self)
            myAct.triggered.connect(self.openChangelog)
            infoMenu.addAction(myAct)
            
            
            infoMenu.addSeparator()

            websiteAct = PyQt5.QtWidgets.QAction(
                PyQt5.QtGui.QIcon(
                    scctool.settings.getAbsPath('src/scct.ico')),
                'StarCraft Casting Tool', self)
            websiteAct.triggered.connect(lambda: self.controller.openURL(
                "https://teampheenix.github.io/StarCraft-Casting-Tool/"))
            infoMenu.addAction(websiteAct)


            ixAct = PyQt5.QtWidgets.QAction(PyQt5.QtGui.QIcon(scctool.settings.getAbsPath(
                'src/icon.png')), 'team pheeniX', self)
            ixAct.triggered.connect(
                lambda:  self.controller.openURL("http://team-pheenix.de"))
            infoMenu.addAction(ixAct)

            alphaAct = PyQt5.QtWidgets.QAction(PyQt5.QtGui.QIcon(scctool.settings.getAbsPath(
                'src/alpha.png')), 'AlphaTL', self)
            alphaAct.triggered.connect(
                lambda: self.controller.openURL("http://alpha.tl"))
            infoMenu.addAction(alphaAct)

            rstlAct = PyQt5.QtWidgets.QAction(PyQt5.QtGui.QIcon(scctool.settings.getAbsPath(
                'src/rstl.png')), 'RSTL', self)
            rstlAct.triggered.connect(
                lambda: self.controller.openURL("http://hdgame.net/en/"))
            infoMenu.addAction(rstlAct)

            infoMenu.addSeparator()

            myAct = PyQt5.QtWidgets.QAction(PyQt5.QtGui.QIcon(scctool.settings.getAbsPath(
                'src/donate.ico')), _('Donate'), self)
            myAct.triggered.connect(lambda: self.controller.openURL(
                "https://streamlabs.com/scpressure"))
            infoMenu.addAction(myAct)

            langMenu = menubar.addMenu(_('Language'))

            language = scctool.settings.config.parser.get("SCT", "language")

            myAct = PyQt5.QtWidgets.QAction(PyQt5.QtGui.QIcon(scctool.settings.getAbsPath(
                'src/de.png')), 'Deutsch', self, checkable=True)
            myAct.setChecked(language == 'de_DE')
            myAct.triggered.connect(lambda: self.changeLanguage('de_DE'))
            langMenu.addAction(myAct)

            myAct = PyQt5.QtWidgets.QAction(PyQt5.QtGui.QIcon(scctool.settings.getAbsPath(
                'src/en.png')), 'English', self, checkable=True)
            myAct.setChecked(language == 'en_US')
            myAct.triggered.connect(lambda: self.changeLanguage('en_US'))
            langMenu.addAction(myAct)

            myAct = PyQt5.QtWidgets.QAction(PyQt5.QtGui.QIcon(scctool.settings.getAbsPath(
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
        self.mysubwindows['readme'].createWindow(self, _("Readme"), "src/readme.ico", "README.md")
        self.mysubwindows['readme'].show()
        
    def openChangelog(self):
        """Open subwindow with readme viewer."""
        self.mysubwindows['changelog'] = SubwindowMarkdown()
        self.mysubwindows['changelog'].createWindow(self, "StarCraft Casting Tool "+_("Changelog"), "src/changelog.png", "CHANGELOG.md")
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
        self.translator = PyQt5.QtCore.QTranslator(self.app)
        self.translator.load(PyQt5.QtCore.QLocale(language),
                             "qtbase", "_",  scctool.settings.getAbsPath('locales'), ".qm")
        self.app.installTranslator(self.translator)

        scctool.settings.config.parser.set("SCT", "language", language)
        self.restart()

    def createTabs(self):
        """Create tabs in main window."""
        try:
            # Initialize tab screen
            self.tabs = PyQt5.QtWidgets.QTabWidget()
            self.tab1 = PyQt5.QtWidgets.QWidget()
            self.tab2 = PyQt5.QtWidgets.QWidget()
            # self.tabs.resize(300,200)

            # Add tabs
            self.tabs.addTab(self.tab1, _("Match Grabber for AlphaTL && RSTL"))
            self.tabs.addTab(self.tab2, _("Custom Match"))

            # Create first tab
            self.tab1.layout = PyQt5.QtWidgets.QVBoxLayout()

            self.le_url = PyQt5.QtWidgets.QLineEdit()
            self.le_url.setAlignment(PyQt5.QtCore.Qt.AlignCenter)

            self.le_url.setPlaceholderText("http://alpha.tl/match/2392")

            completer = PyQt5.QtWidgets.QCompleter(
                ["http://alpha.tl/match/",
                 "http://hdgame.net/en/tournaments/list/tournament/rstl-12/"], self.le_url)
            completer.setCaseSensitivity(PyQt5.QtCore.Qt.CaseInsensitive)
            completer.setCompletionMode(
                PyQt5.QtWidgets.QCompleter.UnfilteredPopupCompletion)
            completer.setWrapAround(True)
            self.le_url.setCompleter(completer)
            minWidth = self.scoreWidth + 2 * self.raceWidth + \
                2 * self.mimumLineEditWidth + 4 * 6
            self.le_url.setMinimumWidth(minWidth)

            self.pb_openBrowser = PyQt5.QtWidgets.QPushButton(
                _("Open in Browser"))
            self.pb_openBrowser.clicked.connect(self.openBrowser_click)
            width = (self.scoreWidth + 2 * self.raceWidth + 2 *
                     self.mimumLineEditWidth + 4 * 6) / 2 - 2
            self.pb_openBrowser.setMinimumWidth(width)

            container = PyQt5.QtWidgets.QHBoxLayout()
            label = PyQt5.QtWidgets.QLabel()
            label.setFixedWidth(self.labelWidth)
            container.addWidget(label, 0)
            label = PyQt5.QtWidgets.QLabel(_("Match-URL:"))
            label.setMinimumWidth(80)
            container.addWidget(label, 0)
            container.addWidget(self.le_url, 1)
            button = PyQt5.QtWidgets.QPushButton()
            pixmap = PyQt5.QtGui.QIcon(
                scctool.settings.getAbsPath('src/alpha.png'))
            button.setIcon(pixmap)
            button.clicked.connect(
                lambda: self.controller.openURL("http://alpha.tl/"))
            container.addWidget(button, 0)
            button = PyQt5.QtWidgets.QPushButton()
            pixmap = PyQt5.QtGui.QIcon(
                scctool.settings.getAbsPath('src/rstl.png'))
            button.setIcon(pixmap)
            button.clicked.connect(
                lambda: self.controller.openURL("http://hdgame.net/en/"))
            container.addWidget(button, 0)

            self.tab1.layout = PyQt5.QtWidgets.QFormLayout()
            self.tab1.layout.addRow(container)

            container = PyQt5.QtWidgets.QHBoxLayout()

            # self.pb_download = PyQt5.QtWidgets.QPushButton("Download Images from URL")
            # container.addWidget(self.pb_download)
            label = PyQt5.QtWidgets.QLabel()
            label.setFixedWidth(self.labelWidth)
            container.addWidget(label, 0)
            label = PyQt5.QtWidgets.QLabel()
            label.setMinimumWidth(80)
            container.addWidget(label, 0)
            self.pb_refresh = PyQt5.QtWidgets.QPushButton(
                _("Load Data from URL"))
            self.pb_refresh.clicked.connect(self.refresh_click)
            container.addWidget(self.pb_openBrowser, 3)
            container.addWidget(self.pb_refresh, 3)

            self.tab1.layout.addRow(container)
            self.tab1.setLayout(self.tab1.layout)

            # Create second tab

            self.tab2.layout = PyQt5.QtWidgets.QVBoxLayout()

            container = PyQt5.QtWidgets.QHBoxLayout()

            label = PyQt5.QtWidgets.QLabel()
            label.setMinimumWidth(self.labelWidth)
            container.addWidget(label, 0)

            label = PyQt5.QtWidgets.QLabel(_("Match Format:"))
            label.setMinimumWidth(80)
            container.addWidget(label, 0)

            container.addWidget(PyQt5.QtWidgets.QLabel(_("Best of")), 0)

            self.cb_bestof = PyQt5.QtWidgets.QComboBox()
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

            container.addWidget(PyQt5.QtWidgets.QLabel(_(" but at least")), 0)

            self.cb_minSets = PyQt5.QtWidgets.QComboBox()

            self.cb_minSets.setToolTip(
                _('Minimum number of maps played (even if the match is decided already)'))
            self.cb_minSets.setMaximumWidth(40)
            container.addWidget(self.cb_minSets, 0)
            container.addWidget(
                PyQt5.QtWidgets.QLabel(" " + _("maps") + " "), 0)

            self.cb_allkill = PyQt5.QtWidgets.QCheckBox(_("All-Kill Format"))
            self.cb_allkill.setChecked(False)
            self.cb_allkill.setToolTip(
                _('Winner stays and is automatically placed into the next set'))
            container.addWidget(self.cb_allkill, 0)

            self.cb_solo = PyQt5.QtWidgets.QCheckBox(_("1vs1"))
            self.cb_solo.setChecked(False)
            self.cb_solo.setToolTip(
                _('Select for solo (non-team matches)'))
            container.addWidget(self.cb_solo, 0)

            label = PyQt5.QtWidgets.QLabel("")
            container.addWidget(label, 1)

            self.pb_applycustom = PyQt5.QtWidgets.QPushButton(
                _("Apply Format"))
            self.pb_applycustom.clicked.connect(self.applycustom_click)
            self.pb_applycustom.setFixedWidth(150)
            container.addWidget(self.pb_applycustom, 0)

            self.tab2.layout.addLayout(container)

            container = PyQt5.QtWidgets.QHBoxLayout()

            label = PyQt5.QtWidgets.QLabel()
            label.setMinimumWidth(self.labelWidth)
            container.addWidget(label, 0)

            label = PyQt5.QtWidgets.QLabel(_("Match-URL:"))
            label.setMinimumWidth(80)
            container.addWidget(label, 0)

            self.le_url_custom = PyQt5.QtWidgets.QLineEdit()
            self.le_url_custom.setAlignment(PyQt5.QtCore.Qt.AlignCenter)
            self.le_url_custom.setToolTip(
                _('Optionally specify the Match-URL, e.g., for Nightbot commands'))
            self.le_url_custom.setPlaceholderText(
                _("Specify the Match-URL of your Custom Match"))

            completer = PyQt5.QtWidgets.QCompleter(
                ["http://"], self.le_url_custom)
            completer.setCaseSensitivity(PyQt5.QtCore.Qt.CaseInsensitive)
            completer.setCompletionMode(
                PyQt5.QtWidgets.QCompleter.UnfilteredPopupCompletion)
            completer.setWrapAround(True)
            self.le_url_custom.setCompleter(completer)
            self.le_url_custom.setMinimumWidth(360)

            container.addWidget(self.le_url_custom, 11)

            label = PyQt5.QtWidgets.QLabel("")
            container.addWidget(label, 1)

            self.pb_resetdata = PyQt5.QtWidgets.QPushButton(
                _("Reset Match Data"))
            self.pb_resetdata.setFixedWidth(150)
            self.pb_resetdata.clicked.connect(self.resetdata_click)
            container.addWidget(self.pb_resetdata, 0)

            self.tab2.layout.addLayout(container)

            self.tab2.setLayout(self.tab2.layout)

        except Exception as e:
            module_logger.exception("message")

    def changeBestOf(self, bestof):
        """Change the minimum sets combo box on change of BoX."""
        bestof = bestof + 1
        self.cb_minSets.clear()
        for idx in range(0, bestof):
            self.cb_minSets.addItem(str(idx + 1))
            if bestof == 2:
                self.cb_minSets.setCurrentIndex(1)
            else:
                self.cb_minSets.setCurrentIndex((bestof - 1) / 2)

    def updateMapCompleters(self):
        """Update the auto completers for maps."""
        for i in range(self.max_no_sets):
            completer = PyQt5.QtWidgets.QCompleter(
                scctool.settings.maps, self.le_map[i])
            completer.setCaseSensitivity(PyQt5.QtCore.Qt.CaseInsensitive)
            completer.setCompletionMode(
                PyQt5.QtWidgets.QCompleter.InlineCompletion)
            completer.setWrapAround(True)
            self.le_map[i].setCompleter(completer)

    def createFormMatchDataBox(self):
        """Create the froms for the match data."""
        try:

            self.max_no_sets = scctool.settings.max_no_sets
            self.scoreWidth = 35
            self.raceWidth = 45
            self.labelWidth = 15
            self.mimumLineEditWidth = 130

            self.fromMatchDataBox = PyQt5.QtWidgets.QGroupBox(_("Match Data"))
            layout2 = PyQt5.QtWidgets.QVBoxLayout()

            self.le_league = PyQt5.QtWidgets.QLineEdit()
            self.le_league.setText("League TBD")
            self.le_league.setAlignment(PyQt5.QtCore.Qt.AlignCenter)
            self.le_league.setPlaceholderText("League TBD")
            policy = PyQt5.QtWidgets.QSizePolicy()
            policy.setHorizontalStretch(3)
            policy.setHorizontalPolicy(PyQt5.QtWidgets.QSizePolicy.Expanding)
            policy.setVerticalStretch(1)
            policy.setVerticalPolicy(PyQt5.QtWidgets.QSizePolicy.Fixed)
            self.le_league.setSizePolicy(policy)

            self.le_team = [PyQt5.QtWidgets.QLineEdit() for y in range(2)]
            self.le_player = [[PyQt5.QtWidgets.QLineEdit() for x in range(
                self.max_no_sets)] for y in range(2)]
            self.cb_race = [[PyQt5.QtWidgets.QComboBox() for x in range(self.max_no_sets)]
                            for y in range(2)]
            self.sl_score = [PyQt5.QtWidgets.QSlider(PyQt5.QtCore.Qt.Horizontal)
                             for y in range(self.max_no_sets)]
            self.le_map = [MapLineEdit() for y in range(self.max_no_sets)]
            self.label_set = [PyQt5.QtWidgets.QLabel()
                              for y in range(self.max_no_sets)]
            self.setContainer = [PyQt5.QtWidgets.QHBoxLayout()
                                 for y in range(self.max_no_sets)]

            container = PyQt5.QtWidgets.QHBoxLayout()
            for team_idx in range(2):
                self.le_team[team_idx].setText("TBD")
                self.le_team[team_idx].setAlignment(
                    PyQt5.QtCore.Qt.AlignCenter)
                self.le_team[team_idx].setPlaceholderText(
                    "Team " + str(team_idx + 1))
                completer = PyQt5.QtWidgets.QCompleter(
                    scctool.settings.config.getMyTeams() + ["TBD"], self.le_team[team_idx])
                completer.setCaseSensitivity(PyQt5.QtCore.Qt.CaseInsensitive)
                completer.setCompletionMode(
                    PyQt5.QtWidgets.QCompleter.InlineCompletion)
                completer.setWrapAround(True)
                self.le_team[team_idx].setCompleter(completer)
                policy = PyQt5.QtWidgets.QSizePolicy()
                policy.setHorizontalStretch(4)
                policy.setHorizontalPolicy(
                    PyQt5.QtWidgets.QSizePolicy.Expanding)
                policy.setVerticalStretch(1)
                policy.setVerticalPolicy(PyQt5.QtWidgets.QSizePolicy.Fixed)
                self.le_team[team_idx].setSizePolicy(policy)
                self.le_team[team_idx].setMinimumWidth(self.mimumLineEditWidth)

            self.qb_logo1 = IconPushButton()
            self.qb_logo1.setFixedWidth(self.raceWidth)
            self.qb_logo1.clicked.connect(lambda: self.logoDialog(1))
            pixmap = PyQt5.QtGui.QIcon(scctool.settings.getAbsPath(self.controller.linkFile(
                scctool.settings.OBSdataDir + '/logo1')))
            self.qb_logo1.setIcon(pixmap)

            self.qb_logo2 = IconPushButton()
            self.qb_logo2.setFixedWidth(self.raceWidth)
            self.qb_logo2.clicked.connect(lambda: self.logoDialog(2))
            pixmap = PyQt5.QtGui.QIcon(scctool.settings.getAbsPath(self.controller.linkFile(
                scctool.settings.OBSdataDir + '/logo2')))
            self.qb_logo2.setIcon(pixmap)

            self.sl_team = PyQt5.QtWidgets.QSlider(PyQt5.QtCore.Qt.Horizontal)
            self.sl_team.setMinimum(-1)
            self.sl_team.setMaximum(1)
            self.sl_team.setValue(0)
            self.sl_team.setTickPosition(
                PyQt5.QtWidgets.QSlider.TicksBothSides)
            self.sl_team.setTickInterval(1)
            self.sl_team.valueChanged.connect(self.sl_changed)
            self.sl_team.setToolTip(_('Choose your team'))
            self.sl_team.setMinimumHeight(5)
            self.sl_team.setFixedWidth(self.scoreWidth)
            policy = PyQt5.QtWidgets.QSizePolicy()
            policy.setHorizontalStretch(0)
            policy.setHorizontalPolicy(PyQt5.QtWidgets.QSizePolicy.Fixed)
            policy.setVerticalStretch(1)
            policy.setVerticalPolicy(PyQt5.QtWidgets.QSizePolicy.Fixed)
            self.sl_team.setSizePolicy(policy)

            container = PyQt5.QtWidgets.QGridLayout()

            label = PyQt5.QtWidgets.QLabel("")
            label.setFixedWidth(self.labelWidth)
            container.addWidget(label, 0, 0, 2, 1)

            label = PyQt5.QtWidgets.QLabel(_("League:"))
            label.setAlignment(PyQt5.QtCore.Qt.AlignCenter)
            policy = PyQt5.QtWidgets.QSizePolicy()
            policy.setHorizontalStretch(4)
            policy.setHorizontalPolicy(PyQt5.QtWidgets.QSizePolicy.Expanding)
            policy.setVerticalStretch(1)
            policy.setVerticalPolicy(PyQt5.QtWidgets.QSizePolicy.Fixed)
            label.setSizePolicy(policy)
            container.addWidget(label, 0, 1, 1, 1)

            label = PyQt5.QtWidgets.QLabel(_("Maps \ Teams:"))
            label.setAlignment(PyQt5.QtCore.Qt.AlignCenter)
            policy = PyQt5.QtWidgets.QSizePolicy()
            policy.setHorizontalStretch(4)
            policy.setHorizontalPolicy(PyQt5.QtWidgets.QSizePolicy.Expanding)
            policy.setVerticalStretch(1)
            policy.setVerticalPolicy(PyQt5.QtWidgets.QSizePolicy.Fixed)
            label.setSizePolicy(policy)
            container.addWidget(label, 1, 1, 1, 1)

            container.addWidget(self.qb_logo1, 0, 2, 2, 1)
            container.addWidget(self.le_league, 0, 3, 1, 3)
            container.addWidget(self.le_team[0], 1, 3, 1, 1)
            container.addWidget(self.sl_team, 1, 4, 1, 1)
            container.addWidget(self.le_team[1], 1, 5, 1, 1)
            container.addWidget(self.qb_logo2, 0, 6, 2, 1)

            layout2.addLayout(container)

            for team_idx in range(2):
                self.le_player[team_idx][0].editingFinished.connect(
                    lambda team_idx=team_idx: self.player_changed(team_idx))
                self.cb_race[team_idx][0].currentIndexChanged.connect(
                    lambda value, team_idx=team_idx, func=self.race_changed: func(team_idx))

            for player_idx in range(self.max_no_sets):
                for team_idx in range(2):
                    self.le_player[team_idx][player_idx].setText("TBD")
                    self.le_player[team_idx][player_idx].setAlignment(
                        PyQt5.QtCore.Qt.AlignCenter)
                    self.le_player[team_idx][player_idx].setPlaceholderText(
                        _("Player {} of team {}").format(player_idx + 1, team_idx + 1))
                    completer = PyQt5.QtWidgets.QCompleter(
                        scctool.settings.config.getMyPlayers(
                            True), self.le_player[team_idx][player_idx])
                    completer.setCaseSensitivity(
                        PyQt5.QtCore.Qt.CaseInsensitive)
                    completer.setCompletionMode(
                        PyQt5.QtWidgets.QCompleter.InlineCompletion)
                    completer.setWrapAround(True)
                    self.le_player[team_idx][player_idx].setCompleter(
                        completer)
                    self.le_player[team_idx][player_idx].setMinimumWidth(
                        self.mimumLineEditWidth)

                    for i in range(4):
                        self.cb_race[team_idx][player_idx].addItem(
                            PyQt5.QtGui.QIcon(scctool.settings.getAbsPath(
                                "src/" + str(i) + ".png")), "")

                    self.cb_race[team_idx][player_idx].setFixedWidth(
                        self.raceWidth)

                self.sl_score[player_idx].setMinimum(-1)
                self.sl_score[player_idx].setMaximum(1)
                self.sl_score[player_idx].setValue(0)
                self.sl_score[player_idx].setTickPosition(
                    PyQt5.QtWidgets.QSlider.TicksBothSides)
                self.sl_score[player_idx].setTickInterval(1)
                self.sl_score[player_idx].valueChanged.connect(self.sl_changed)
                self.sl_score[player_idx].setToolTip(_('Set the score'))
                self.sl_score[player_idx].setFixedWidth(self.scoreWidth)

                self.le_map[player_idx].setText("TBD")
                self.le_map[player_idx].setAlignment(
                    PyQt5.QtCore.Qt.AlignCenter)
                self.le_map[player_idx].setPlaceholderText(
                    _("Map {}").format(player_idx + 1))
                self.le_map[player_idx].setMinimumWidth(
                    self.mimumLineEditWidth)

                # self.le_map[player_idx].setReadOnly(True)

                self.setContainer[player_idx] = PyQt5.QtWidgets.QHBoxLayout()
                self.label_set[player_idx].setText("#" + str(player_idx + 1))
                self.label_set[player_idx].setAlignment(
                    PyQt5.QtCore.Qt.AlignCenter)
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

            layout2.addItem(PyQt5.QtWidgets.QSpacerItem(
                0, 0, PyQt5.QtWidgets.QSizePolicy.Minimum,
                PyQt5.QtWidgets.QSizePolicy.Expanding))
            self.fromMatchDataBox.setLayout(layout2)

            self.updateMapCompleters()

        except Exception as e:
            module_logger.exception("message")

    def createHorizontalGroupBox(self):
        """Create horizontal group box for tasks."""
        try:
            self.horizontalGroupBox = PyQt5.QtWidgets.QGroupBox(_("Tasks"))
            layout = PyQt5.QtWidgets.QHBoxLayout()

            self.pb_twitchupdate = PyQt5.QtWidgets.QPushButton(
                _("Update Twitch Title"))
            self.pb_twitchupdate.clicked.connect(self.updatetwitch_click)

            self.pb_nightbotupdate = PyQt5.QtWidgets.QPushButton(
                _("Update Nightbot"))
            self.pb_nightbotupdate.clicked.connect(self.updatenightbot_click)

            self.pb_resetscore = PyQt5.QtWidgets.QPushButton(_("Reset Score"))
            self.pb_resetscore.clicked.connect(self.resetscore_click)

            self.pb_obsupdate = PyQt5.QtWidgets.QPushButton(
                _("Update OBS Data"))
            self.pb_obsupdate.clicked.connect(self.updateobs_click)

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
            self.backgroundTasksBox = PyQt5.QtWidgets.QGroupBox(
                _("Background Tasks"))

            self.cb_autoUpdate = PyQt5.QtWidgets.QCheckBox(
                _("Auto Score Update"))
            self.cb_autoUpdate.setChecked(False)
            string = _('Automatically detects the outcome of SC2 matches that are ' +
                       'played/observed in your SC2-client and updates the score accordingly.')
            self.cb_autoUpdate.setToolTip(string)
            self.cb_autoUpdate.stateChanged.connect(self.autoUpdate_change)

            self.cb_playerIntros = PyQt5.QtWidgets.QCheckBox(
                _("Provide Player Intros"))
            self.cb_playerIntros.setChecked(False)
            self.cb_playerIntros.setToolTip(
                _('Update player intros files via SC2-Client-API'))
            self.cb_playerIntros.stateChanged.connect(self.playerIntros_change)

            self.cb_autoToggleScore = PyQt5.QtWidgets.QCheckBox(
                _("Set Ingame Score"))
            self.cb_autoToggleScore.setChecked(False)
            string = _('Automatically sets the score of your ingame' +
                       ' UI-interface at the begining of a game.')
            self.cb_autoToggleScore.setToolTip(string)
            self.cb_autoToggleScore.stateChanged.connect(
                self.autoToggleScore_change)

            self.cb_autoToggleProduction = PyQt5.QtWidgets.QCheckBox(
                _("Toggle Production Tab"))
            self.cb_autoToggleProduction.setChecked(False)
            string = _('Automatically toggles the production tab of your' +
                       ' ingame UI-interface at the begining of a game.')
            self.cb_autoToggleProduction.setToolTip(string)
            self.cb_autoToggleProduction.stateChanged.connect(
                self.autoToggleProduction_change)

            self.cb_autoFTP = PyQt5.QtWidgets.QCheckBox(_("FTP Upload"))
            self.cb_autoFTP.setChecked(False)
            self.cb_autoFTP.stateChanged.connect(self.autoFTP_change)

            self.cb_autoTwitch = PyQt5.QtWidgets.QCheckBox(
                _("Auto Twitch Update"))
            self.cb_autoTwitch.setChecked(False)
            self.cb_autoTwitch.stateChanged.connect(self.autoTwitch_change)

            self.cb_autoNightbot = PyQt5.QtWidgets.QCheckBox(
                _("Auto Nightbot Update"))
            self.cb_autoNightbot.setChecked(False)
            self.cb_autoNightbot.stateChanged.connect(
                self.autoNightbot_change)

            if(not scctool.settings.windows):
                self.cb_autoToggleScore.setEnabled(False)
                self.cb_autoToggleScore.setAttribute(
                    PyQt5.QtCore.Qt.WA_AlwaysShowToolTips)
                self.cb_autoToggleScore.setToolTip(_('Only Windows'))
                self.cb_autoToggleProduction.setEnabled(False)
                self.cb_autoToggleProduction.setAttribute(
                    PyQt5.QtCore.Qt.WA_AlwaysShowToolTips)
                self.cb_autoToggleProduction.setToolTip(_('Only Windows'))

            layout = PyQt5.QtWidgets.QGridLayout()

            label = PyQt5.QtWidgets.QLabel()
            label.setFixedWidth(2)
            layout.addWidget(label, 0, 0)
            layout.addWidget(self.cb_autoFTP, 0, 1)
            layout.addWidget(self.cb_autoTwitch, 0, 2)
            layout.addWidget(self.cb_autoNightbot, 0, 3)

            layout.addWidget(self.cb_autoUpdate, 1, 1)
            layout.addWidget(self.cb_playerIntros, 1, 2)
            layout.addWidget(self.cb_autoToggleScore, 1, 3)
            layout.addWidget(self.cb_autoToggleProduction, 1, 4)

            self.backgroundTasksBox.setLayout(layout)

        except Exception as e:
            module_logger.exception("message")

    def autoFTP_change(self):
        """Monitor check box for ftp upload."""
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

    def ftpSignal(self, signal):
        """Define signal handle for ftpUploader."""
        if(signal == -2):
            PyQt5.QtWidgets.QMessageBox.warning(self, _("Login error"),
                                                _('FTP server login incorrect!'))
            self.cb_autoFTP.setChecked(False)
        elif(signal == -3):
            self.progressBar.setVisible(False)
        else:
            self.progressBar.setVisible(True)

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

    def applycustom_click(self):
        """Handle click to apply custom match."""
        try:
            self.trigger = False
            self.statusBar().showMessage(_('Applying Custom Match...'))
            msg = self.controller.applyCustom(int(self.cb_bestof.currentText()),
                                              self.cb_allkill.isChecked(),
                                              self.cb_solo.isChecked(),
                                              int(self.cb_minSets.currentText()),
                                              self.le_url_custom.text().strip())
            self.statusBar().showMessage(msg)
            self.trigger = True
        except Exception as e:
            module_logger.exception("message")

    def resetdata_click(self):
        """Handle click to reset the data."""
        try:
            self.trigger = False
            msg = self.controller.resetData()
            self.statusBar().showMessage(msg)
            self.trigger = True
        except Exception as e:
            module_logger.exception("message")

    def refresh_click(self):
        """Handle click to refresh/load data from an URL."""
        try:
            url = self.le_url.text()
            self.trigger = False
            self.statusBar().showMessage(_('Reading {}...').format(url))
            msg = self.controller.refreshData(url)
            self.statusBar().showMessage(msg)
            self.trigger = True
        except Exception as e:
            module_logger.exception("message")

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

    def resetscore_click(self):
        """Handle click to reset the score."""
        try:
            self.statusBar().showMessage(_('Resetting Score...'))
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
        """Handle change of the score."""
        try:
            if(self.sl_score[idx].value() == 0):
                self.statusBar().showMessage(_('Updating Score...'))
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
        """Handle a new score value."""
        try:
            if(self.trigger):
                self.controller.allkillUpdate()
                self.controller.updateOBS()
        except Exception as e:
            module_logger.exception("message")

    def player_changed(self, team_idx):
        """Handle a change of player names."""
        try:
            if(self.controller.matchData.getSolo()):
                text = self.le_player[team_idx][0].text()
                for player_idx in range(1, self.max_no_sets):
                    self.le_player[team_idx][player_idx].setText(text)

        except Exception as e:
            module_logger.exception("message")

    def race_changed(self, team_idx):
        """Handle a change of player names."""
        try:
            if(self.controller.matchData.getSolo()):
                idx = self.cb_race[team_idx][0].currentIndex()
                for player_idx in range(1, self.max_no_sets):
                    self.cb_race[team_idx][player_idx].setCurrentIndex(idx)

        except Exception as e:
            module_logger.exception("message")

    def logoDialog(self, button):
        """Open dialog for team logo."""
        self.mysubwindows['icons'] = SubwindowIcons()
        self.mysubwindows['icons'].createWindow(self, self.controller)
        self.mysubwindows['icons'].show()
        # options = PyQt5.QtWidgets.QFileDialog.Options()
        # options |= PyQt5.QtWidgets.QFileDialog.DontUseNativeDialog
        
        # fileName, status = PyQt5.QtWidgets.QFileDialog.getOpenFileName(
        #     self, _("Select Team Logo"), "", _("Support Images ({})").format("*.png *.jpg"))
        # if fileName:
        #     try:
        #         os.remove(scctool.settings.getAbsPath(scctool.settings.OBSdataDir +
        #                                               "/logo" + str(button) + ".png"))
        #     except Exception:
        #         pass
        #     try:
        #         os.remove(scctool.settings.getAbsPath(scctool.settings.OBSdataDir +
        #                                               "/logo" + str(button) + ".jpg"))
        #     except Exception:
        #         pass

       ##       base, ext = os.path.splitext(fileName)
        #     ext = ext.split("?")[0]
        #     fname = scctool.settings.OBSdataDir + "/logo" + str(button) + ext

       ##       shutil.copy(fileName, scctool.settings.getAbsPath(fname))
        #     self.controller.updateLogos()
        #     self.controller.ftpUploader.cwd(scctool.settings.OBSdataDir)
        #     self.controller.ftpUploader.upload(
        #         fname, "logo" + str(button) + ext)
        #     self.controller.ftpUploader.cwd("..")
        #     self.controller.matchData.metaChanged()
        #     self.controller.matchData.updateScoreIcon()

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
