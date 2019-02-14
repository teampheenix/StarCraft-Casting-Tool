"""Widget to display match data (in a tab)."""
import logging

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor, QIcon
from PyQt5.QtWidgets import (QAction, QComboBox, QCompleter, QGridLayout,
                             QGroupBox, QHBoxLayout, QInputDialog, QLabel,
                             QMessageBox, QPushButton, QRadioButton,
                             QSizePolicy, QSlider, QSpacerItem, QTabBar,
                             QVBoxLayout, QWidget)

import scctool.settings
import scctool.settings.config
import scctool.settings.translation
from scctool.view.widgets import IconPushButton, MapLineEdit, MonitoredLineEdit

module_logger = logging.getLogger(__name__)
_ = scctool.settings.translation.gettext


class MatchDataWidget(QWidget):
    """Widget to display match data."""

    def __init__(self, parent, tabWidget, matchData, closeable=True):
        """Init widget."""
        super().__init__(parent)

        self.max_no_sets = scctool.settings.max_no_sets
        self.max_no_vetoes = int(scctool.settings.max_no_sets / 2) * 2
        self.scoreWidth = 35
        self.raceWidth = 50
        self.labelWidth = 35
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

        self._closeButton = QPushButton()
        pixmap = QIcon(scctool.settings.getResFile('close.png'))
        self._closeButton.setIcon(pixmap)
        self._closeButton.setFlat(True)
        self._closeButton.clicked.connect(self.closeTab)
        self._closeButton.setToolTip(_('Close Match'))
        self._tabWidget.tabBar().setTabButton(
            self._tabIdx, QTabBar.ButtonPosition.RightSide, self._closeButton)
        self.setClosable(closeable)

    def setClosable(self, closeable):
        """Make the tab closable."""
        self._closeButton.setHidden(not closeable)

    def closeTab(self):
        """Close the tab."""
        if self._tabWidget.count() > 1:
            idx = self._tabWidget.indexOf(self)
            ident = self.matchData.getControlID()
            self._tabWidget.removeTab(idx)
            new_index = self.controller.matchControl.removeMatch(ident)
            if new_index is not None:
                self._tabWidget.widget(new_index).checkButton()
        count = self._tabWidget.count()
        if count == 1:
            self._tabWidget.widget(0).setClosable(False)

    def checkButton(self):
        """Check the button."""
        self._radioButton.setChecked(True)

    def activate(self, checked):
        """Activate match tab."""
        if (checked
                and self.controller.matchControl.activeMatchId()
                != self._ctrlID):
            self.controller.matchControl.activateMatch(
                self.matchData.getControlID())
            self.autoSetNextMap(send=False)
            self.controller.mapstatsManager.sendMapPool()
            self.parent.updateAllMapButtons()
            self.controller.updateLogosWebsocket()
        elif self.controller.matchControl.countMatches() == 1:
            self._radioButton.toggled.disconnect()
            self._radioButton.setChecked(True)
            self._radioButton.toggled.connect(self.activate)

    def setName(self):
        """Set the name of the tab."""
        team1 = self.matchData.getTeamOrPlayer(0).replace('&', '&&')
        team2 = self.matchData.getTeamOrPlayer(1).replace('&', '&&')
        name = " {} vs {}".format(team1, team2)
        self._tabWidget.tabBar().setTabText(self._tabIdx, name)

    def _createView(self):
        """Create the view."""
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

        self.pb_swap = QPushButton()
        pixmap = QIcon(
            scctool.settings.getResFile('update.png'))
        self.pb_swap.setIcon(pixmap)
        self.pb_swap.clicked.connect(self.controller.swapTeams)
        self.pb_swap.setFixedWidth(self.labelWidth)
        self.pb_swap.setToolTip(_("Swap teams and logos."))
        container.addWidget(self.pb_swap, 0, 0, 2, 1)

        label = QLabel(_("League:"))
        label.setAlignment(Qt.AlignCenter)
        policy = QSizePolicy()
        policy.setHorizontalStretch(4)
        policy.setHorizontalPolicy(QSizePolicy.Expanding)
        policy.setVerticalStretch(1)
        policy.setVerticalPolicy(QSizePolicy.Fixed)
        label.setSizePolicy(policy)
        container.addWidget(label, 0, 1, 1, 1)

        label = QLabel(_('Maps \\ Teams:'))
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
                self.le_player[team_idx][player_idx].setContextMenuPolicy(
                    Qt.CustomContextMenu)
                self.le_player[team_idx][player_idx].\
                    customContextMenuRequested.connect(
                    lambda x, team_idx=team_idx,
                    player_idx=player_idx:
                    self.openPlayerContextMenu(team_idx, player_idx))

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
                self.showMap(player_idx))
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

        self.createVetoGroupBox()
        layout.addWidget(self.veto_groupbox)

        layout.addItem(QSpacerItem(
            0, 0, QSizePolicy.Minimum,
            QSizePolicy.Expanding))
        self.setLayout(layout)

        self.updateMapCompleters()
        self.updatePlayerCompleters()
        self.updateTeamCompleters()

    def createVetoGroupBox(self):
        """Create a group box to insert vetoes."""
        self.veto_groupbox = QGroupBox(_('Map Vetoes'))
        self.veto_groupbox.setVisible(False)
        box_layout = QGridLayout()
        rows = int(self.max_no_vetoes / 2)
        self.le_veto_maps = [MapLineEdit() for i in range(self.max_no_vetoes)]
        self.veto_label = [QLabel(f'#{i+1}')
                           for i in range(self.max_no_vetoes)]
        self.sl_veto = [QSlider(Qt.Horizontal)
                        for i in range(self.max_no_vetoes)]
        self.row_label = [QLabel('') for y in range(rows)]
        for veto_idx in range(self.max_no_vetoes):
            row = veto_idx / 2
            col = (veto_idx % 2) * 2
            veto_layout = QHBoxLayout()
            self.le_veto_maps[veto_idx].textModified.connect(
                lambda veto_idx=veto_idx: self.map_veto_changed(veto_idx))
            self.sl_veto[veto_idx].valueChanged.connect(
                lambda value, veto_idx=veto_idx:
                    self.veto_team_changed(veto_idx, value))
            self.veto_label[veto_idx].setFixedWidth(self.labelWidth - 5)
            veto_layout.addWidget(self.veto_label[veto_idx])
            self.le_veto_maps[veto_idx].setText("TBD")
            self.le_veto_maps[veto_idx].setAlignment(
                Qt.AlignCenter)
            self.le_veto_maps[veto_idx].setPlaceholderText(
                _("Map Veto {}").format(veto_idx + 1))
            self.le_veto_maps[veto_idx].setMinimumWidth(
                self.mimumLineEditWidth)
            veto_layout.addWidget(self.le_veto_maps[veto_idx])
            self.sl_veto[veto_idx].setMinimum(0)
            self.sl_veto[veto_idx].setMaximum(1)
            self.sl_veto[veto_idx].setValue(veto_idx % 2)
            self.sl_veto[veto_idx].setTickPosition(
                QSlider.TicksBothSides)
            self.sl_veto[veto_idx].setTickInterval(1)
            self.sl_veto[veto_idx].setTracking(False)
            self.sl_veto[veto_idx].setToolTip(
                _('Select which player/team vetoes.'))
            self.sl_veto[veto_idx].setFixedWidth(self.scoreWidth - 5)
            veto_layout.addWidget(self.sl_veto[veto_idx])
            box_layout.addLayout(veto_layout, row, col)
        for idx in range(int(self.max_no_vetoes / 2)):
            self.row_label[idx].setFixedWidth(self.labelWidth / 2 + 5)
            box_layout.addWidget(self.row_label[idx], idx, 1)
        self.veto_groupbox.setLayout(box_layout)

    def toggleVetoes(self, visible=True):
        """Toggle the visibility of the veto group box."""
        self.veto_groupbox.setVisible(visible)

    def openPlayerContextMenu(self, team_idx, player_idx):
        """Open the player context menu."""
        menu = self.le_player[team_idx][player_idx].\
            createStandardContextMenu()
        first_action = menu.actions()[0]
        add_alias_action = QAction('Add Alias')
        add_alias_action.triggered.connect(
            lambda x, team_idx=team_idx,
            player_idx=player_idx: self.addAlias(team_idx, player_idx))
        menu.insertAction(first_action, add_alias_action)
        menu.insertSeparator(first_action)
        menu.exec_(QCursor.pos())

    def addAlias(self, team_idx, player_idx):
        """Add a player alias."""
        name = self.le_player[team_idx][player_idx].text().strip()
        name, ok = QInputDialog.getText(
            self, _('Player Alias'), _('Name') + ':', text=name)
        if not ok:
            return

        name = name.strip()
        alias, ok = QInputDialog.getText(
            self, _('Alias'), _('Alias of {}').format(name) + ':', text="")

        alias = alias.strip()
        if not ok:
            return
        try:
            self.controller.aliasManager.addPlayerAlias(name, alias)
        except Exception as e:
            module_logger.exception("message")
            QMessageBox.critical(self, _("Error"), str(e))

    def league_changed(self):
        """Handle a change of the league."""
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
                    self.autoSetNextMap()
        except Exception:
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
        except Exception:
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

        except Exception:
            module_logger.exception("message")

    def team_changed(self, team_idx):
        """Handle change of the team."""
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
        """Handle a map change."""
        if not self.tlock.trigger():
            return
        self.matchData.setMap(set_idx, self.le_map[set_idx].text())
        self.updateMapButtons()
        self.autoSetNextMap(set_idx)

    def map_veto_changed(self, idx):
        """Handle a map veto change."""
        if not self.tlock.trigger():
            return
        self.matchData.setVeto(idx, self.le_veto_maps[idx].text())
        self.controller.mapstatsManager.sendMapPool()

    def veto_team_changed(self, idx, team):
        """Handle a map veto change."""
        if not self.tlock.trigger():
            return
        self.matchData.setVeto(idx, self.le_veto_maps[idx].text(), team)

    def autoSetNextMap(self, idx=-1, send=True):
        """Set the next map automatically."""
        if self.controller.matchControl.activeMatchId() == self._ctrlID:
            self.controller.autoSetNextMap(idx, send)

    def updateMapCompleters(self):
        """Update the auto completers for maps."""
        for i in range(self.max_no_sets):
            map_list = scctool.settings.maps.copy()
            try:
                map_list.remove("TBD")
            except Exception:
                pass
            finally:
                map_list.sort()
                map_list.append("TBD")
            completer = QCompleter(map_list, self.le_map[i])
            completer.setCaseSensitivity(Qt.CaseInsensitive)
            completer.setFilterMode(Qt.MatchContains)
            completer.setCompletionMode(
                QCompleter.UnfilteredPopupCompletion)
            completer.setWrapAround(True)
            completer.activated.connect(self.le_map[i].completerFinished)
            self.le_map[i].setCompleter(completer)

        for i in range(self.max_no_vetoes):
            map_list = scctool.settings.maps.copy()
            if 'TBD' in map_list:
                map_list.remove('TBD')
            map_list.sort()
            map_list.append('TBD')
            completer = QCompleter(map_list, self.le_veto_maps[i])
            completer.setCaseSensitivity(Qt.CaseInsensitive)
            completer.setFilterMode(Qt.MatchContains)
            completer.setCompletionMode(
                QCompleter.UnfilteredPopupCompletion)
            completer.setWrapAround(True)
            completer.activated.connect(self.le_veto_maps[i].completerFinished)
            self.le_veto_maps[i].setCompleter(completer)

    def updatePlayerCompleters(self):
        """Refresh the completer for the player line edits."""
        player_list = scctool.settings.config.getMyPlayers(
            True) + ["TBD"] + self.controller.historyManager.getPlayerList()
        for player_idx in range(self.max_no_sets):
            for team_idx in range(2):
                completer = QCompleter(
                    player_list, self.le_player[team_idx][player_idx])
                completer.setCaseSensitivity(
                    Qt.CaseInsensitive)
                completer.setCompletionMode(
                    QCompleter.InlineCompletion)
                completer.setFilterMode(Qt.MatchContains)
                completer.setWrapAround(True)
                completer.activated.connect(
                    self.le_player[team_idx][player_idx].completerFinished)
                self.le_player[team_idx][player_idx].setCompleter(
                    completer)

    def updateTeamCompleters(self):
        """Refresh the completer for the team line edits."""
        team_list = scctool.settings.config.getMyTeams() + \
            ["TBD"] + self.controller.historyManager.getTeamList()
        for team_idx in range(2):
            completer = QCompleter(
                team_list, self.le_team[team_idx])
            completer.setCaseSensitivity(Qt.CaseInsensitive)
            completer.setCompletionMode(
                QCompleter.InlineCompletion)
            completer.setFilterMode(Qt.MatchContains)
            completer.setWrapAround(True)
            completer.activated.connect(
                self.le_team[team_idx].completerFinished)
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

            no_vetoes = self.matchData.getNoVetoes()
            for i in range(self.max_no_vetoes):
                visible = no_vetoes > i
                self.le_veto_maps[i].setVisible(visible)
                self.veto_label[i].setVisible(visible)
                self.sl_veto[i].setVisible(visible)
                if i % 2:
                    self.row_label[int(i / 2)].setVisible(visible)
                if visible:
                    veto = self.matchData.getVeto(i)
                    self.le_veto_maps[i].setText(veto.get('map'))
                    self.sl_veto[i].setValue(veto.get('team'))

            self.updatePlayerCompleters()
            self.updateTeamCompleters()
            self.updateMapButtons()
            self.setName()
            # self.autoSetNextMap()

        except Exception:
            module_logger.exception("message")
            raise

    def updateMapButtons(self):
        """Update the map buttons."""
        mappool = list(self.controller.mapstatsManager.getMapPool())
        for i in range(self.max_no_sets):
            self.label_set[i].setEnabled(self.matchData.getMap(i) in mappool)
        if (self.controller.mapstatsManager.getMapPoolType() == 2
                and self.controller.matchControl.activeMatchId()
                == self._ctrlID):
            self.controller.mapstatsManager.sendMapPool()

    def updateLogos(self, force=False):
        """Update team logos in view."""
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
            self.controller.updateLogosWebsocket()

    def allkillUpdate(self):
        """In case of allkill move the winner to the next set."""
        if(self.matchData.allkillUpdate()):
            self.updateForms()

    def setScore(self, idx, score, allkill=True):
        """Handle change of the score."""
        try:
            if(self.sl_score[idx].value() == 0):
                self.parent.statusBar().showMessage(_('Updating Score...'))
                with self.tlock:
                    self.sl_score[idx].setValue(score)
                    self.matchData.setMapScore(idx, score, True)
                    if allkill:
                        self.allkillUpdate()
                    self.autoSetNextMap()
                    if not self.controller.resetWarning():
                        self.parent.statusBar().showMessage('')
                return True
            else:
                return False
        except Exception:
            module_logger.exception("message")

    def showMap(self, player_idx):
        """Show the map in the mapstats browser source."""
        self.controller.mapstatsManager.selectMap(
            self.matchData.getMap(player_idx))


class TriggerLock():
    """Trigger lock."""

    def __init__(self):
        """Init the lock."""
        self.__trigger = True

    def __enter__(self):
        """Enter the lock."""
        self.__trigger = False

    def __exit__(self, error_type, value, traceback):
        """Exit the lock."""
        self.__trigger = True

    def trigger(self):
        """Return if the logged is triggered."""
        return bool(self.__trigger)
