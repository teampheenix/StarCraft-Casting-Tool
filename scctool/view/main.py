"""Define the main window."""
import logging
import os

import markdown2
from PyQt5.QtCore import QSettings, Qt
from PyQt5.QtGui import QIcon, QPalette
from PyQt5.QtWidgets import (QAction, QApplication, QCheckBox, QComboBox,
                             QCompleter, QFormLayout, QGridLayout, QGroupBox,
                             QHBoxLayout, QLabel, QMainWindow, QMenu,
                             QMessageBox, QPushButton, QTabWidget, QToolButton,
                             QVBoxLayout, QWidget)

import scctool.settings
import scctool.settings.config
from scctool.settings.client_config import ClientConfig
from scctool.view.countdown import CountdownWidget
from scctool.view.matchdataview import MatchDataWidget
from scctool.view.subBrowserSources import SubwindowBrowserSources
from scctool.view.subConnections import SubwindowConnections
from scctool.view.subLogos import SubwindowLogos
from scctool.view.subMarkdown import SubwindowMarkdown
from scctool.view.subMisc import SubwindowMisc
from scctool.view.subOverlay import SubwindowOverlay
from scctool.view.subStyles import SubwindowStyles
from scctool.view.widgets import (LedIndicator, MatchComboBox,
                                  MonitoredLineEdit, ProfileMenu)

