"""Control all other modules."""
import logging
import os
import shutil
import sys
import webbrowser

import gtts
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QCheckBox, QMessageBox

import scctool.settings
import scctool.tasks.nightbot
import scctool.tasks.twitch
from scctool.matchdata import matchData
from scctool.settings.alias import AliasManager
from scctool.settings.history import HistoryManager
from scctool.settings.logoManager import LogoManager
from scctool.settings.placeholders import PlaceholderList
from scctool.tasks.autorequests import AutoRequestsThread
from scctool.tasks.mapstats import MapStatsManager
from scctool.tasks.sc2ClientInteraction import (SC2ApiThread, SwapPlayerNames,
                                                ToggleScore)
from scctool.tasks.textfiles import TextFilesThread
from scctool.tasks.updater import VersionHandler
from scctool.tasks.webapp import FlaskThread
from scctool.tasks.websocket import WebsocketThread
from scctool.view.widgets import ToolUpdater

# create logger
module_logger = logging.getLogger('scctool.controller')


class MainController:
    """Control all other modules."""
    webApp = FlaskThread()

    def __init__(self):
        """Init controller and connect them with other modules."""
        try:
            self.matchData = matchData(self)
            self.textFilesThread = TextFilesThread(self.matchData)
            self.matchData.dataChanged.connect(self.handleMatchDataChange)
            self.matchData.metaChangedSignal.connect(self.matchMetaDataChanged)
            self.SC2ApiThread = SC2ApiThread(self)
            self.SC2ApiThread.requestScoreUpdate.connect(
                self.requestScoreUpdate)
            self.versionHandler = VersionHandler(self)
            self.webApp.signal_twitch.connect(self.webAppDone_twitch)
            self.webApp.signal_nightbot.connect(self.webAppDone_nightbot)
            self.websocketThread = WebsocketThread(self)
            self.websocketThread.socketConnectionChanged.connect(
                self.toogleLEDs)
            self.runWebsocketThread()
            self.autoRequestsThread = AutoRequestsThread(self)
            self.placeholderSetup()
            self._warning = False
            self.checkVersion()
            self.initPlayerIntroData()
            self.logoManager = LogoManager(self)
            self.aliasManager = AliasManager()
            self.historyManager = HistoryManager()
            self.mapstatsManager = MapStatsManager(self)

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
        self.placeholders = PlaceholderList()

        self.placeholders.addConnection("Team1", lambda:
                                        self.matchData.getTeamOrPlayer(0))
        self.placeholders.addConnection("Team2", lambda:
                                        self.matchData.getTeamOrPlayer(1))
        self.placeholders.addConnection("URL", self.matchData.getURL)
        self.placeholders.addConnection(
            "BestOf", lambda: str(self.matchData.getBestOfRaw()))
        self.placeholders.addConnection("League", self.matchData.getLeague)
        self.placeholders.addConnection("Score", self.matchData.getScoreString)

    def setView(self, view):
        """Connect view."""
        self.view = view
        try:
            self.matchData.readJsonFile()
            with self.view.tlock:
                self.updateForms()
            self.setCBs()
            self.view.resizeWindow()
        except Exception as e:
            module_logger.exception("message")

    def updateForms(self):
        """Update data in froms."""
        try:
            if(self.matchData.getProvider() == "Custom"):
                self.view.tabs.setCurrentIndex(1)
            else:
                self.view.tabs.setCurrentIndex(0)

            self.view.cb_allkill.setChecked(self.matchData.getAllKill())

            self.view.cb_solo.setChecked(self.matchData.getSolo())

            index = self.view.cb_bestof.findText(
                str(self.matchData.getBestOfRaw()),
                Qt.MatchFixedString)
            if index >= 0:
                self.view.cb_bestof.setCurrentIndex(index)

            index = self.view.cb_minSets.findText(
                str(self.matchData.getMinSets()),
                Qt.MatchFixedString)
            if index >= 0:
                self.view.cb_minSets.setCurrentIndex(index)

            self.view.le_url.setText(self.matchData.getURL())
            self.view.le_url_custom.setText(self.matchData.getURL())
            self.view.le_league.setText(self.matchData.getLeague())
            self.view.sl_team.setValue(self.matchData.getMyTeam())
            for i in range(2):
                team = self.matchData.getTeam(i)
                self.view.le_team[i].setText(team)
                self.historyManager.insertTeam(team)

            for j in range(2):
                for i in range(1, self.matchData.getNoSets()):
                    self.view.le_player[j][i].setReadOnly(
                        self.matchData.getSolo())

            for i in range(min(self.view.max_no_sets,
                               self.matchData.getNoSets())):
                for j in range(2):
                    player = self.matchData.getPlayer(j, i)
                    race = self.matchData.getRace(j, i)
                    self.view.le_player[j][i].setText(player)
                    self.view.cb_race[j][i].setCurrentIndex(
                        scctool.settings.race2idx(race))
                    self.historyManager.insertPlayer(player, race)

                self.view.le_map[i].setText(self.matchData.getMap(i))

                self.view.sl_score[i].setValue(self.matchData.getMapScore(i))

            for i in range(self.matchData.getNoSets(), self.view.max_no_sets):
                for j in range(2):
                    self.view.le_player[j][i].hide()
                    self.view.cb_race[j][i].hide()
                self.view.le_map[i].hide()
                self.view.sl_score[i].hide()
                self.view.label_set[i].hide()

            for i in range(min(self.view.max_no_sets,
                               self.matchData.getNoSets())):
                for j in range(2):
                    self.view.le_player[j][i].show()
                    self.view.cb_race[j][i].show()
                self.view.le_map[i].show()
                self.view.sl_score[i].show()
                self.view.label_set[i].show()

            self.view.updatePlayerCompleters()
            self.view.updateTeamCompleters()
            self.updateMapButtons()

        except Exception as e:
            module_logger.exception("message")
            raise

    def updateLogos(self, force=False):
        """Updata team logos in  view."""

        logo = self.logoManager.getTeam1()
        self.view.qb_logo1.setIcon(QIcon(logo.provideQPixmap()))

        logo = self.logoManager.getTeam2()
        self.view.qb_logo2.setIcon(QIcon(logo.provideQPixmap()))

        self.updateLogosHTML(force)

    def applyCustom(self, bestof, allkill, solo, minSets, url):
        """Apply a custom match format."""
        msg = ''
        try:

            self.matchData.setCustom(bestof, allkill, solo)
            self.matchData.setMinSets(minSets)
            self.matchData.setURL(url)
            self.matchData.writeJsonFile()
            self.updateForms()
            self.view.resizeWindow()
            self.matchData.updateLeagueIcon()

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
            self.matchData.resetData(False)
            self.matchData.writeJsonFile()
            self.updateLogos(True)
            self.updateForms()

        except Exception as e:
            msg = str(e)
            module_logger.exception("message")

        return msg

    def refreshData(self, url):
        """Load data from match grabber."""
        msg = ''
        try:
            newProvider = self.matchData.parseURL(url)
            self.matchData.grabData(newProvider, self.logoManager)
            self.matchData.writeJsonFile()
            try:
                self.matchData.downloadBanner()
            except Exception:
                pass
            self.updateLogos(True)
            self.updateForms()
            self.view.resizeWindow()
            self.matchData.updateLeagueIcon()

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

            if scctool.settings.windows:
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
        if(self.matchData.allkillUpdate()):
            self.updateForms()

    def webAppDone_nightbot(self):
        """Call to return of nightbot token."""
        try:
            self.view.mysubwindow1.nightbotToken.setTextMonitored(
                FlaskThread._single.token_nightbot)

            self.view.raise_()
            self.view.show()
            self.view.activateWindow()

            self.view.mysubwindow1.raise_()
            self.view.mysubwindow1.show()
            self.view.mysubwindow1.activateWindow()

        except Exception as e:
            module_logger.exception("message")

    def webAppDone_twitch(self):
        """Call to return of twitch token."""
        try:
            self.view.mysubwindow1.twitchToken.setTextMonitored(
                FlaskThread._single.token_twitch)

            self.view.raise_()
            self.view.show()
            self.view.activateWindow()

            self.view.mysubwindow1.raise_()
            self.view.mysubwindow1.show()
            self.view.mysubwindow1.activateWindow()

        except Exception as e:
            module_logger.exception("message")

    def getNightbotToken(self):
        """Get nightbot token."""
        try:
            self.webApp.start()
            webbrowser.open("http://localhost:65010/nightbot")
        except Exception as e:
            module_logger.exception("message")

    def getTwitchToken(self):
        """Get twitch token."""
        try:
            self.webApp.start()
            webbrowser.open("http://localhost:65010/twitch")
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
            url = "http://alpha.tl/match/2392"
        try:
            webbrowser.open(url)
        except Exception as e:
            module_logger.exception("message")

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
            self.webApp.terminate()
            self.stopWebsocketThread()
            self.textFilesThread.terminate()
            self.autoRequestsThread.terminate()
            self.mapstatsManager.close(False)
            if save:
                self.saveAll()
        except Exception as e:
            module_logger.exception("message")

    def saveAll(self):
        self.saveConfig()
        self.matchData.writeJsonFile()
        scctool.settings.saveNightbotCommands()
        self.logoManager.dumpJson()
        self.historyManager.dumpJson()
        self.aliasManager.dumpJson()
        self.mapstatsManager.dumpJson()

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
        if self.matchData.setRace(team_idx, set_idx, race):
            race_idx = scctool.settings.race2idx(race)
            if race_idx != self.view.cb_race[team_idx][set_idx].currentIndex():
                with self.view.tlock:
                    self.view.cb_race[team_idx][set_idx].setCurrentIndex(
                        race_idx)

    def requestScoreUpdate(self, newSC2MatchData):
        """Update score based on result of SC2-Client-API."""
        try:
            alias = self.aliasManager.translatePlayer
            newscore = 0
            for j in range(2):
                self.historyManager.insertPlayer(
                    alias(newSC2MatchData.getPlayer(j)),
                    newSC2MatchData.getRace(j))
            self.view.updatePlayerCompleters()
            if newSC2MatchData.result == 0:
                return
            for i in range(self.matchData.getNoSets()):
                player1 = self.matchData.getPlayer(0, i)
                player2 = self.matchData.getPlayer(1, i)
                found, in_order, newscore, _ = \
                    newSC2MatchData.compare_returnScore(
                        player1,
                        player2,
                        translator=alias)
                if found:
                    if(self.view.setScore(i, newscore)):
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
                for i in range(self.matchData.getNoSets()):
                    player1 = self.matchData.getPlayer(0, i)
                    player2 = self.matchData.getPlayer(1, i)
                    found, in_order, newscore, notset_idx \
                        = newSC2MatchData.compare_returnScore(
                            player1, player2, weak=True, translator=alias)
                    if(found and notset_idx in range(2)):
                        if(self.view.setScore(i, newscore, allkill=False)):
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
                            self.matchData.setPlayer(notset_idx, i, player)
                            with self.view.tlock:
                                self.view.le_player[notset_idx][i].setText(
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
        if condition:
            tooltip = ttTrue
        else:
            tooltip = ttFalse
        widget.setToolTip(tooltip)
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

    def requestToggleScore(self, newSC2MatchData, swap=False):
        """Check if SC2-Client-API players are present"""
        """and toggle score accordingly."""
        try:
            alias = self.aliasManager.translatePlayer

            for i in range(self.matchData.getNoSets()):
                found, inorder = newSC2MatchData.compare_returnOrder(
                    self.matchData.getPlayer(0, i),
                    self.matchData.getPlayer(1, i),
                    translator=alias)
                if found:
                    break
            if not found:
                for i in range(self.matchData.getNoSets()):
                    found, inorder = newSC2MatchData.compare_returnOrder(
                        self.matchData.getPlayer(0, i),
                        self.matchData.getPlayer(1, i),
                        weak=True,
                        translator=alias)
                    if found:
                        break
            if found:
                score = self.matchData.getScore()
                if swap:
                    inorder = not inorder

                if inorder:
                    ToggleScore(score[0], score[1],
                                self.matchData.getBestOf())
                else:
                    if scctool.settings.config.parser.getboolean(
                            "SCT", "CtrlX"):
                        SwapPlayerNames()
                        ToggleScore(score[0], score[1],
                                    self.matchData.getBestOf())
                    else:
                        ToggleScore(score[1], score[0],
                                    self.matchData.getBestOf())

            else:
                ToggleScore(0, 0, self.matchData.getBestOf())

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
        for idx in range(2):
            logo = getattr(self.logoManager, 'getTeam{}'.format(idx + 1))()
            filename = scctool.settings.casting_html_dir + \
                "/data/logo" + str(idx + 1) + "-data.html"
            template = scctool.settings.casting_html_dir + \
                "/data/logo-template.html"
            self.matchData._useTemplate(
                template, filename, {'logo': logo.getFile(True)})
            if force:
                self.websocketThread.sendData2Path(
                    'score', 'CHANGE_IMAGE',
                    {'id': 'logo{}'.format(idx + 1),
                     'img': logo.getFile(True)})

    def updateHotkeys(self):
        """Refresh hotkeys."""
        if(self.websocketThread.isRunning()):
            self.websocketThread.unregister_hotkeys()
            self.websocketThread.register_hotkeys()

    def initPlayerIntroData(self):
        """Initalize player intro data."""
        self.__playerIntroData = dict()
        for player_idx in range(2):
            data = dict()
            data['name'] = ""
            data['race'] = "random"
            data['logo'] = ""
            data['team'] = ""
            data['display'] = "none"
            self.__playerIntroData[player_idx] = data

    def getPlayerIntroData(self, idx):
        """Return player intro."""
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
        tts_lang = scctool.settings.config.parser.get(
            "Intros", "tts_lang")
        tts_scope = scctool.settings.config.parser.get(
            "Intros", "tts_scope")

        for player_idx in range(2):
            team1 = newData.playerInList(
                player_idx,
                self.matchData.getPlayerList(0),
                self.aliasManager.translatePlayer)
            team2 = newData.playerInList(
                player_idx, self.matchData.getPlayerList(1),
                self.aliasManager.translatePlayer)

            if(not team1 and not team2):
                team = ""
                logo = ""
                display = "none"
            elif(team1):
                team = self.matchData.getTeam(0)
                logo = "../" + self.logoManager.getTeam1().getFile(True)
                display = "block"
            elif(team2):
                team = self.matchData.getTeam(1)
                logo = "../" + self.logoManager.getTeam2().getFile(True)
                display = "block"

            name = self.aliasManager.translatePlayer(
                newData.getPlayer(player_idx))
            self.__playerIntroData[player_idx]['name'] = name
            self.__playerIntroData[player_idx]['team'] = team
            self.__playerIntroData[player_idx]['race'] = newData.getRace(
                player_idx).lower()
            self.__playerIntroData[player_idx]['logo'] = logo
            self.__playerIntroData[player_idx]['display'] = display

            try:
                if tts_active:
                    if team and tts_scope == 'team_player':
                        text = "{}'s {}".format(team, name)
                    else:
                        text = name
                    tts = gtts.gTTS(text=text, lang=tts_lang)
                    tts_file = 'src/sound/player{}.mp3'.format(player_idx + 1)
                    file = os.path.normpath(os.path.join(
                        scctool.settings.getAbsPath(
                            scctool.settings.casting_html_dir),
                        tts_file))
                    tts.save(file)
                else:
                    tts_file = None
                self.__playerIntroData[player_idx]['tts'] = tts_file

            except Exception as e:
                self.__playerIntroData[player_idx]['tts'] = None
                module_logger.exception("message")

    def getMapImg(self, map, fullpath=False):
        """Get map image from map name."""
        mapdir = scctool.settings.getAbsPath(
            scctool.settings.casting_html_dir)
        mapimg = os.path.normpath(os.path.join(
            mapdir, "src/img/maps", map.replace(" ", "_")))
        mapimg = os.path.basename(self.linkFile(mapimg))
        if not mapimg:
            mapimg = "TBD.jpg"
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
            self.logoManager.swapTeamLogos()
            self.matchData.swapTeams()
            self.updateForms()
            self.updateLogos(False)

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
        self.mapstatsManager.selectMap(self.matchData.getMap(player_idx))

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

    def updateMapButtons(self):
        mappool = list(self.mapstatsManager.getMapPool())
        for i in range(self.view.max_no_sets):
            map = self.matchData.getMap(i)
            if map in mappool:
                self.view.label_set[i].setEnabled(True)
            else:
                self.view.label_set[i].setEnabled(False)
        if self.mapstatsManager.getMapPoolType() == 2:
            self.mapstatsManager.sendMapPool()

    def matchMetaDataChanged(self):
        data = self.matchData.getScoreData()
        self.websocketThread.sendData2Path("score", "ALL_DATA", data)
        data = self.matchData.getMapIconsData()
        self.websocketThread.sendData2Path(
            ['mapicons_box', 'mapicons_landscape'],
            'DATA',
            data)

    def handleMatchDataChange(self, label, object):
        if label == 'team':
            self.websocketThread.sendData2Path(
                'score', 'CHANGE_TEXT',
                {'id': 'team{}'.format(object['idx'] + 1),
                 'text': object['value']})
        elif label == 'score':
            score = self.matchData.getScore()
            for idx in range(0, 2):
                self.websocketThread.sendData2Path(
                    'score', 'CHANGE_TEXT', {
                        'id': 'score{}'.format(idx + 1),
                        'text': str(score[idx])})
                color = self.matchData.getScoreIconColor(
                    idx, object['set_idx'])
                self.websocketThread.sendData2Path(
                    'score', 'CHANGE_SCORE', {
                        'teamid': idx + 1,
                        'setid': object['set_idx'] + 1,
                        'color': color})
            colorData = self.matchData.getColorData(object['set_idx'])
            self.websocketThread.sendData2Path(
                ['mapicons_box', 'mapicons_landscape'],
                'CHANGE_SCORE', {
                    'winner': object['value'],
                    'setid': object['set_idx'] + 1,
                    'score_color': colorData['score_color'],
                    'border_color': colorData['border_color'],
                    'hide': colorData['hide'],
                    'opacity': colorData['opacity']})
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
