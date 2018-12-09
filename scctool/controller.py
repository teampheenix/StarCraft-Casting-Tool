"""Control all other modules."""
import logging
import os
import shutil
import subprocess
import sys
import webbrowser

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QCheckBox, QMessageBox

import scctool.settings
import scctool.tasks.nightbot
import scctool.tasks.twitch
from scctool.matchcontrol import MatchControl
from scctool.settings.alias import AliasManager
from scctool.settings.aligulac import AligulacManager
from scctool.settings.history import HistoryManager
from scctool.settings.logoManager import LogoManager
from scctool.settings.placeholders import PlaceholderList
from scctool.tasks.aligulac import AligulacThread
from scctool.tasks.auth import AuthThread
from scctool.tasks.autorequests import AutoRequestsThread
from scctool.tasks.housekeeper import HouseKeeperThread
from scctool.tasks.mapstats import MapStatsManager
from scctool.tasks.sc2ClientInteraction import (SC2ApiThread, SwapPlayerNames,
                                                ToggleScore)
from scctool.tasks.textfiles import TextFilesThread
from scctool.tasks.texttospeech import TextToSpeech
from scctool.tasks.updater import VersionHandler
from scctool.tasks.websocket import WebsocketThread
from scctool.view.widgets import ToolUpdater
from scctool.tasks.localhost import LocalhostThread

# create logger
module_logger = logging.getLogger(__name__)


