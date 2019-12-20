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
import scctool.settings.translation
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

# create logger
module_logger = logging.getLogger(__name__)

_ = scctool.settings.translation.gettext


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
            self.housekeeper = HouseKeeperThread(self)
            self.initPlayerIntroData()
            self._my_ip = ''

        except Exception:
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
            "Race1", lambda:
            self.matchControl.activeMatch().getNextRace(0)[0])
        placeholders.addConnection(
            "Race2", lambda:
            self.matchControl.activeMatch().getNextRace(1)[0])
        placeholders.addConnection(
            "URL", self.matchControl.activeMatch().getURL)
        placeholders.addConnection(
            "BestOf",
            lambda: str(self.matchControl.activeMatch().getBestOf()))
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
            self.housekeeper.ip_updated.connect(self.update_ip)
            self.housekeeper.activateTask('check_ip')
        except Exception:
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

            ace_sets = self.matchControl.selectedMatch().getAceSets()
            index = self.view.cb_ace_bo.findText(
                str(ace_sets),
                Qt.MatchFixedString)
            if index >= 0:
                self.view.cb_ace_bo.setCurrentIndex(index)
            self.view.cb_extend_ace.setChecked(ace_sets > 0)

            index = self.view.cb_minSets.findText(
                str(self.matchControl.selectedMatch().getMinSets()),
                Qt.MatchFixedString)
            if index >= 0:
                self.view.cb_minSets.setCurrentIndex(index)

            self.view.le_url.setURL(
                self.matchControl.selectedMatch().getURL())
            self.view.le_url_custom.setText(
                self.matchControl.selectedMatch().getURL())

            vetoes = self.matchControl.selectedMatch().getNoVetoes()
            index = self.view.cb_vetoes.findText(
                str(vetoes),
                Qt.MatchFixedString)
            if index >= 0:
                self.view.cb_vetoes.setCurrentIndex(index)

            idx = self.matchControl.selectedMatchIdx()
            matchWidget = self.view.matchDataTabWidget.widget(idx)
            if matchWidget is not None:
                matchWidget.toggleVetoes(vetoes > 0)

            self.autoSetNextMap()

        except Exception:
            module_logger.exception("message")
            raise

    def updateLogos(self, force=False):
        """Update team logos in  view."""
        idx = self.matchControl.selectedMatchIdx()
        matchWidget = self.view.matchDataTabWidget.widget(idx)
        matchWidget.updateLogos(force)

    def applyCustom(self, bestof, allkill, solo,
                    minSets, url, vetoes, extend_ace):
        """Apply a custom match format."""
        msg = ''
        try:
            match = self.matchControl.selectedMatch()
            idx = self.matchControl.selectedMatchIdx()
            with match.emitLock(
                    True,
                    match.metaChanged):
                match.setCustom(bestof, allkill, solo, extend_ace, vetoes)
                match.setMinSets(minSets)
                match.setURL(url)
                self.matchControl.writeJsonFile()
                self.updateMatchFormat()
                matchWidget = self.view.matchDataTabWidget.widget(idx)
                matchWidget.updateForms()
                self.view.resizeWindow()
                if idx == self.matchControl.activeMatchIdx():
                    self.matchControl.selectedMatch().updateLeagueIcon()

        except Exception:
            module_logger.exception("message")

        return msg

    def resetData(self):
        """Reset the match data."""
        msg = ''
        try:
            self.matchControl.selectedMatch().resetData(False)
            self.logoManager.resetTeam1Logo()
            self.logoManager.resetTeam2Logo()
            self.matchControl.writeJsonFile()
            self.updateLogos(True)
            idx = self.matchControl.selectedMatchIdx()
            matchWidget = self.view.matchDataTabWidget.widget(idx)
            matchWidget.updateForms()
            self.updateMatchFormat()

        except Exception:
            module_logger.exception("message")

        return msg

    def refreshData(self, url, update_progress=lambda *args, **kwargs: None):
        """Load data from match grabber."""
        msg = ''
        try:
            match = self.matchControl.selectedMatch()
            newProvider = match.parseURL(url)
            update_progress(20)
            match.grabData(newProvider, self.logoManager)
            update_progress(80)
            self.matchControl.writeJsonFile()
            try:
                # TODO: Need to have multiple banners
                match.downloadBanner()
            except Exception:
                module_logger.exception("message")
            update_progress(90)
            self.updateLogos(True)
            idx = self.matchControl.selectedMatchIdx()
            matchWidget = self.view.matchDataTabWidget.widget(idx)
            matchWidget.updateForms()
            update_progress(95)
            self.updateMatchFormat()
            self.view.resizeWindow()
            self.matchControl.activeMatch().updateLeagueIcon()
            update_progress(99)

        except Exception:
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

        except Exception:
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

        except Exception:
            module_logger.exception("message")

    def updateNightbotCommand(self):
        """Update nightbot commands."""
        self.autoRequestsThread.activateTask('nightbot_once')

    def updateTwitchTitle(self):
        """Update twitch title."""
        self.autoRequestsThread.activateTask('twitch_once')

    @classmethod
    def openURL(cls, url):
        """Open URL in Browser."""
        if(len(url) < 5):
            url = "https://teampheenix.github.io/StarCraft-Casting-Tool/"
        try:
            webbrowser.open(url)
        except Exception:
            module_logger.exception("message")

    @classmethod
    def open_file(cls, filename):
        """Open a local file."""
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

        except Exception:
            module_logger.exception("message")

    def stopSC2ApiThread(self, task):
        """Stop task in thread thats monitors SC2-Client-API."""
        try:
            self.SC2ApiThread.requestTermination(task)
        except Exception:
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
        except Exception:
            module_logger.exception("message")

    def cleanUp(self, save=True):
        """Clean up all threads and save config to close program."""
        try:
            module_logger.info("cleanUp called")
            self.SC2ApiThread.requestTermination("ALL")
            self.authThread.terminate()
            self.stopWebsocketThread()
            self.textFilesThread.terminate()
            self.aligulacThread.terminate()
            self.autoRequestsThread.terminate()
            self.mapstatsManager.close(False)
            self.housekeeper.terminate()
            if save:
                self.saveAll()
        except Exception:
            module_logger.exception("message")

    def saveAll(self):
        """Save everything."""
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
        except Exception:
            module_logger.exception("message")

    def setRace(self, team_idx, set_idx, race):
        """Set the race of a player."""
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

        except Exception:
            module_logger.exception("message")

    @classmethod
    def toggleWidget(cls, widget, condition, ttFalse='', ttTrue=''):
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

        txt = _('Automatically update the title of your'
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
            _('Automatically update the commands of your'
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
                _('Automatically sets the score of your ingame'
                  ' UI-interface at the begining of a game.'))

            self.toggleWidget(
                self.view.cb_autoToggleProduction,
                not network_listener,
                _('Not available when SC2 is running on a different PC.'),
                _('Automatically toggles the production tab of your'
                  ' ingame UI-interface at the begining of a game.'))

    def requestScoreLogoUpdate(self, data, swap=False):
        """Request a update of the score logos."""
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
        """Check if players are present in sc2 api and toggle score."""
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

        except Exception:
            module_logger.exception("message")

    @classmethod
    def linkFile(cls, file):
        """Return correct img file ending."""
        for ext in [".jpg", ".jpeg", ".png"]:
            if(os.path.isfile(scctool.settings.getAbsPath(file + ext))):
                return file + ext
        return ""

    def updateLogosWebsocket(self):
        """Update logos in browser sources via websocket."""
        match_ident = self.matchControl.activeMatchId()
        for idx in range(2):
            logo = self.logoManager.getTeam(idx + 1, match_ident)
            self.websocketThread.sendData2Path(
                'logo_{}'.format(idx + 1), 'DATA',
                {'logo': logo.getFile(True)})

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
        """Alternate between player intros."""
        self.__playerIntroIdx = (self.__playerIntroIdx + 1) % 2

    def initPlayerIntroData(self):
        """Init player intro data."""
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
                player_idx,
                self.matchControl.activeMatch().getPlayerList(1),
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

            except Exception:
                self.__playerIntroData[player_idx]['tts'] = None
                module_logger.exception("message")

    def getMapImg(self, mapname, fullpath=False):
        """Get map image from map name."""
        if mapname == 'TBD':
            return mapname
        mapdir = scctool.settings.getAbsPath(
            scctool.settings.casting_html_dir)
        mapimg = os.path.normpath(os.path.join(
            mapdir, "src/img/maps", mapname.replace(" ", "_")))
        mapimg = os.path.basename(self.linkFile(mapimg))
        if not mapimg:
            mapimg = "TBD"
            self.displayWarning(
                _("Warning: Map '{}' not found!").format(mapname))

        if(fullpath):
            return os.path.normpath(os.path.join(
                mapdir, "src/img/maps", mapimg))
        else:
            return mapimg

    @classmethod
    def addMap(cls, file, mapname):
        """Add a new map via file and name."""
        __, ext = os.path.splitext(file)
        mapdir = scctool.settings.getAbsPath(
            scctool.settings.casting_html_dir)
        mapname = mapname.strip()
        sc2map = mapname.replace(" ", "_") + ext.lower()
        newfile = os.path.normpath(
            os.path.join(mapdir, "src/img/maps", sc2map))
        shutil.copy(file, newfile)
        if mapname not in scctool.settings.maps:
            scctool.settings.maps.append(mapname)

    def deleteMap(self, mapname):
        """Delete map and file."""
        os.remove(self.getMapImg(mapname, True))
        scctool.settings.maps.remove(mapname)

    def swapTeams(self):
        """Swap teams from left to right."""
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
        """Show a specific map on the mapstats browser source."""
        self.mapstatsManager.selectMap(
            self.matchControl.activeMatch().getMap(player_idx))

    def getBrowserSourceURL(self, file, external=False):
        """Return the URL of a browser source."""
        file = file.replace('\\', '/')
        file = file.replace('.html', '')
        if external and self._my_ip:
            ip = self._my_ip
        else:
            ip = 'localhost'
        return f'http://{ip}:{self.websocketThread.get_port()}/{file}'

    def toogleLEDs(self, num, path, view=None):
        """Indicate when browser sources are connected."""
        if not view:
            view = self.view
        view.leds[path].setChecked(num > 0)
        name = path.replace('_', ' ').title()
        port = self.websocketThread.get_port()
        view.leds[path].setToolTip(
            _("{} {} Browser Source(s) connected on port {}.").format(
                num, name, port))
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
        """Select the next map to be shown on the mapstats browser source."""
        if scctool.settings.config.parser.getboolean(
                "Mapstats", "autoset_next_map"):
            self.mapstatsManager.selectMap(
                self.matchControl.activeMatch().getNextMap(idx), send)

    def matchMetaDataChanged(self):
        """Send new data to all browser sources triggered by a meta change."""
        data = self.matchControl.activeMatch().getScoreData()
        self.websocketThread.sendData2Path("score", "ALL_DATA", data)
        data = self.matchControl.activeMatch().getMapIconsData()

        for boxtype in ['box', 'landscape']:
            for idx in range(0, 3):
                path = f'mapicons_{boxtype}_{idx + 1}'
                scope = f'scope_{boxtype}_{idx + 1}'
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
        data = self.matchControl.activeMatch().getVetoData()
        self.websocketThread.sendData2Path('vetoes', "DATA", data)

    def handleTeamChange(self, obj):
        if not self.matchControl.activeMatch().getSolo():
            self.websocketThread.sendData2Path(
                'score', 'CHANGE_TEXT',
                {'id': 'team{}'.format(obj['idx'] + 1),
                 'text': obj['value']})

    def handleBoChange(self, obj):
        self.websocketThread.sendData2Path(
            'score', 'CHANGE_TEXT', {
                'id': 'bestof',
                'text': f"{obj['value']}"})

    def handleScoreChange(self, obj):
        score = self.matchControl.activeMatch().getScore()
        for idx in range(0, 2):
            self.websocketThread.sendData2Path(
                'score', 'CHANGE_TEXT', {
                    'id': 'score{}'.format(idx + 1),
                    'text': str(score[idx])})
            color = self.matchControl.activeMatch().getScoreIconColor(
                idx, obj['set_idx'])
            self.websocketThread.sendData2Path(
                'score', 'CHANGE_SCORE', {
                    'teamid': idx + 1,
                    'setid': obj['set_idx'] + 1,
                    'color': color})
        colorData = self.matchControl.activeMatch(
        ).getColorData(obj['set_idx'])
        self.websocketThread.sendData2Path(
            ['mapicons_box', 'mapicons_landscape'],
            'CHANGE_SCORE', {
                'winner': obj['value'],
                'setid': obj['set_idx'] + 1,
                'score_color': colorData['score_color'],
                'border_color': colorData['border_color'],
                'hide': colorData['hide'],
                'opacity': colorData['opacity']})
        if scctool.settings.config.parser.getboolean(
                "Mapstats", "mark_played",):
            sc2_map = self.matchControl.activeMatch().getMap(
                obj['set_idx'])
            played = obj['value'] != 0
            self.websocketThread.sendData2Path(
                'mapstats', 'MARK_PLAYED',
                {'map': sc2_map, 'played': played})

    def handleVetoChange(self, obj):
        if scctool.settings.config.parser.getboolean(
                "Mapstats", "mark_vetoed",):
            sc2_map = obj.get('map')
            old_map = obj.get('old_map')
            if(old_map != sc2_map
               and old_map != 'TBD'
               and not self.matchControl.activeMatch().isMapVetoed(
                   old_map)):
                self.websocketThread.sendData2Path(
                    'mapstats', 'MARK_VETOED',
                    {'map': old_map, 'vetoed': False})
            if sc2_map.lower() != 'tbd':
                self.websocketThread.sendData2Path(
                    'mapstats', 'MARK_VETOED',
                    {'map': sc2_map, 'vetoed': True})
        self.websocketThread.sendData2Path(
            'vetoes', "VETO",
            {'idx': obj['idx'],
             'map_name': obj['map'],
             'map_img': self.getMapImg(obj['map']),
             'team': obj['team']
             })

    def handleColorChange(self, obj):
        for idx in range(0, 2):
            self.websocketThread.sendData2Path(
                'score', 'CHANGE_SCORE', {
                    'teamid': idx + 1,
                    'setid': obj['set_idx'] + 1,
                    'color': obj['score_color']})
        self.websocketThread.sendData2Path(
            ['mapicons_box', 'mapicons_landscape'],
            'CHANGE_SCORE', {
                'winner': 0,
                'setid': obj['set_idx'] + 1,
                'score_color': obj['score_color'],
                'border_color': obj['border_color'],
                'hide': obj['hide'],
                'opacity': obj['opacity']})

    def handleColorDataChange(self, obj):
        self.websocketThread.sendData2Path(
            ['mapicons_box', 'mapicons_landscape'], 'CHANGE_SCORE', {
                'winner': obj['score'],
                'setid': obj['set_idx'] + 1,
                'score_color': obj['score_color'],
                'border_color': obj['border_color'],
                'hide': obj['hide'],
                'opacity': obj['opacity']})

    def handlePlayerChange(self, obj):
        self.websocketThread.sendData2Path(
            ['mapicons_box', 'mapicons_landscape'],
            'CHANGE_TEXT', {
                'icon': obj['set_idx'] + 1,
                'label': 'player{}'.format(obj['team_idx'] + 1),
                'text': obj['value']})
        if(obj['set_idx'] == 0
                and self.matchControl.activeMatch().getSolo()):
            self.websocketThread.sendData2Path(
                'score', 'CHANGE_TEXT',
                {'id': 'team{}'.format(obj['team_idx'] + 1),
                 'text': obj['value']})

    def handleRaceChange(self, obj):
        self.websocketThread.sendData2Path(
            ['mapicons_box', 'mapicons_landscape'],
            'CHANGE_RACE', {
                'icon': obj['set_idx'] + 1,
                'team': obj['team_idx'] + 1,
                'race': obj['value'].lower()})

    def handleMapChange(self, obj):
        self.websocketThread.sendData2Path(
            ['mapicons_box', 'mapicons_landscape'],
            'CHANGE_MAP', {
                'icon': obj['set_idx'] + 1,
                'map': obj['value'],
                'map_img': self.getMapImg(obj['value'])})

    def handleMatchDataChange(self, label, obj):
        """Send new data to browser sources due to a change of the map data."""
        if label == 'team':
            self.handleTeamChange(obj)
        elif label == 'bestof':
            self.handleBoChange(obj)
        elif label == 'score':
            self.handleScoreChange(obj)
        elif label == 'map_veto':
            self.handleVetoChange(obj)
        elif label == 'color':
            self.handleColorChange(obj)
        elif label == 'color-data':
            self.handleColorDataChange(obj)
        elif label == 'outcome':
            self.websocketThread.sendData2Path('score', 'SET_WINNER', obj)
        elif label == 'player':
            self.handlePlayerChange(obj)
        elif label == 'race':
            self.handleRaceChange(obj)
        elif label == 'map':
            self.handleMapChange(obj)

        data = self.matchControl.activeMatch().getMapIconsData()
        for icon_type in ['box', 'landscape']:
            for idx in range(0, 3):
                path = f'mapicons_{icon_type}_{idx + 1}'
                if len(self.websocketThread.connected.get(path, set())) > 0:
                    processedData = dict()
                    for set_idx in \
                            self.websocketThread.compareMapIconSets(path):
                        processedData[set_idx] = data[set_idx]
                    if(len(processedData) > 0):
                        self.websocketThread.sendData2Path(path,
                                                           'DATA',
                                                           processedData)

    def update_ip(self, ip):
        """Save the current external ip."""
        self._my_ip = ip

    def newVersion(self, version, force=False):
        """Display dialog for new version."""
        prompt = force or scctool.settings.config.parser.getboolean(
            "SCT", "new_version_prompt")
        if hasattr(sys, "frozen") and prompt:
            messagebox = QMessageBox()
            text = _("A new version {} is available.")
            messagebox.setText(text.format(version))
            messagebox.setInformativeText(_("Update to new version?"))
            messagebox.setWindowTitle(_("New StarCraft Casting Tool Version"))
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
