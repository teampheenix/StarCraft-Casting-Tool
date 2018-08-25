"""Define the match data widget/view."""
import logging

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QComboBox, QCompleter, QGridLayout, QHBoxLayout,
                             QLabel, QPushButton, QRadioButton, QSizePolicy,
                             QSlider, QSpacerItem, QTabBar, QVBoxLayout,
                             QWidget)

import scctool.settings
import scctool.settings.config
from scctool.view.widgets import IconPushButton, MapLineEdit, MonitoredLineEdit

module_logger = logging.getLogger('scctool.view.matchdataview')


class MatchDataWidget(QWidget):
    """Widget to display matchd data."""

    def __init__(self, parent, tabWidget, matchData):
        """Init widget"""
        super().__init__(parent)

        self.max_no_sets = scctool.settings.max_no_sets
        self.scoreWidth = 35
        self.raceWidth = 45
        self.labelWidth = 25
        self.mimumLineEditWidth = 130

        self._tabWidget = tabWidget
        self.matchData = matchData
        self._ctrlID = self.matchData.getControlID()
        self.parent = parent
        self.controller = parent.controller
        self.tlock = TriggerLock()
        self._tabIdx = self._tabWidget.addTab(self, '')
        with self.tlock:
            self._createView()
            self.updateForms()
        self._radioButton = QRadioButton()
        self._radioButton.setStyleSheet("color: green")
        self._radioButton.setToolTip(_('Activate Match'))
        if self.controller.matchControl.selectedMatchId() == self._ctrlID:
            self._tabWidget.setCurrentIndex(self._tabIdx)
        self._tabWidget.tabBar().setTabButton(
            self._tabIdx, QTabBar.ButtonPosition.LeftSide, self._radioButton)
        self._radioButton.toggled.connect(self.activate)
        if self.controller.matchControl.activeMatchId() == self._ctrlID:
            self.checkButton()

    def checkButton(self):
        self._radioButton.setChecked(True)

    def activate(self, checked):
        if checked:
            self.controller.matchControl.activateMatch(
                self.matchData.getControlID())
        elif self.controller.matchControl.countMatches() == 1:
            self._radioButton.toggled.disconnect()
            self._radioButton.setChecked(True)
            self._radioButton.toggled.connect(self.activate)

    def setName(self):
        team1 = self.matchData.getTeamOrPlayer(0)
        team2 = self.matchData.getTeamOrPlayer(1)
        name = "{} vs {}".format(team1, team2)
        self._tabWidget.tabBar().setTabText(self._tabIdx, name)

    def _createView(self):

        layout = QVBoxLayout()

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
        self.label_set = [QPushButton('#{}'.format(y + 1), self)
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
        self.qb_logo1.clicked.connect(lambda: self.parent.logoDialog(1, self))
        logo = self.controller.logoManager.getTeam1(self._ctrlID)
        self.qb_logo1.setIcon(QIcon(logo.provideQPixmap()))

        self.qb_logo2 = IconPushButton()
        self.qb_logo2.setFixedWidth(self.raceWidth)
        self.qb_logo2.clicked.connect(lambda: self.parent.logoDialog(2, self))
        logo = self.controller.logoManager.getTeam2(self._ctrlID)
        self.qb_logo2.setIcon(QIcon(logo.provideQPixmap()))

        self.sl_team = QSlider(Qt.Horizontal)
        self.sl_team.setTracking(False)
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

        button = QPushButton()
        pixmap = QIcon(
            scctool.settings.getResFile('update.png'))
        button.setIcon(pixmap)
        button.clicked.connect(
            lambda: self.controller.swapTeams())
        button.setFixedWidth(self.labelWidth)
        button.setToolTip(_("Swap teams and logos."))
        container.addWidget(button, 0, 0, 2, 1)

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

        layout.addLayout(container)

        for player_idx in range(self.max_no_sets):
            self.le_map[player_idx].textModified.connect(
                lambda player_idx=player_idx: self.map_changed(player_idx))
            for team_idx in range(2):
                self.cb_race[team_idx][player_idx].\
                    currentIndexChanged.connect(
                    lambda idx,
                    t=team_idx,
                    p=player_idx: self.race_changed(t, p))
                self.le_player[team_idx][player_idx].textModified.connect(
                    lambda t=team_idx,
                    p=player_idx: self.player_changed(t, p))
                self.le_player[team_idx][player_idx].setText("TBD")
                self.le_player[team_idx][player_idx].setAlignment(
                    Qt.AlignCenter)
                self.le_player[team_idx][player_idx].setPlaceholderText(
                    _("Player {} of team {}").format(player_idx + 1,
                                                     team_idx + 1))
                self.le_player[team_idx][player_idx].setMinimumWidth(
                    self.mimumLineEditWidth)

                for i in range(4):
                    self.cb_race[team_idx][player_idx].addItem(
                        QIcon(scctool.settings.getResFile(
                            str(i) + ".png")), "")

                self.cb_race[team_idx][player_idx].setFixedWidth(
                    self.raceWidth)

            self.sl_score[player_idx].setMinimum(-1)
            self.sl_score[player_idx].setMaximum(1)
            self.sl_score[player_idx].setValue(0)
            self.sl_score[player_idx].setTickPosition(
                QSlider.TicksBothSides)
            self.sl_score[player_idx].setTickInterval(1)
            self.sl_score[player_idx].setTracking(False)
            self.sl_score[player_idx].valueChanged.connect(
                lambda x,
                player_idx=player_idx: self.sl_changed(player_idx, x))
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
            # self.label_set[player_idx].setText("#" + str(player_idx + 1))
            # self.label_set[player_idx].setAlignment(
            #    Qt.AlignCenter)
            self.label_set[player_idx].setToolTip(
                _("Select map on Mapstats Browser Source."))
            self.label_set[player_idx].setEnabled(False)
            self.label_set[player_idx].clicked.connect(
                lambda x,
                player_idx=player_idx:
                self.controller.showMap(player_idx))
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
            layout.addLayout(self.setContainer[player_idx])

        layout.addItem(QSpacerItem(
            0, 0, QSizePolicy.Minimum,
            QSizePolicy.Expanding))
        self.setLayout(layout)

        self.updateMapCompleters()
        self.updatePlayerCompleters()
        self.updateTeamCompleters()

    def league_changed(self):
        if not self.tlock.trigger():
            return
        self.matchData.setLeague(self.le_league.text())

    def sl_changed(self, set_idx, value):
        """Handle a new score value."""
        try:
            if self.tlock.trigger():
                if set_idx == -1:
                    self.matchData.setMyTeam(value)
                else:
                    self.matchData.setMapScore(set_idx, value, True)
                    self.allkillUpdate()
                    self.controller.autoSetNextMap()
        except Exception as e:
            module_logger.exception("message")

    def player_changed(self, team_idx, player_idx):
        """Handle a change of player names."""
        if not self.tlock.trigger():
            return
        try:
            player = self.le_player[team_idx][player_idx].text().strip()
            race = self.cb_race[team_idx][player_idx].currentIndex()
            if(player_idx == 0 and self.matchData.getSolo()):
                for p_idx in range(1, self.max_no_sets):
                    self.le_player[team_idx][p_idx].setText(player)
                    self.player_changed(team_idx, p_idx)
            self.controller.historyManager.insertPlayer(player, race)
            self.matchData.setPlayer(
                team_idx, player_idx,
                self.le_player[team_idx][player_idx].text())

            if race == 0:
                new_race = scctool.settings.race2idx(
                    self.controller.historyManager.getRace(player))
                if new_race != 0:
                    self.cb_race[team_idx][player_idx].setCurrentIndex(
                        new_race)
            elif player.lower() == "tbd":
                self.cb_race[team_idx][player_idx].setCurrentIndex(0)
            self.updatePlayerCompleters()
            self.setName()
        except Exception as e:
            module_logger.exception("message")

    def race_changed(self, team_idx, player_idx):
        """Handle a change of player names."""
        if not self.tlock.trigger():
            return
        player = self.le_player[team_idx][player_idx].text().strip()
        race = self.cb_race[team_idx][player_idx].currentIndex()
        self.controller.historyManager.insertPlayer(player, race)
        self.matchData.setRace(
            team_idx, player_idx,
            scctool.settings.idx2race(
                self.cb_race[team_idx][player_idx].currentIndex()))
        try:
            if(player_idx == 0 and self.matchData.getSolo()):
                idx = self.cb_race[team_idx][0].currentIndex()
                for player_idx in range(1, self.max_no_sets):
                    self.cb_race[team_idx][player_idx].setCurrentIndex(idx)

        except Exception as e:
            module_logger.exception("message")

    def team_changed(self, team_idx):
        if not self.tlock.trigger():
            return
        team = self.le_team[team_idx].text().strip()
        logo = self.controller.logoManager.getTeam(team_idx + 1).getIdent()
        if logo == '0':
            logo = self.controller.historyManager.getLogo(team)
            if logo != '0':
                self.controller.logoManager.setTeamLogo(team_idx + 1, logo)
                self.controller.updateLogos(True)
        self.controller.historyManager.insertTeam(team, logo)
        self.updateTeamCompleters()
        self.matchData.setTeam(team_idx, team)
        self.matchData.autoSetMyTeam()
        self.sl_team.setValue(self.matchData.getMyTeam())
        self.setName()

    def map_changed(self, set_idx):
        if not self.tlock.trigger():
            return
        self.matchData.setMap(set_idx, self.le_map[set_idx].text())
        self.updateMapButtons()
        self.controller.autoSetNextMap(set_idx)

    def updateMapCompleters(self):
        """Update the auto completers for maps."""
        for i in range(self.max_no_sets):
            list = scctool.settings.maps.copy()
            try:
                list.remove("TBD")
            except Exception as e:
                pass
            finally:
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

    def updateForms(self):
        """Update data in forms."""
        try:
            self.le_league.setText(
                self.matchData.getLeague())
            self.sl_team.setValue(
                self.matchData.getMyTeam())
            for i in range(2):
                team = self.matchData.getTeam(i)
                self.le_team[i].setText(team)
                logo = self.controller.logoManager.getTeam(i + 1).getIdent()
                self.controller.historyManager.insertTeam(team, logo)

            for j in range(2):
                for i in range(1, self.matchData.getNoSets()):
                    self.le_player[j][i].setReadOnly(
                        self.matchData.getSolo())

            for i in range(min(self.max_no_sets,
                               self.matchData.getNoSets())):
                for j in range(2):
                    player = self.matchData.getPlayer(j, i)
                    race = self.matchData.getRace(j, i)
                    self.le_player[j][i].setText(player)
                    self.cb_race[j][i].setCurrentIndex(
                        scctool.settings.race2idx(race))
                    self.controller.historyManager.insertPlayer(player, race)

                self.le_map[i].setText(
                    self.matchData.getMap(i))

                self.sl_score[i].setValue(
                    self.matchData.getMapScore(i))

            for i in range(self.matchData.getNoSets(),
                           self.max_no_sets):
                for j in range(2):
                    self.le_player[j][i].hide()
                    self.cb_race[j][i].hide()
                self.le_map[i].hide()
                self.sl_score[i].hide()
                self.label_set[i].hide()

            for i in range(min(self.max_no_sets,
                               self.matchData.getNoSets())):
                for j in range(2):
                    self.le_player[j][i].show()
                    self.cb_race[j][i].show()
                self.le_map[i].show()
                self.sl_score[i].show()
                self.label_set[i].show()

            self.updatePlayerCompleters()
            self.updateTeamCompleters()
            self.updateMapButtons()
            self.setName()
            # self.autoSetNextMap()

        except Exception as e:
            module_logger.exception("message")
            raise

    def updateMapButtons(self):
        mappool = list(self.controller.mapstatsManager.getMapPool())
        for i in range(self.max_no_sets):
            map = self.matchData.getMap(i)
            if map in mappool:
                self.label_set[i].setEnabled(True)
            else:
                self.label_set[i].setEnabled(False)
        if self.controller.mapstatsManager.getMapPoolType() == 2:
            self.controller.mapstatsManager.sendMapPool()

    def updateLogos(self, force=False):
        """Updata team logos in  view."""
        logo = self.controller.logoManager.getTeam1(self._ctrlID)
        self.qb_logo1.setIcon(QIcon(logo.provideQPixmap()))

        logo = self.controller.logoManager.getTeam2(self._ctrlID)
        self.qb_logo2.setIcon(QIcon(logo.provideQPixmap()))

        for idx in range(2):
            team = self.matchData.getTeam(idx)
            logo = self.controller.logoManager.getTeam(
                idx + 1, self._ctrlID).getIdent()
            self.controller.historyManager.insertTeam(team, logo)

        if self.controller.matchControl.activeMatchId() == self._ctrlID:
            self.controller.updateLogosHTML(force)

    def allkillUpdate(self):
        """In case of allkill move the winner to the next set."""
        if(self.matchData.allkillUpdate()):
            self.updateForms()


class TriggerLock():
    def __init__(self):
        self.__trigger = True

    def __enter__(self):
        self.__trigger = False

    def __exit__(self, type, value, traceback):
        self.__trigger = True

    def trigger(self):
        return bool(self.__trigger)