class MainController:
    """Control all other modules."""

    def __init__(self):
        """Init controller and connect them with other modules."""
        try:
            self.matchControl = MatchControl(self)
            self.matchControl.readJsonFile()
            # self.matchControl.activeMatch() = matchData(self)
            self.authThread = AuthThread()
            self.authThread.tokenRecived.connect(self.tokenRecived)
            self.textFilesThread = TextFilesThread(self.matchControl)
            self.matchControl.dataChanged.connect(self.handleMatchDataChange)
            self.matchControl.metaChanged.connect(self.matchMetaDataChanged)
            self.SC2ApiThread = SC2ApiThread(self)
            self.SC2ApiThread.requestScoreUpdate.connect(
                self.requestScoreUpdate)
            self.versionHandler = VersionHandler(self)
            self.websocketThread = WebsocketThread(self)
            self.websocketThread.socketConnectionChanged.connect(
                self.toogleLEDs)
            self.websocketThread.introShown.connect(self.updatePlayerIntroIdx)
            self.runWebsocketThread()
            self.aligulacManager = AligulacManager()
            self.aligulacThread = AligulacThread(
                self.matchControl,
                self.websocketThread,
                self.aligulacManager)
            self.autoRequestsThread = AutoRequestsThread(self)
            self._warning = False
            self.checkVersion()
            self.logoManager = LogoManager(self)
            self.aliasManager = AliasManager()
            self.historyManager = HistoryManager()
            self.mapstatsManager = MapStatsManager(self)
            self.tts = TextToSpeech()
            self.localhost = LocalhostThread()
            self.localhost.start(9)
            self.housekeeper = HouseKeeperThread(self)
            self.initPlayerIntroData()

        except Exception as e:
            module_logger.exception("message")
            raise

    def checkVersion(self, force=False):
        """Check for new version."""
        try:
            self.versionHandler.disconnect()
        except Exception:
            pass
        try:
            self.noNewVersion.disconnect()
        except Exception:
            pass

        self.versionHandler.newVersion.connect(
            lambda x: self.newVersion(x, force))
        if force:
            self.versionHandler.noNewVersion.connect(
                lambda: self.displayWarning(_("This version is up to date.")))

        self.versionHandler.activateTask('version_check')

    def placeholderSetup(self):
        """Define and connect placeholders."""
        placeholders = PlaceholderList()

        placeholders.addConnection(
            "Team1", lambda:
            self.matchControl.activeMatch().getTeamOrPlayer(0))
        placeholders.addConnection(
            "Team2", lambda:
            self.matchControl.activeMatch().getTeamOrPlayer(1))
        placeholders.addConnection(
            "URL", self.matchControl.activeMatch().getURL)
        placeholders.addConnection(
            "BestOf",
            lambda: str(self.matchControl.activeMatch().getBestOfRaw()))
        placeholders.addConnection(
            "League", self.matchControl.activeMatch().getLeague)
        placeholders.addConnection(
            "Score", self.matchControl.activeMatch().getScoreString)

        self.placeholders = placeholders

    def setView(self, view):
        """Connect view."""
        self.view = view
        try:
            # self.matchControl.activeMatch().readJsonFile()
            with self.view.tlock:
                self.updateMatchFormat()
            self.setCBs()
            self.view.resizeWindow()
            self.housekeeper.activateTask('save')
            self.housekeeper.alphaMatches.connect(self.view.le_url.updateItems)
            self.housekeeper.activateTask('alphatl')
        except Exception as e:
            module_logger.exception("message")

    def updateMatchFormat(self):
        """Update match format in forms."""
        try:
            if(self.matchControl.selectedMatch().getProvider() == "Custom"):
                self.view.tabs.setCurrentIndex(1)
            else:
                self.view.tabs.setCurrentIndex(0)

            self.view.cb_allkill.setChecked(
                self.matchControl.selectedMatch().getAllKill())

            self.view.cb_solo.setChecked(
                self.matchControl.selectedMatch().getSolo())

            index = self.view.cb_bestof.findText(
                str(self.matchControl.selectedMatch().getBestOfRaw()),
                Qt.MatchFixedString)
            if index >= 0:
                self.view.cb_bestof.setCurrentIndex(index)

            index = self.view.cb_minSets.findText(
                str(self.matchControl.selectedMatch().getMinSets()),
                Qt.MatchFixedString)
            if index >= 0:
                self.view.cb_minSets.setCurrentIndex(index)

            self.view.le_url.setURL(
                self.matchControl.selectedMatch().getURL())
            self.view.le_url_custom.setText(
                self.matchControl.selectedMatch().getURL())

            self.autoSetNextMap()

        except Exception as e:
            module_logger.exception("message")
            raise

    def updateLogos(self, force=False):
        """Updata team logos in  view."""
        idx = self.matchControl.selectedMatchIdx()
        matchWidget = self.view.matchDataTabWidget.widget(idx)
        matchWidget.updateLogos(force)

    def applyCustom(self, bestof, allkill, solo, minSets, url):
        """Apply a custom match format."""
        msg = ''
        try:
            match = self.matchControl.selectedMatch()
            idx = self.matchControl.selectedMatchIdx()
            with match.emitLock(
                    True,
                    match.metaChanged):
                match.setCustom(bestof, allkill, solo)
                match.setMinSets(minSets)
                match.setURL(url)
                self.matchControl.writeJsonFile()
                self.updateMatchFormat()
                matchWidget = self.view.matchDataTabWidget.widget(idx)
                matchWidget.updateForms()
                self.view.resizeWindow()
                if idx == self.matchControl.activeMatchIdx():
                    self.matchControl.selectedMatch().updateLeagueIcon()

        except Exception as e:
            msg = str(e)
            module_logger.exception("message")

        return msg

    def resetData(self):
        """Reset data."""
        msg = ''
        try:
            self.logoManager.resetTeam1Logo()
            self.logoManager.resetTeam2Logo()
            self.matchControl.selectedMatch().resetData(False)
            self.matchControl.writeJsonFile()
            self.updateLogos(True)
            idx = self.matchControl.selectedMatchIdx()
            matchWidget = self.view.matchDataTabWidget.widget(idx)
            matchWidget.updateForms()
            self.updateMatchFormat()

        except Exception as e:
            msg = str(e)
            module_logger.exception("message")

        return msg

    def refreshData(self, url):
        """Load data from match grabber."""
        msg = ''
        try:
            match = self.matchControl.selectedMatch()
            newProvider = match.parseURL(url)
            match.grabData(newProvider, self.logoManager)
            self.matchControl.writeJsonFile()
            try:
                # TODO: Need to have multiple banners
                match.downloadBanner()
            except Exception as e:
                module_logger.exception("message")
                pass
            self.updateLogos(True)
            idx = self.matchControl.selectedMatchIdx()
            matchWidget = self.view.matchDataTabWidget.widget(idx)
            matchWidget.updateForms()
            self.updateMatchFormat()
            self.view.resizeWindow()
            self.matchControl.activeMatch().updateLeagueIcon()

        except Exception as e:
            msg = str(e)
            module_logger.exception("message")

        return msg

    def setCBs(self):
        """Update value of check boxes from config."""
        try:

            self.view.cb_autoUpdate.setChecked(
                scctool.settings.config.parser.getboolean("Form",
                                                          "scoreupdate"))
            network_listener = scctool.settings.config.parser.getboolean(
                "SCT", "sc2_network_listener_enabled")

            if scctool.settings.windows and not network_listener:
                self.view.cb_autoToggleScore.setChecked(
                    scctool.settings.config.parser.getboolean("Form",
                                                              "togglescore"))

                self.view.cb_autoToggleProduction.setChecked(
                    scctool.settings.config.parser.getboolean("Form",
                                                              "toggleprod"))

            self.view.cb_autoTwitch.setChecked(
                scctool.settings.config.parser.getboolean("Form",
                                                          "autotwitch"))
            self.view.cb_autoNightbot.setChecked(
                scctool.settings.config.parser.getboolean("Form",
                                                          "autonightbot"))

        except Exception as e:
            module_logger.exception("message")

    def uncheckCB(self, cb):
        """Uncheck check boxes on error."""
        if(cb == 'twitch'):
            self.view.cb_autoTwitch.setChecked(False)
        elif(cb == 'nightbot'):
            self.view.cb_autoNightbot.setChecked(False)

    def allkillUpdate(self):
        """In case of allkill move the winner to the next set."""
        if(self.matchControl.activeMatch().allkillUpdate()):
            self.matchControl.activeMatch().updateForms()

    def tokenRecived(self, scope, token):
        """Call to return of token."""
        try:
            subwindow = self.view.mysubwindows['connections']
            getattr(subwindow, '{}Token'.format(scope)).setTextMonitored(token)

            self.view.raise_()
            self.view.show()
            self.view.activateWindow()

            subwindow.raise_()
            subwindow.show()
            subwindow.activateWindow()

        except Exception as e:
            module_logger.exception("message")

    def updateNightbotCommand(self):
        """Update nightbot commands."""
        self.autoRequestsThread.activateTask('nightbot_once')

    def updateTwitchTitle(self):
        """Update twitch title."""
        self.autoRequestsThread.activateTask('twitch_once')

    def openURL(self, url):
        """Open URL in Browser."""
        if(len(url) < 5):
            url = "https://teampheenix.github.io/StarCraft-Casting-Tool/"
        try:
            webbrowser.open(url)
        except Exception as e:
            module_logger.exception("message")

    def open_file(self, filename):
        if sys.platform == "win32":
            os.startfile(filename)
        else:
            opener = "open" if sys.platform == "darwin" else "xdg-open"
            subprocess.call([opener, filename])

    def runSC2ApiThread(self, task):
        """Start task in thread that monitors SC2-Client-API."""
        try:
            if(not self.SC2ApiThread.isRunning()):
                self.SC2ApiThread.startTask(task)
            else:
                self.SC2ApiThread.cancelTerminationRequest(task)

        except Exception as e:
            module_logger.exception("message")

    def stopSC2ApiThread(self, task):
        """Stop task in thread thats monitors SC2-Client-API."""
        try:
            self.SC2ApiThread.requestTermination(task)
        except Exception as e:
            module_logger.exception("message")

    def runWebsocketThread(self):
        """Run websocket thread."""
        if(not self.websocketThread.isRunning()):
            self.websocketThread.start()
        else:
            module_logger.exception("Thread is still running")

    def stopWebsocketThread(self):
        """Stop websocket thread."""
        try:
            self.websocketThread.stop()
        except Exception as e:
            module_logger.exception("message")

    def cleanUp(self, save=True):
        """Clean up all threads and save config to close program."""
        try:
            module_logger.info("cleanUp called")
            self.SC2ApiThread.requestTermination("ALL")
            self.authThread.terminate()
            self.localhost.terminate()
            self.stopWebsocketThread()
            self.textFilesThread.terminate()
            self.aligulacThread.terminate()
            self.autoRequestsThread.terminate()
            self.mapstatsManager.close(False)
            self.housekeeper.terminate()
            if save:
                self.saveAll()
        except Exception as e:
            module_logger.exception("message")

    def saveAll(self):
        self.saveConfig()
        self.matchControl.writeJsonFile()
        scctool.settings.saveNightbotCommands()
        self.logoManager.dumpJson()
        self.historyManager.dumpJson()
        self.aliasManager.dumpJson()
        self.aligulacManager.dumpJson()
        self.mapstatsManager.dumpJson()
        self.tts.dumpJson()

    def saveConfig(self):
        """Save the settings to the config file."""
        try:
            scctool.settings.config.parser.set("Form", "scoreupdate", str(
                self.view.cb_autoUpdate.isChecked()))
            scctool.settings.config.parser.set("Form", "togglescore", str(
                self.view.cb_autoToggleScore.isChecked()))
            scctool.settings.config.parser.set("Form", "toggleprod", str(
                self.view.cb_autoToggleProduction.isChecked()))
            scctool.settings.config.parser.set("Form", "autotwitch", str(
                self.view.cb_autoTwitch.isChecked()))
            scctool.settings.config.parser.set("Form", "autonightbot", str(
                self.view.cb_autoNightbot.isChecked()))

            configFile = open(scctool.settings.configFile(),
                              'w', encoding='utf-8-sig')
            scctool.settings.config.parser.write(configFile)
            configFile.close()
        except Exception as e:
            module_logger.exception("message")

    def setRace(self, team_idx, set_idx, race):
        if self.matchControl.activeMatch().setRace(team_idx, set_idx, race):
            race_idx = scctool.settings.race2idx(race)
            matchWidget = self.view.matchDataTabWidget.widget(
                self.matchControl.activeMatchIdx())
            if race_idx != matchWidget.cb_race[team_idx][set_idx].\
                    currentIndex():
                with matchWidget.tlock:
                    matchWidget.cb_race[team_idx][set_idx].setCurrentIndex(
                        race_idx)

    def requestScoreUpdate(self, newSC2MatchData):
        """Update score based on result of SC2-Client-API."""
        try:
            alias = self.aliasManager.translatePlayer
            newscore = 0
            matchWidget = self.view.matchDataTabWidget.widget(
                self.matchControl.activeMatchIdx())

            for j in range(2):
                self.historyManager.insertPlayer(
                    alias(newSC2MatchData.getPlayer(j)),
                    newSC2MatchData.getRace(j))
            self.view.updateAllPlayerCompleters()
            if newSC2MatchData.result == 0:
                return
            for i in range(self.matchControl.activeMatch().getNoSets()):
                player1 = self.matchControl.activeMatch().getPlayer(0, i)
                player2 = self.matchControl.activeMatch().getPlayer(1, i)
                found, in_order, newscore, _ = \
                    newSC2MatchData.compare_returnScore(
                        player1,
                        player2,
                        translator=alias)
                if found:
                    if(matchWidget.setScore(i, newscore)):
                        race1 = newSC2MatchData.getRace(0)
                        race2 = newSC2MatchData.getRace(1)
                        if not in_order:
                            race1, race2 = race2, race1
                        self.setRace(0, i, race1)
                        self.setRace(1, i, race2)
                        break
                    else:
                        continue
            # If not found try again with weak search
            # and set missing playernames
            if not found:
                for i in range(self.matchControl.activeMatch().getNoSets()):
                    player1 = self.matchControl.activeMatch().getPlayer(0, i)
                    player2 = self.matchControl.activeMatch().getPlayer(1, i)
                    found, in_order, newscore, notset_idx \
                        = newSC2MatchData.compare_returnScore(
                            player1, player2, weak=True, translator=alias)
                    if(found and notset_idx in range(2)):
                        if(matchWidget.setScore(i, newscore, allkill=False)):
                            race1 = newSC2MatchData.getRace(0)
                            race2 = newSC2MatchData.getRace(1)
                            if not in_order:
                                race1, race2 = race2, race1
                                player = newSC2MatchData.getPlayer(
                                    1 - notset_idx)
                            else:
                                player = newSC2MatchData.getRace(notset_idx)
                            self.setRace(0, i, race1)
                            self.setRace(1, i, race2)
                            self.matchControl.activeMatch().setPlayer(
                                notset_idx, i, player)
                            with matchWidget.tlock:
                                matchWidget.le_player[notset_idx][i].setText(
                                    player)
                            self.allkillUpdate()
                            break
                        else:
                            continue

        except Exception as e:
            module_logger.exception("message")

    def toggleWidget(self, widget, condition, ttFalse='', ttTrue=''):
        """Disable or an enable a widget based on a condition."""
        widget.setAttribute(Qt.WA_AlwaysShowToolTips)
        widget.setToolTip(ttTrue if condition else ttFalse)
        if not condition:
            try:
                widget.setChecked(False)
            except Exception:
                pass
        widget.setEnabled(condition)

    def refreshButtonStatus(self):
        """Enable or disable buttons depending on config."""
        self.toggleWidget(
            self.view.pb_twitchupdate,
            scctool.settings.config.twitchIsValid(),
            _('Specify your Twitch Settings to use this feature'),
            '')

        txt = _('Automatically update the title of your' +
                ' twitch channel in the background.')
        self.toggleWidget(
            self.view.cb_autoTwitch,
            scctool.settings.config.twitchIsValid(),
            _('Specify your Twitch Settings to use this feature'),
            txt)

        self.toggleWidget(
            self.view.cb_autoNightbot,
            scctool.settings.config.nightbotIsValid(),
            _('Specify your Nightbot Settings to use this feature'),
            _('Automatically update the commands of your' +
              ' nightbot in the background.'))

        self.toggleWidget(
            self.view.pb_nightbotupdate,
            scctool.settings.config.nightbotIsValid(),
            _('Specify your Nightbot Settings to use this feature'),
            '')

        if scctool.settings.windows:

            network_listener = scctool.settings.config.parser.getboolean(
                "SCT", "sc2_network_listener_enabled")

            self.toggleWidget(
                self.view.cb_autoToggleScore,
                not network_listener,
                _('Not available when SC2 is running on a different PC.'),
                _('Automatically sets the score of your ingame' +
                  ' UI-interface at the begining of a game.'))

            self.toggleWidget(
                self.view.cb_autoToggleProduction,
                not network_listener,
                _('Not available when SC2 is running on a different PC.'),
                _('Automatically toggles the production tab of your' +
                  ' ingame UI-interface at the begining of a game.'))

    def requestScoreLogoUpdate(self, data, swap=False):
        module_logger.info("requestScoreLogoUpdate")
        match_ident = self.matchControl.activeMatchId()
        for player_idx in range(2):
            team1 = data.playerInList(
                player_idx,
                self.matchControl.activeMatch().getPlayerList(0),
                self.aliasManager.translatePlayer)
            team2 = data.playerInList(
                player_idx, self.matchControl.activeMatch().getPlayerList(1),
                self.aliasManager.translatePlayer)

            if swap:
                path = 'ui_logo_{}'.format(2 - player_idx)
            else:
                path = 'ui_logo_{}'.format(player_idx + 1)

            if(not team1 and not team2):
                logo = ""
                display = "none"
            elif(team1):
                logo = "../" + \
                    self.logoManager.getTeam1(match_ident).getFile(True)
                display = "block"
            elif(team2):
                logo = "../" + \
                    self.logoManager.getTeam2(match_ident).getFile(True)
                display = "block"

            self.websocketThread.sendData2Path(
                path, 'DATA',
                {'logo': logo, 'display': display})

    def requestToggleScore(self, newSC2MatchData, swap=False):
        """Check if SC2-Client-API players are present"""
        """and toggle score accordingly."""
        try:
            alias = self.aliasManager.translatePlayer
            bo = self.matchControl.activeMatch().getBestOf()

            for i in range(self.matchControl.activeMatch().getNoSets()):
                found, inorder = newSC2MatchData.compare_returnOrder(
                    self.matchControl.activeMatch().getPlayer(0, i),
                    self.matchControl.activeMatch().getPlayer(1, i),
                    translator=alias)
                if found:
                    break
            if not found:
                for i in range(self.matchControl.activeMatch().getNoSets()):
                    found, inorder = newSC2MatchData.compare_returnOrder(
                        self.matchControl.activeMatch().getPlayer(0, i),
                        self.matchControl.activeMatch().getPlayer(1, i),
                        weak=True,
                        translator=alias)
                    if found:
                        break
            if found:
                score = self.matchControl.activeMatch().getScore()
                if swap:
                    inorder = not inorder

                if inorder:
                    ToggleScore(score[0], score[1], bo)
                else:
                    if scctool.settings.config.parser.getboolean(
                            "SCT", "CtrlX"):
                        SwapPlayerNames()
                        ToggleScore(score[0], score[1], bo)
                    else:
                        ToggleScore(score[1], score[0], bo)

            else:
                ToggleScore(0, 0, bo)

        except Exception as e:
            module_logger.exception("message")

    def linkFile(self, file):
        """Return correct img file ending."""
        for ext in [".jpg", ".png"]:
            if(os.path.isfile(scctool.settings.getAbsPath(file + ext))):
                return file + ext
        return ""

    def updateLogosHTML(self, force=False):
        """Update html files with team logos."""
        match_ident = self.matchControl.activeMatchId()
        for idx in range(2):
            logo = self.logoManager.getTeam(idx + 1, match_ident)
            filename = scctool.settings.casting_html_dir + \
                "/data/logo" + str(idx + 1) + "-data.html"
            template = scctool.settings.casting_html_dir + \
                "/data/logo-template.html"
            self.matchControl.activeMatch()._useTemplate(
                template, filename, {'logo': logo.getFile(True)})
            if force:
                self.websocketThread.sendData2Path(
                    'score', 'CHANGE_IMAGE',
                    {'id': 'logo{}'.format(idx + 1),
                     'img': logo.getFile(True)})

    def updateHotkeys(self):
        """Refresh hotkeys."""
        if(self.websocketThread.isRunning()):
            self.websocketThread.unregister_hotkeys(force=True)
            self.websocketThread.register_hotkeys()

    def updatePlayerIntroIdx(self):
        self.__playerIntroIdx = (self.__playerIntroIdx + 1) % 2

    def initPlayerIntroData(self):
        """Initalize player intro data."""
        self.__playerIntroData = dict()
        self.__playerIntroIdx = 0
        for player_idx in range(2):
            data = dict()
            data['name'] = "pressure"
            data['race'] = "protoss"
            data['logo'] = "../" + self.logoManager.newLogo().getFile(True)
            data['team'] = "team pheeniX"
            data['display'] = "block"
            self.__playerIntroData[player_idx] = data

    def getPlayerIntroData(self, idx):
        """Return player intro."""
        if idx == -1:
            idx = self.__playerIntroIdx
        data = self.__playerIntroData[idx]
        data['volume'] = scctool.settings.config.parser.getint(
            "Intros", "sound_volume")
        data['tts_volume'] = scctool.settings.config.parser.getint(
            "Intros", "tts_volume")
        data['display_time'] = scctool.settings.config.parser.getfloat(
            "Intros", "display_time")
        data['animation'] = scctool.settings.config.parser.get(
            "Intros", "animation") .strip().lower()
        if scctool.settings.config.parser.getboolean(
                "Style", "use_custom_font"):
            data['font'] = scctool.settings.config.parser.get(
                "Style", "custom_font")
        return data

    def updatePlayerIntros(self, newData):
        """Update player intro files."""
        module_logger.info("updatePlayerIntros")

        tts_active = scctool.settings.config.parser.getboolean(
            "Intros", "tts_active")
        tts_voice = scctool.settings.config.parser.get(
            "Intros", "tts_voice")
        tts_scope = scctool.settings.config.parser.get(
            "Intros", "tts_scope")
        tts_pitch = scctool.settings.config.parser.getfloat(
            "Intros", "tts_pitch")
        tts_rate = scctool.settings.config.parser.getfloat(
            "Intros", "tts_rate")

        matchID = self.matchControl.activeMatchId()

        for player_idx in range(2):
            team1 = newData.playerInList(
                player_idx,
                self.matchControl.activeMatch().getPlayerList(0),
                self.aliasManager.translatePlayer)
            team2 = newData.playerInList(
                player_idx, self.matchControl.activeMatch().getPlayerList(1),
                self.aliasManager.translatePlayer)

            if(not team1 and not team2):
                team = ""
                logo = ""
                display = "none"
            elif(team1):
                team = self.matchControl.activeMatch().getTeam(0)
                logo = "../" + self.logoManager.getTeam1(matchID).getFile(True)
                display = "block"
            elif(team2):
                team = self.matchControl.activeMatch().getTeam(1)
                logo = "../" + self.logoManager.getTeam2(matchID).getFile(True)
                display = "block"

            name = self.aliasManager.translatePlayer(
                newData.getPlayer(player_idx))
            race = newData.getRace(player_idx)
            self.__playerIntroData[player_idx]['name'] = name
            self.__playerIntroData[player_idx]['team'] = team
            self.__playerIntroData[player_idx]['race'] = race.lower()
            self.__playerIntroData[player_idx]['logo'] = logo
            self.__playerIntroData[player_idx]['display'] = display
            self.__playerIntroIdx = 0

            try:
                if tts_active:
                    if team.strip().lower() == 'tbd':
                        team = ''
                    text = self.tts.getLine(tts_scope, name, race, team)
                    tts_file = os.path.join("..", self.tts.synthesize(
                        text, tts_voice,
                        tts_pitch, tts_rate)).replace('\\', '/')
                else:
                    tts_file = None
                self.__playerIntroData[player_idx]['tts'] = tts_file

            except Exception as e:
                self.__playerIntroData[player_idx]['tts'] = None
                module_logger.exception("message")

    def getMapImg(self, map, fullpath=False):
        """Get map image from map name."""
        if map == 'TBD':
            return map
        mapdir = scctool.settings.getAbsPath(
            scctool.settings.casting_html_dir)
        mapimg = os.path.normpath(os.path.join(
            mapdir, "src/img/maps", map.replace(" ", "_")))
        mapimg = os.path.basename(self.linkFile(mapimg))
        if not mapimg:
            mapimg = "TBD"
            self.displayWarning(_("Warning: Map '{}' not found!").format(map))

        if(fullpath):
            return os.path.normpath(os.path.join(
                mapdir, "src/img/maps", mapimg))
        else:
            return mapimg

    def addMap(self, file, mapname):
        """Add a new map via file and name."""
        _, ext = os.path.splitext(file)
        mapdir = scctool.settings.getAbsPath(
            scctool.settings.casting_html_dir)
        map = mapname.strip().replace(" ", "_") + ext.lower()
        newfile = os.path.normpath(os.path.join(mapdir, "src/img/maps", map))
        shutil.copy(file, newfile)
        if mapname not in scctool.settings.maps:
            scctool.settings.maps.append(mapname)

    def deleteMap(self, map):
        """Delete map and file."""
        os.remove(self.getMapImg(map, True))
        scctool.settings.maps.remove(map)

    def swapTeams(self):
        with self.view.tlock:
            self.logoManager.swapTeamLogos(self.matchControl.selectedMatchId())
            self.matchControl.selectedMatch().swapTeams()
            idx = self.matchControl.selectedMatchIdx()
            matchWidget = self.view.matchDataTabWidget.widget(idx)
            matchWidget.updateForms()
            matchWidget.updateLogos(False)

    def displayWarning(self, msg="Warning: Something went wrong..."):
        """Display a warning in status bar."""
        msg = _(msg)
        self._warning = True
        self.view.statusBar().showMessage(msg)

    def resetWarning(self):
        """Display or reset warning now."""
        warning = self._warning
        self._warning = False
        return warning

    def showMap(self, player_idx):
        self.mapstatsManager.selectMap(
            self.matchControl.activeMatch().getMap(player_idx))

    def toogleLEDs(self, num, path, view=None):
        """Indicate when browser sources are connected."""
        if not view:
            view = self.view
        view.leds[path].setChecked(num > 0)
        name = path.replace('_', ' ').title()
        view.leds[path].setToolTip(
            _("{} {} Browser Source(s) connected.").format(num, name))
        if path == 'intro':
            if num > 0:
                self.runSC2ApiThread("playerIntros")
            else:
                self.stopSC2ApiThread("playerIntros")
        if path == 'ui_logo':
            if num > 0:
                self.runSC2ApiThread("playerLogos")
            else:
                self.stopSC2ApiThread("playerLogos")
        if path == 'aligulac':
            if num > 0:
                self.aligulacThread.activate()
                self.aligulacThread.receive_data('meta')
                # view.toogleAligulacTab(True)
            else:
                self.aligulacThread.terminate()
                # view.toogleAligulacTab(False)

    def autoSetNextMap(self, idx=-1, send=True):
        if scctool.settings.config.parser.getboolean(
                "Mapstats", "autoset_next_map"):
            self.mapstatsManager.selectMap(
                self.matchControl.activeMatch().getNextMap(idx), send)

    def matchMetaDataChanged(self):
        data = self.matchControl.activeMatch().getScoreData()
        self.websocketThread.sendData2Path("score", "ALL_DATA", data)
        data = self.matchControl.activeMatch().getMapIconsData()

        for type in ['box', 'landscape']:
            for idx in range(0, 3):
                path = 'mapicons_{}_{}'.format(type, idx + 1)
                scope = 'scope_{}_{}'.format(type, idx + 1)
                scope = scctool.settings.config.parser.get("MapIcons", scope)
                if not self.matchControl.activeMatch().isValidScope(scope):
                    scope = 'all'
                processedData = dict()
                self.websocketThread.mapicon_sets[path] = set()
                for idx in self.matchControl.activeMatch().parseScope(scope):
                    processedData[idx + 1] = data[idx + 1]
                    self.websocketThread.mapicon_sets[path].add(idx + 1)
                self.websocketThread.sendData2Path(path,
                                                   'DATA',
                                                   processedData)

    def handleMatchDataChange(self, label, object):
        if label == 'team':
            if not self.matchControl.activeMatch().getSolo():
                self.websocketThread.sendData2Path(
                    'score', 'CHANGE_TEXT',
                    {'id': 'team{}'.format(object['idx'] + 1),
                     'text': object['value']})
        elif label == 'score':
            score = self.matchControl.activeMatch().getScore()
            for idx in range(0, 2):
                self.websocketThread.sendData2Path(
                    'score', 'CHANGE_TEXT', {
                        'id': 'score{}'.format(idx + 1),
                        'text': str(score[idx])})
                color = self.matchControl.activeMatch().getScoreIconColor(
                    idx, object['set_idx'])
                self.websocketThread.sendData2Path(
                    'score', 'CHANGE_SCORE', {
                        'teamid': idx + 1,
                        'setid': object['set_idx'] + 1,
                        'color': color})
            colorData = self.matchControl.activeMatch(
            ).getColorData(object['set_idx'])
            self.websocketThread.sendData2Path(
                ['mapicons_box', 'mapicons_landscape'],
                'CHANGE_SCORE', {
                    'winner': object['value'],
                    'setid': object['set_idx'] + 1,
                    'score_color': colorData['score_color'],
                    'border_color': colorData['border_color'],
                    'hide': colorData['hide'],
                    'opacity': colorData['opacity']})
            if scctool.settings.config.parser.getboolean(
                    "Mapstats", "mark_played",):
                map = self.matchControl.activeMatch().getMap(object['set_idx'])
                played = object['value'] != 0
                self.websocketThread.sendData2Path(
                    'mapstats', 'MARK_PLAYED', {'map': map, 'played': played})
        elif label == 'color':
            for idx in range(0, 2):
                self.websocketThread.sendData2Path(
                    'score', 'CHANGE_SCORE', {
                        'teamid': idx + 1,
                        'setid': object['set_idx'] + 1,
                        'color': object['score_color']})
            self.websocketThread.sendData2Path(
                ['mapicons_box', 'mapicons_landscape'],
                'CHANGE_SCORE', {
                    'winner': 0,
                    'setid': object['set_idx'] + 1,
                    'score_color': object['score_color'],
                    'border_color': object['border_color'],
                    'hide': object['hide'],
                    'opacity': object['opacity']})
        elif label == 'color-data':
            self.websocketThread.sendData2Path(
                ['mapicons_box', 'mapicons_landscape'], 'CHANGE_SCORE', {
                    'winner': object['score'],
                    'setid': object['set_idx'] + 1,
                    'score_color': object['score_color'],
                    'border_color': object['border_color'],
                    'hide': object['hide'],
                    'opacity': object['opacity']})
        elif label == 'outcome':
            self.websocketThread.sendData2Path('score', 'SET_WINNER', object)
        elif label == 'player':
            self.websocketThread.sendData2Path(
                ['mapicons_box', 'mapicons_landscape'],
                'CHANGE_TEXT', {
                    'icon': object['set_idx'] + 1,
                    'label': 'player{}'.format(object['team_idx'] + 1),
                    'text': object['value']})
            if(object['set_idx'] == 0 and
                    self.matchControl.activeMatch().getSolo()):
                self.websocketThread.sendData2Path(
                    'score', 'CHANGE_TEXT',
                    {'id': 'team{}'.format(object['team_idx'] + 1),
                     'text': object['value']})
        elif label == 'race':
            self.websocketThread.sendData2Path(
                ['mapicons_box', 'mapicons_landscape'],
                'CHANGE_RACE', {
                    'icon': object['set_idx'] + 1,
                    'team': object['team_idx'] + 1,
                    'race': object['value'].lower()})
        elif label == 'map':
            self.websocketThread.sendData2Path(
                ['mapicons_box', 'mapicons_landscape'],
                'CHANGE_MAP', {
                    'icon': object['set_idx'] + 1,
                    'map': object['value'],
                    'map_img': self.getMapImg(object['value'])})

        data = self.matchControl.activeMatch().getMapIconsData()
        for type in ['box', 'landscape']:
            for idx in range(0, 3):
                path = 'mapicons_{}_{}'.format(type, idx + 1)
                if len(self.websocketThread.connected.get(path, set())) > 0:
                    processedData = dict()
                    for set_idx in \
                            self.websocketThread.compareMapIconSets(path):
                        processedData[set_idx] = data[set_idx]
                    if(len(processedData) > 0):
                        self.websocketThread.sendData2Path(path,
                                                           'DATA',
                                                           processedData)

    def newVersion(self, version, force=False):
        """Display dialog for new version."""
        prompt = force or scctool.settings.config.parser.getboolean(
            "SCT", "new_version_prompt")
        if hasattr(sys, "frozen") and prompt:
            messagebox = QMessageBox()
            text = _("A new version {} is available.")
            messagebox.setText(text.format(version))
            messagebox.setInformativeText(_("Update to new version?"))
            messagebox.setWindowTitle(_("New SCC-Tool Version"))
            messagebox.setStandardButtons(
                QMessageBox.Yes | QMessageBox.No)
            messagebox.setDefaultButton(QMessageBox.Yes)
            messagebox.setIcon(QMessageBox.Information)
            messagebox.setWindowModality(Qt.ApplicationModal)
            cb = QCheckBox()
            cb.setChecked(not scctool.settings.config.parser.getboolean(
                "SCT", "new_version_prompt"))
            cb.setText(_("Don't show on startup."))
            messagebox.setCheckBox(cb)
            if messagebox.exec_() == QMessageBox.Yes:
                ToolUpdater(self, self.view)
            scctool.settings.config.parser.set("SCT",
                                               "new_version_prompt",
                                               str(not cb.isChecked()))
        else:
            self.view.statusBar().showMessage(
                _("A new version {} is available on GitHub!").format(version))
