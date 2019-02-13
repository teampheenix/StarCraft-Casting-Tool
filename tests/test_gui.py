from PyQt5.QtCore import Qt

import pytest
import scctool.settings
import logging
import random
import string


class TestGUI(object):

    def gui_setup(self, qtbot, caplog, scct_app):
        caplog.set_level(logging.ERROR)
        self.caplog = caplog
        self.main_window, self.cntlr = scct_app
        self.qtbot = qtbot
        self.qtbot.addWidget(self.main_window)
        self.qtbot.waitForWindowShown(self.main_window)

    def catch_errors(self):
        for record in self.caplog.records:
            assert record.levelname != 'CRITICAL'
            assert record.levelname != 'ERROR'

    def test_match_formats(self, qtbot, caplog, scct_app):
        self.gui_setup(qtbot, caplog, scct_app)

        self.assert_match_format()

        self.catch_errors()

    def test_subwindows(self, qtbot, caplog, scct_app):
        self.gui_setup(qtbot, caplog, scct_app)

        self.assert_subwindows()

        self.catch_errors()

    @pytest.mark.parametrize("player_before_race",
                             [True, False],
                             ids=["player_race", "race_player"])
    def test_player_autocomplete(self, qtbot, caplog,
                                 scct_app, player_before_race):
        self.gui_setup(qtbot, caplog, scct_app)

        self.qtbot.mouseClick(self.main_window.pb_resetdata, Qt.LeftButton)
        self.assert_bo(3)
        self.main_window.cb_allkill.setChecked(False)
        match = self.cntlr.matchControl.activeMatch()
        assert self.main_window.cb_allkill.isChecked() is False
        assert match.getAllKill() is False
        matchWidget = self.main_window.matchDataTabWidget.widget(
            self.cntlr.matchControl.activeMatchIdx())
        team_idx = random.choice([0, 1])
        set_idx = random.choice([0, 1, 2])
        player = ''.join(random.choices(
            string.ascii_letters + string.digits, k=15))
        race = scctool.settings.idx2race(random.choice([1, 2, 3]))
        if player_before_race:
            self.insert_into_widget(
                matchWidget.le_player[team_idx][set_idx], player)
            matchWidget.cb_race[team_idx][set_idx].setCurrentIndex(
                scctool.settings.race2idx(race))
        else:
            matchWidget.cb_race[team_idx][set_idx].setCurrentIndex(
                scctool.settings.race2idx(race))
            self.insert_into_widget(
                matchWidget.le_player[team_idx][set_idx], player)
        self.assert_player(team_idx, set_idx, player)
        self.assert_race(team_idx, set_idx, race)
        self.qtbot.mouseClick(self.main_window.pb_resetdata, Qt.LeftButton)
        team_idx = random.choice([0, 1])
        set_idx = random.choice([0, 1, 2])
        self.assert_player(team_idx, set_idx, 'TBD')
        self.assert_race(team_idx, set_idx, 'Random')
        self.insert_into_widget(
            matchWidget.le_player[team_idx][set_idx],
            player[:-5], key=Qt.Key_Enter)
        self.assert_player(team_idx, set_idx, player)
        self.assert_race(team_idx, set_idx, race)

        self.catch_errors()

    def test_allkill_update(self, qtbot, caplog, scct_app):
        self.gui_setup(qtbot, caplog, scct_app)

        self.qtbot.mouseClick(self.main_window.pb_resetdata, Qt.LeftButton)
        bo = 15
        self.assert_bo(bo)
        self.main_window.cb_allkill.setChecked(False)
        match = self.cntlr.matchControl.activeMatch()
        assert self.main_window.cb_allkill.isChecked() is False
        assert match.getAllKill() is False
        self.main_window.cb_allkill.setChecked(True)
        assert match.getAllKill()

        matchWidget = self.main_window.matchDataTabWidget.widget(
            self.cntlr.matchControl.activeMatchIdx())
        for set_idx in range(bo - 1):
            players = []
            for team_idx in range(2):
                player = f'Allkill Player {team_idx+1} {set_idx+1}'
                self.insert_into_widget(
                    matchWidget.le_player[team_idx][set_idx], player)
                race = scctool.settings.idx2race(
                    (team_idx + set_idx + 1) % 4)
                matchWidget.cb_race[team_idx][set_idx].setCurrentIndex(
                    scctool.settings.race2idx(race))
                players.append({'player': player, 'race': race})
                self.assert_player(team_idx, set_idx + 1, 'TBD')
                self.assert_race(team_idx, set_idx + 1, 'Random')
            self.assert_score(set_idx, 0)
            score = random.choice([-1, 1])
            matchWidget.sl_score[set_idx].setValue(score)
            self.assert_score(set_idx, score)
            team = int((score + 1) / 2)
            other_team = int((-score + 1) / 2)
            self.assert_player(other_team, set_idx + 1, 'TBD')
            self.assert_race(other_team, set_idx + 1, 'Random')
            self.assert_player(team, set_idx + 1, players[team]['player'])
            self.assert_race(team, set_idx + 1, players[team]['race'])

        self.catch_errors()

    def assert_race(self, team_idx, set_idx, race):
        match = self.cntlr.matchControl.activeMatch()
        matchWidget = self.main_window.matchDataTabWidget.widget(
            self.cntlr.matchControl.activeMatchIdx())
        assert (matchWidget.cb_race[team_idx][set_idx].currentIndex(
        ) == scctool.settings.race2idx(race))
        assert (match.getRace(
                team_idx, set_idx) == race)

    def assert_player(self, team_idx, set_idx, player):
        match = self.cntlr.matchControl.activeMatch()
        matchWidget = self.main_window.matchDataTabWidget.widget(
            self.cntlr.matchControl.activeMatchIdx())
        assert (matchWidget.le_player[team_idx][set_idx].text(
        ) == player)
        assert (match.getPlayer(
                team_idx, set_idx) == player)

    def assert_score(self, set_idx, score):
        match = self.cntlr.matchControl.activeMatch()
        matchWidget = self.main_window.matchDataTabWidget.widget(
            self.cntlr.matchControl.activeMatchIdx())
        assert matchWidget.sl_score[set_idx].value() == score
        assert (match.getMapScore(set_idx) == score)

    def assert_match_format(self):
        self.qtbot.mouseClick(self.main_window.pb_resetdata, Qt.LeftButton)
        self.main_window.tabs.setCurrentIndex(1)
        assert self.main_window.tabs.currentIndex() == 1
        for bo in range(1, scctool.settings.max_no_sets - 3):
            self.assert_bo(bo)
        matchWidget = self.main_window.matchDataTabWidget.widget(
            self.cntlr.matchControl.activeMatchIdx())
        match = self.cntlr.matchControl.activeMatch()
        assert matchWidget.le_league.text() == 'TBD'
        self.insert_into_widget(matchWidget.le_league, 'My Test League')
        assert (match.getLeague() == 'My Test League')

        for team_idx in range(2):
            assert matchWidget.le_team[team_idx].text() == 'TBD'
            assert match.getTeam(
                team_idx) == 'TBD'
            self.insert_into_widget(
                matchWidget.le_team[team_idx], f'My Test Team {team_idx + 1}')
            assert match.getTeam(
                team_idx) == f'My Test Team {team_idx + 1}'
            for player_idx in range(bo):
                self.assert_player(team_idx, player_idx, 'TBD')
                self.assert_race(team_idx, player_idx, 'Random')
                self.insert_into_widget(
                    matchWidget.le_player[team_idx][player_idx],
                    f'Player {team_idx+1} {player_idx+1}')
                self.assert_player(team_idx, player_idx,
                                   f'Player {team_idx+1} {player_idx+1}')
                race = scctool.settings.idx2race((team_idx + player_idx) % 4)
                matchWidget.cb_race[team_idx][player_idx].setCurrentIndex(
                    scctool.settings.race2idx(race))
                self.assert_race(team_idx, player_idx, race)

        for set_idx in range(bo):
            assert matchWidget.le_map[set_idx].text() == 'TBD'
            sc2map = scctool.settings.maps[set_idx %
                                           len(scctool.settings.maps)]
            self.insert_into_widget(
                matchWidget.le_map[set_idx],
                sc2map, True)
            assert (match.getMap(
                set_idx) == sc2map)
            self.assert_score(set_idx, 0)
            score = (set_idx % 2) * 2 - 1
            matchWidget.sl_score[set_idx].setValue(score)
            self.assert_score(set_idx, score)

        self.qtbot.mouseClick(self.main_window.pb_resetscore, Qt.LeftButton)
        for set_idx in range(bo):
            assert matchWidget.sl_score[set_idx].value() == 0
            assert (match.getMapScore(
                set_idx) == 0)

    def assert_bo(self, bo):
        self.main_window.cb_bestof.setCurrentIndex(bo - 1)
        assert self.main_window.cb_bestof.currentText() == str(bo)
        assert self.main_window.cb_minSets.currentText() == str(int(bo / 2) + 1)
        assert self.main_window.cb_minSets.count() == bo
        self.main_window.cb_extend_ace.setChecked(False)
        assert self.main_window.cb_ace_bo.isEnabled() is False
        self.qtbot.mouseClick(self.main_window.pb_applycustom, Qt.LeftButton)
        match = self.cntlr.matchControl.activeMatch()
        assert match.getBestOf() == bo
        assert match.getNoSets() == bo
        assert match.getMinSets() == int(bo / 2) + 1

    def insert_into_widget(self, widget, text,
                           completer=False, key=Qt.Key_Delete):
        widget.setFocus(Qt.TabFocusReason)
        widget.selectAll()
        self.qtbot.keyClicks(widget, text, Qt.NoModifier, 1)
        if completer:
            self.qtbot.keyClick(widget.completer().popup(), Qt.Key_Enter)
        else:
            self.qtbot.keyClick(widget, key)
        if key != Qt.Key_Enter:
            assert widget.text() == text
        widget.clearFocus()
        self.qtbot.wait(5)

    def assert_subwindows(self):
        self.main_window.openBrowserSourcesDialog()
        self.sub_window = self.main_window.mysubwindows['browser']
        self.qtbot.waitForWindowShown(self.sub_window)
        self.sub_window.closeWindow()

        self.main_window.openMiscDialog()
        self.sub_window = self.main_window.mysubwindows['misc']
        self.qtbot.waitForWindowShown(self.sub_window)
        self.sub_window.closeWindow()

        self.main_window.openStyleDialog()
        self.sub_window = self.main_window.mysubwindows['styles']
        self.qtbot.waitForWindowShown(self.sub_window)
        self.sub_window.closeWindow()

        self.main_window.openApiDialog()
        self.sub_window = self.main_window.mysubwindows['connections']
        self.qtbot.waitForWindowShown(self.sub_window)
        self.sub_window.closeWindow()

        self.main_window.openApiDialog()
        self.sub_window = self.main_window.mysubwindows['connections']
        self.qtbot.waitForWindowShown(self.sub_window)
        self.sub_window.closeWindow()

        self.main_window.openReadme()
        self.sub_window = self.main_window.mysubwindows['readme']
        self.qtbot.waitForWindowShown(self.sub_window)
        self.sub_window.close()

        self.main_window.openChangelog()
        self.sub_window = self.main_window.mysubwindows['changelog']
        self.qtbot.waitForWindowShown(self.sub_window)
        self.sub_window.close()