# create logger
module_logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """Show the main window of SCCT."""

    EXIT_CODE_REBOOT = -123

    def __init__(self, controller, app, showChangelog):
        """Init the main window."""
        try:
            super().__init__()

            self._save = True
            self.tlock = TriggerLock()
            self.controller = controller

            self.max_no_sets = scctool.settings.max_no_sets
            self.scoreWidth = 35
            self.raceWidth = 45
            self.labelWidth = 25
            self.mimumLineEditWidth = 130

            self.createTabs()
            self.createMatchDataTabs()
            self.createHorizontalGroupBox()
            self.createLowerTabWidget()

            self.createMenuBar()

            mainLayout = QVBoxLayout()
            mainLayout.addWidget(self.tabs, 0)
            mainLayout.addWidget(self.matchDataTabWidget, 1)
            # mainLayout.addWidget(self.fromMatchDataBox, 1)
            mainLayout.addWidget(self.lowerTabWidget, 0)
            mainLayout.addWidget(self.horizontalGroupBox, 0)

            self.setWindowTitle(
                "StarCraft Casting Tool v{}".format(scctool.__version__))

            self.window = QWidget()
            self.window.setLayout(mainLayout)
            self.setCentralWidget(self.window)

            # self.size
            self.statusBar()

            self.leds = dict()
            for scope in self.controller.websocketThread.get_primary_scopes():
                self.leds[scope] = LedIndicator(self)

            for key, led in self.leds.items():
                self.controller.toogleLEDs(0, key, self)
                self.statusBar().addPermanentWidget(led)

            self.app = app
            self.controller.setView(self)
            self.controller.refreshButtonStatus()

            self.processEvents()
            self.settings = QSettings(
                ClientConfig.APP_NAME, ClientConfig.COMPANY_NAME)
            self.restoreGeometry(self.settings.value(
                "geometry", self.saveGeometry()))
            self.restoreState(self.settings.value(
                "windowState", self.saveState()))

            self.mysubwindows = dict()

            self.show()
            self.raise_()

            if showChangelog:
                self.openChangelog()

        except Exception as e:
            module_logger.exception("message")

    def showAbout(self):
        """Show subwindow with about info."""
        html = markdown2.markdown_path(
            scctool.settings.getResFile("about.md"))

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
                self.controller.cleanUp(self._save)
                QMainWindow.closeEvent(self, event)
                # event.accept()
        except Exception as e:
            module_logger.exception("message")

    def createMenuBar(self):
        """Create the menu bar."""
        try:
            menubar = self.menuBar()
            settingsMenu = menubar.addMenu(_('Settings'))

            apiAct = QAction(QIcon(scctool.settings.getResFile(
                'browser.png')), _('Browser Sources'), self)
            apiAct.setToolTip(
                _('Edit Settings for all Browser Sources'))
            apiAct.triggered.connect(self.openBrowserSourcesDialog)
            settingsMenu.addAction(apiAct)
            apiAct = QAction(QIcon(scctool.settings.getResFile(
                'twitch.png')), _('Twitch && Nightbot'), self)
            apiAct.setToolTip(
                _('Edit Intro-Settings and API-Settings'
                  ' for Twitch and Nightbot'))
            apiAct.triggered.connect(self.openApiDialog)
            settingsMenu.addAction(apiAct)
            styleAct = QAction(QIcon(scctool.settings.getResFile(
                'pantone.png')), _('Styles'), self)
            styleAct.setToolTip('')
            styleAct.triggered.connect(self.openStyleDialog)
            settingsMenu.addAction(styleAct)
            miscAct = QAction(QIcon(scctool.settings.getResFile(
                'settings.png')), _('Misc'), self)
            miscAct.setToolTip('')
            miscAct.triggered.connect(self.openMiscDialog)
            settingsMenu.addAction(miscAct)

            self.createBrowserSrcMenu()

            ProfileMenu(self, self.controller)

            self.createLangMenu()

            infoMenu = menubar.addMenu(_('Info && Links'))

            myAct = QAction(QIcon(scctool.settings.getResFile(
                'about.png')), _('About'), self)
            myAct.triggered.connect(self.showAbout)
            infoMenu.addAction(myAct)

            myAct = QAction(QIcon(scctool.settings.getResFile(
                'readme.ico')), _('Readme'), self)
            myAct.triggered.connect(self.openReadme)
            infoMenu.addAction(myAct)

            websiteAct = QAction(
                QIcon(
                    scctool.settings.getResFile('youtube.png')),
                _('Video Tutorial'), self)
            websiteAct.triggered.connect(lambda: self.controller.openURL(
                "https://youtu.be/j5iWa4JB8bM"))
            infoMenu.addAction(websiteAct)

            myAct = QAction(QIcon(scctool.settings.getResFile(
                'update.png')), _('Check for new version'), self)
            myAct.triggered.connect(lambda: self.controller.checkVersion(True))
            infoMenu.addAction(myAct)

            myAct = QAction(QIcon(scctool.settings.getResFile(
                'changelog.png')), _('Changelog'), self)
            myAct.triggered.connect(self.openChangelog)
            infoMenu.addAction(myAct)

            myAct = QAction(QIcon(scctool.settings.getResFile(
                'folder.png')), _('Open log folder'), self)
            myAct.triggered.connect(lambda: self.controller.open_file(
                scctool.settings.getAbsPath(scctool.settings.getLogDir())))
            infoMenu.addAction(myAct)

            infoMenu.addSeparator()

            websiteAct = QAction(
                QIcon(
                    scctool.settings.getResFile('scct.ico')),
                'StarCraft Casting Tool', self)
            websiteAct.triggered.connect(lambda: self.controller.openURL(
                "https://teampheenix.github.io/StarCraft-Casting-Tool/"))
            infoMenu.addAction(websiteAct)

            discordAct = QAction(
                QIcon(
                    scctool.settings.getResFile('discord.png')),
                'Discord', self)
            discordAct.triggered.connect(lambda: self.controller.openURL(
                "https://discord.gg/G9hFEfh"))
            infoMenu.addAction(discordAct)

            ixAct = QAction(QIcon(scctool.settings.getResFile(
                'icon.png')), 'team pheeniX', self)
            ixAct.triggered.connect(
                lambda: self.controller.openURL("http://team-pheenix.de"))
            infoMenu.addAction(ixAct)

            alphaAct = QAction(QIcon(scctool.settings.getResFile(
                'alpha.png')), 'AlphaTL', self)
            alphaAct.triggered.connect(
                lambda: self.controller.openURL("https://alpha.tl"))
            infoMenu.addAction(alphaAct)

            rstlAct = QAction(QIcon(scctool.settings.getResFile(
                'rstl.png')), 'RSTL', self)
            rstlAct.triggered.connect(
                lambda: self.controller.openURL("http://hdgame.net/en/"))
            infoMenu.addAction(rstlAct)

            infoMenu.addSeparator()

            myAct = QAction(QIcon(scctool.settings.getResFile(
                'patreon.png')), _('Become a Patron'), self)
            myAct.triggered.connect(lambda: self.controller.openURL(
                "https://www.patreon.com/StarCraftCastingTool"))
            infoMenu.addAction(myAct)

            myAct = QAction(QIcon(scctool.settings.getResFile(
                'donate.ico')), _('Donate via PayPal'), self)
            myAct.triggered.connect(lambda: self.controller.openURL(
                "https://paypal.me/StarCraftCastingTool"))
            infoMenu.addAction(myAct)

        except Exception as e:
            module_logger.exception("message")

    def createLangMenu(self):
        menubar = self.menuBar()

        langMenu = menubar.addMenu(_('Language'))

        language = scctool.settings.config.parser.get("SCT", "language")

        languages = []
        languages.append({'handle': 'de_DE', 'icon': 'de.png',
                          'name': 'Deutsch', 'active': True})
        languages.append({'handle': 'en_US', 'icon': 'en.png',
                          'name': 'English', 'active': True})
        languages.append({'handle': 'fr_FR', 'icon': 'fr.png',
                          'name': 'Français', 'active': True})
        languages.append({'handle': 'ru_RU', 'icon': 'ru.png',
                          'name': 'Pусский', 'active': True})

        for lang in languages:
            myAct = QAction(QIcon(scctool.settings.getResFile(
                lang['icon'])), lang['name'], self, checkable=True)
            myAct.setChecked(language == lang['handle'])
            myAct.setDisabled(not lang['active'])
            myAct.triggered.connect(
                lambda x, handle=lang['handle']: self.changeLanguage(handle))
            langMenu.addAction(myAct)

    def createBrowserSrcMenu(self):
        menubar = self.menuBar()
        main_menu = menubar.addMenu(_('Browser Sources'))

        srcs = []
        srcs.append({'name': _('Intro'),
                     'file': 'intro.html',
                     'settings': lambda: self.openBrowserSourcesDialog(
                     'intro')})
        srcs.append({'name': _('Mapstats'),
                     'file': 'mapstats.html',
                     'settings': lambda: self.openBrowserSourcesDialog(
                     'mapstats')})
        srcs.append({'name': _('Score'),
                     'file': 'score.html'})
        srcs.append({'name': _('Map Icons Box'),
                     'settings': lambda: self.openBrowserSourcesDialog(
                     'mapicons_box'),
                     'sub': [{'name': _('Icon Set {}').format(1),
                              'file': 'mapicons_box_1.html'},
                             {'name': _('Icon Set {}').format(2),
                              'file': 'mapicons_box_2.html'},
                             {'name': _('Icon Set {}').format(3),
                              'file': 'mapicons_box_3.html'}]})
        srcs.append({'name': _('Map Icons Landscape'),
                     'settings': lambda: self.openBrowserSourcesDialog(
                     "mapicons_landscape"),
                     'sub': [{'name': _('Icon Set {}').format(1),
                              'file': 'mapicons_landscape_1.html'},
                             {'name': _('Icon Set {}').format(2),
                              'file': 'mapicons_landscape_2.html'},
                             {'name': _('Icon Set {}').format(3),
                              'file': 'mapicons_landscape_3.html'}]})
        srcs.append({'name': _('Misc'),
                     'sub': [{'name': _('Logo {}').format(1),
                              'file': 'logo1.html'},
                             {'name': _('Logo {}').format(2),
                              'file': 'logo2.html'},
                             {'name': _('UI Logo {}').format(1),
                              'file': 'ui_logo_1.html'},
                             {'name': _('UI Logo {}').format(2),
                              'file': 'ui_logo_2.html'},
                             {'name': _('Aligulac (only 1vs1)'),
                              'file': 'aligulac.html'},
                             {'name': _('Countdown'),
                              'file': 'countdown.html'},
                             {'name': _('League (ALphaTL && RSTL only)'),
                              'file': 'league.html'},
                             {'name': _('Matchbanner (AlphaTL)'),
                              'file': 'matchbanner.html',
                              'settings': lambda:
                              self.openMiscDialog('alphatl')}
                             ]})

        act = QAction(QIcon(scctool.settings.getResFile(
            'folder.png')), _('Open Folder'), self)
        act.triggered.connect(lambda: self.controller.open_file(
            scctool.settings.getAbsPath(scctool.settings.casting_html_dir)))
        main_menu.addAction(act)
        main_menu.addSeparator()

        for src in srcs:
            myMenu = QMenu(src['name'], self)
            sub = src.get('sub', False)
            if sub:
                for icon in sub:
                    mySubMenu = QMenu(icon['name'], self)
                    icon['file'] = os.path.join(
                        scctool.settings.casting_html_dir, icon['file'])
                    act = QAction(QIcon(scctool.settings.getResFile(
                        'html.png')), _('Open in Browser'), self)
                    act.triggered.connect(
                        lambda x,
                        file=icon['file']: self.controller.openURL(
                            scctool.settings.getAbsPath(file)))
                    mySubMenu.addAction(act)
                    act = QAction(QIcon(scctool.settings.getResFile(
                        'copy.png')), _('Copy URL to Clipboard'), self)
                    act.triggered.connect(
                        lambda x, file=icon['file']:
                        QApplication.clipboard().setText(
                            scctool.settings.getAbsPath(file)))
                    mySubMenu.addAction(act)
                    if icon.get('settings', None) is not None:
                        act = QAction(QIcon(scctool.settings.getResFile(
                            'browser.png')), _('Settings'), self)
                        act.triggered.connect(icon['settings'])
                        mySubMenu.addAction(act)
                    myMenu.addMenu(mySubMenu)
            else:
                src['file'] = os.path.join(
                    scctool.settings.casting_html_dir, src['file'])
                act = QAction(QIcon(scctool.settings.getResFile(
                    'html.png')), _('Open in Browser'), self)
                act.triggered.connect(
                    lambda x,
                    file=src['file']: self.controller.openURL(
                        scctool.settings.getAbsPath(file)))
                myMenu.addAction(act)
                act = QAction(QIcon(scctool.settings.getResFile(
                    'copy.png')), _('Copy URL to Clipboard'), self)
                act.triggered.connect(
                    lambda x, file=src['file']:
                    QApplication.clipboard().setText(
                        scctool.settings.getAbsPath(file)))
                myMenu.addAction(act)

            if src.get('settings', None) is not None:
                act = QAction(QIcon(scctool.settings.getResFile(
                    'browser.png')), _('Settings'), self)
                act.triggered.connect(src['settings'])
                myMenu.addAction(act)
            main_menu.addMenu(myMenu)

        main_menu.addSeparator()

        apiAct = QAction(QIcon(scctool.settings.getResFile(
            'browser.png')), _('Settings'), self)
        apiAct.setToolTip(
            _('Edit Settings for all Browser Sources'))
        apiAct.triggered.connect(self.openBrowserSourcesDialog)
        main_menu.addAction(apiAct)

        styleAct = QAction(QIcon(scctool.settings.getResFile(
            'pantone.png')), _('Styles'), self)
        styleAct.setToolTip('')
        styleAct.triggered.connect(self.openStyleDialog)
        main_menu.addAction(styleAct)

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

    def openMiscDialog(self, tab=''):
        """Open subwindow with misc settings."""
        self.mysubwindows['misc'] = SubwindowMisc()
        self.mysubwindows['misc'].createWindow(self, tab)
        self.mysubwindows['misc'].show()

    def openBrowserSourcesDialog(self, tab=''):
        """Open subwindow with misc settings."""
        self.mysubwindows['browser'] = SubwindowBrowserSources()
        self.mysubwindows['browser'].createWindow(self, tab)
        self.mysubwindows['browser'].show()

    def openReadme(self):
        """Open subwindow with readme viewer."""
        self.mysubwindows['readme'] = SubwindowMarkdown()
        self.mysubwindows['readme'].createWindow(
            self, _("Readme"),
            scctool.settings.getResFile('readme.ico'),
            scctool.settings.getResFile("../README.md"))
        self.mysubwindows['readme'].show()

    def openChangelog(self):
        """Open subwindow with readme viewer."""
        self.mysubwindows['changelog'] = SubwindowMarkdown()
        self.mysubwindows['changelog'].createWindow(
            self, "StarCraft Casting Tool " + _("Changelog"),
            scctool.settings.getResFile("changelog.png"),
            scctool.settings.getResFile("../CHANGELOG.md"))
        self.mysubwindows['changelog'].show()

    def showOverlay(self, toogle):
        """Opens a subwindow that is used as an ingame overlay."""
        window = self.mysubwindows.get('overlay', False)
        if(window and window.isVisible()):
            window.close()
        else:
            self.mysubwindows['overlay'] = SubwindowOverlay()
            self.mysubwindows['overlay'].createWindow(self)
            self.mysubwindows['overlay'].showMaximized()

    def changeLanguage(self, language):
        """Change the language."""
        scctool.settings.config.parser.set("SCT", "language", language)
        self.restart()

    def updateAllMapCompleters(self):
        for idx in range(self.matchDataTabWidget.count()):
            self.matchDataTabWidget.widget(idx).updateMapCompleters()

    def updateAllPlayerCompleters(self):
        for idx in range(self.matchDataTabWidget.count()):
            self.matchDataTabWidget.widget(idx).updatePlayerCompleters()

    def updateAllMapButtons(self):
        for idx in range(self.matchDataTabWidget.count()):
            self.matchDataTabWidget.widget(idx).updateMapButtons()

    def createMatchDataTabs(self):
        self.matchDataTabWidget = QTabWidget()
        self.matchDataTabWidget.setMovable(True)
        closeable = self.controller.matchControl.countMatches() > 1
        self.matchDataTabWidget.setUsesScrollButtons(True)
        for match in self.controller.matchControl.getMatches():
            MatchDataWidget(self,
                            self.matchDataTabWidget,
                            match, closeable)

        container = QWidget()
        buttonLayout = QHBoxLayout()
        buttonLayout.setContentsMargins(2, 1, 1, 2)
        buttonLayout.setSpacing(1)
        button = QPushButton()
        pixmap = QIcon(scctool.settings.getResFile('add.png'))
        button.setIcon(pixmap)
        button.setFixedSize(28, 28)
        # button.setFlat(True)
        button.setToolTip(_('Add Match Tab'))
        button.clicked.connect(self.addMatchTab)
        buttonLayout.addWidget(button)
        button = QPushButton()
        button.setFixedSize(28, 28)
        pixmap = QIcon(scctool.settings.getResFile('copy.png'))
        button.setIcon(pixmap)
        # button.setFlat(True)
        button.setToolTip(_('Copy Match Tab'))
        button.clicked.connect(self.copyMatchTab)
        buttonLayout.addWidget(button)
        container.setLayout(buttonLayout)
        self.matchDataTabWidget.setCornerWidget(container)

        tabBar = self.matchDataTabWidget.tabBar()
        tabBar.setExpanding(True)
        self.matchDataTabWidget.currentChanged.connect(
            self.currentMatchTabChanged)
        tabBar.tabMoved.connect(self.tabMoved)

    def addMatchTab(self):
        match = self.controller.matchControl.newMatchData()
        MatchDataWidget(self,
                        self.matchDataTabWidget,
                        match)
        count = self.matchDataTabWidget.count()
        self.matchDataTabWidget.setCurrentIndex(count - 1)
        if count > 1:
            for idx in range(count):
                self.matchDataTabWidget.widget(idx).setClosable(True)

    def copyMatchTab(self):
        matchId = self.controller.matchControl.selectedMatchId()
        data = self.controller.matchControl.selectedMatch().getData()
        match = self.controller.matchControl.newMatchData(data)
        self.controller.logoManager.copyMatch(match.getControlID(), matchId)
        MatchDataWidget(self,
                        self.matchDataTabWidget,
                        match)
        count = self.matchDataTabWidget.count()
        self.matchDataTabWidget.setCurrentIndex(count - 1)
        if count > 1:
            for idx in range(count):
                self.matchDataTabWidget.widget(idx).setClosable(True)

    def currentMatchTabChanged(self, idx):
        dataWidget = self.matchDataTabWidget.widget(idx)
        ident = dataWidget.matchData.getControlID()
        self.controller.matchControl.selectMatch(ident)
        with self.tlock:
            self.controller.updateMatchFormat()

    def tabMoved(self, toIdx, fromIdx):
        self.controller.matchControl.updateOrder(toIdx, fromIdx)

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

            self.le_url = MatchComboBox(self)
            self.le_url.returnPressed.connect(self.refresh_click)

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
                scctool.settings.getResFile('alpha.png'))
            button.setIcon(pixmap)
            button.clicked.connect(
                lambda: self.controller.openURL("https://alpha.tl/"))
            container.addWidget(button, 0)
            button = QPushButton()
            pixmap = QIcon(
                scctool.settings.getResFile('rstl.png'))
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
            string = _('"Best of 6/4": First, a Bo5/3 is played and the'
                       ' ace map gets extended to a Bo3 if needed;'
                       ' Best of 2: Bo3 with only two maps played.')
            self.cb_bestof.setToolTip(string)
            self.cb_bestof.setMaximumWidth(45)
            self.cb_bestof.currentIndexChanged.connect(self.changeBestOf)
            container.addWidget(self.cb_bestof, 0)

            container.addWidget(QLabel(_(" but at least")), 0)

            self.cb_minSets = QComboBox()

            self.cb_minSets.setToolTip(
                _('Minimum number of maps played (even if the match'
                  ' is decided already)'))
            self.cb_minSets.setMaximumWidth(45)
            container.addWidget(self.cb_minSets, 0)
            container.addWidget(
                QLabel(" " + _("maps") + "  "), 0)
            self.cb_minSets.currentIndexChanged.connect(
                lambda idx: self.highlightApplyCustom())

            self.cb_allkill = QCheckBox(_("All-Kill Format"))
            self.cb_allkill.setChecked(False)
            self.cb_allkill.setToolTip(
                _('Winner stays and is automatically'
                  ' placed into the next set'))
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

            self.pb_applycustom = QToolButton()
            action = QAction(_("Apply Format"))
            action.triggered.connect(self.applycustom_click)
            self.pb_applycustom.setDefaultAction(action)
            self.custom_menu = QMenu(self.pb_applycustom)
            for format, icon in \
                    self.controller.matchControl.getCustomFormats():
                if icon:
                    action = self.custom_menu.addAction(
                        QIcon(scctool.settings.getResFile(icon)), format)
                else:
                    action = self.custom_menu.addAction(format)
                action.triggered.connect(
                    lambda x, format=format: self.applyCustomFormat(format))
            self.pb_applycustom.setMenu(self.custom_menu)
            self.pb_applycustom.setPopupMode(QToolButton.MenuButtonPopup)

            self.pb_applycustom.setFixedWidth(150)
            container.addWidget(self.pb_applycustom, 0)

            self.defaultButtonPalette = self.pb_applycustom.palette()

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
                _('Optionally specify the Match-URL,'
                  ' e.g., for Nightbot commands'))
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
            self.controller.matchControl.\
                selectedMatch().setAllKill(self.cb_allkill.isChecked())
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

            layout.addWidget(self.pb_twitchupdate)
            layout.addWidget(self.pb_nightbotupdate)
            layout.addWidget(self.pb_resetscore)

            self.horizontalGroupBox.setLayout(layout)

        except Exception as e:
            module_logger.exception("message")

    def createLowerTabWidget(self):
        """Create the tab widget at the bottom."""
        try:
            self.lowerTabWidget = QTabWidget()
            self.createBackgroundTasksTab()
            self.countdownTab = CountdownWidget(self.controller, self)
            self.lowerTabWidget.addTab(
                self.backgroundTasksTab,
                _("Background Tasks"))
            self.lowerTabWidget.addTab(
                self.countdownTab,
                _("Countdown"))
        except Exception as e:
            module_logger.exception("message")

    def createBackgroundTasksTab(self):
        """Create group box for background tasks."""
        try:

            self.backgroundTasksTab = QWidget()

            self.cb_autoUpdate = QCheckBox(
                _("Auto Score Update"))
            self.cb_autoUpdate.setChecked(False)
            string = _('Automatically detects the outcome' +
                       ' of SC2 matches that are ' +
                       'played/observed in your SC2-client' +
                       ' and updates the score accordingly.')
            self.cb_autoUpdate.setToolTip(string)
            self.cb_autoUpdate.stateChanged.connect(self.autoUpdate_change)

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

            self.cb_showOverlay = QCheckBox(
                _("Show Overlay"))
            self.cb_showOverlay.setChecked(False)
            self.cb_showOverlay.stateChanged.connect(self.showOverlay)

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

            layout.addWidget(self.cb_autoTwitch, 0, 0)
            layout.addWidget(self.cb_autoNightbot, 0, 1)
            layout.addWidget(self.cb_showOverlay, 0, 2)

            layout.addWidget(self.cb_autoUpdate, 1, 0)
            layout.addWidget(self.cb_autoToggleScore, 1, 1)
            layout.addWidget(self.cb_autoToggleProduction, 1, 2)

            self.backgroundTasksTab.setLayout(layout)

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
                self.controller.matchControl.\
                    selectedMatch().applyCustomFormat(format)
                self.controller.updateMatchFormat()
                matchWidget = self.matchDataTabWidget.currentWidget()
                matchWidget.updateForms()
                self.resizeWindow()
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
                msg = self.controller.applyCustom(
                    int(self.cb_bestof.currentText()),
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
            url = self.le_url.lineEdit().text()
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

    def resetscore_click(self, myteam=False):
        """Handle click to reset the score."""
        try:
            self.statusBar().showMessage(_('Resetting Score...'))
            with self.tlock:
                matchDataWidget = self.matchDataTabWidget.currentWidget()
                for set_idx in range(self.max_no_sets):
                    matchDataWidget.sl_score[set_idx].setValue(0)
                    self.controller.matchControl.selectedMatch().setMapScore(
                        set_idx, 0, overwrite=True)
                self.controller.autoSetNextMap()
                if myteam:
                    matchDataWidget.sl_team.setValue(0)
                    self.controller.matchControl.selectedMatch().setMyTeam(0)
                if not self.controller.resetWarning():
                    self.statusBar().showMessage('')

        except Exception as e:
            module_logger.exception("message")

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

    def logoDialog(self, team, matchDataWidget):
        """Open dialog for team logo."""
        self.controller.logoManager.resetLogoChanged()
        self.mysubwindows['icons'] = SubwindowLogos()
        self.mysubwindows['icons'].createWindow(
            self, self.controller, team, matchDataWidget)
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

    def restart(self, save=True):
        """Restart the main window."""
        self._save = save
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
