import random
import string

import pytest
from PyQt5.QtCore import Qt

import scctool.settings


class TestGUI(object):

    def gui_setup(self, qtbot, scct_app):
        self.main_window, self.cntlr = scct_app
        self.qtbot = qtbot
        self.qtbot.addWidget(self.main_window)
        self.qtbot.waitForWindowShown(self.main_window)

    def test_match_formats(self, qtbot, scct_app):
        self.gui_setup(qtbot, scct_app)

        self.assert_match_format()

    def test_subwindows(self, qtbot, scct_app):
        self.gui_setup(qtbot, scct_app)

        self.assert_subwindows()

    @pytest.mark.parametrize("copy",
                             [True, False],
                             ids=["copy", "add"])
    def test_match_tabs(self, qtbot, scct_app, copy):
        self.gui_setup(qtbot, scct_app)
        old_selected = self.cntlr.matchControl.selectedMatchId()
        old_active = self.cntlr.matchControl.activeMatchId()
        assert old_selected == old_active
        if copy:
            button = self.main_window.pb_copy_match_tab
        else:
            button = self.main_window.pb_add_match_tab
        self.qtbot.mouseClick(button, Qt.LeftButton)
        new_selected = self.cntlr.matchControl.selectedMatchId()
        new_active = self.cntlr.matchControl.activeMatchId()
        assert old_selected != new_selected
        assert old_active == new_active
        new_widget = self.main_window.matchDataTabWidget.widget(
            self.cntlr.matchControl.selectedMatchIdx())
        self.qtbot.mouseClick(new_widget._radioButton, Qt.LeftButton)
        new_active = self.cntlr.matchControl.activeMatchId()
        assert new_selected == new_active
        assert old_active != new_active
        self.qtbot.mouseClick(new_widget._closeButton, Qt.LeftButton)
        new_selected = self.cntlr.matchControl.selectedMatchId()
        new_active = self.cntlr.matchControl.activeMatchId()
        assert old_selected == new_selected
        assert old_active == new_active

    @pytest.mark.parametrize("player_before_race",
                             [True, False],
                             ids=["player_race", "race_player"])
    def test_player_autocomplete(self, qtbot,
                                 scct_app, player_before_race):
        self.gui_setup(qtbot, scct_app)

        self.new_tab()
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

    def test_solo_mode(self, qtbot, scct_app):
        self.gui_setup(qtbot, scct_app)

        self.new_tab()
        bo = 15
        self.assert_bo(bo)

        self.main_window.cb_solo.setChecked(False)
        match = self.cntlr.matchControl.activeMatch()
        assert self.main_window.cb_solo.isChecked() is False
        assert match.getSolo() is False
        self.main_window.cb_solo.setChecked(True)
        assert match.getSolo() is False
        self.qtbot.mouseClick(self.main_window.pb_applycustom, Qt.LeftButton)
        assert match.getSolo()

        matchWidget = self.main_window.matchDataTabWidget.widget(
            self.cntlr.matchControl.activeMatchIdx())
        for team_idx in range(2):
            assert matchWidget.le_team[team_idx].text() == 'TBD'
            assert match.getTeam(
                team_idx) == 'TBD'
            self.insert_into_widget(
                matchWidget.le_team[team_idx], f'My Test Team {team_idx + 1}')
            assert match.getTeam(
                team_idx) == f'My Test Team {team_idx + 1}'
            assert match.getTeamOrPlayer(team_idx) == 'TBD'
        for team_idx in range(2):
            self.assert_player(team_idx, 0, 'TBD')
            self.assert_race(team_idx, 0, 'Random')
            player_name = f'Player for Team {team_idx + 1}'
            race = scctool.settings.idx2race(random.choice([1, 2, 3]))
            matchWidget.cb_race[team_idx][0].setCurrentIndex(
                scctool.settings.race2idx(race))
            self.insert_into_widget(
                matchWidget.le_player[team_idx][0], player_name)
            assert match.getTeamOrPlayer(
                team_idx) == player_name

            for set_idx in range(bo):
                self.assert_player(team_idx, set_idx, player_name)
                self.assert_race(team_idx, set_idx, race)
                if set_idx > 0:
                    assert matchWidget.le_player[team_idx][
                        set_idx].isReadOnly()
                    new_race = scctool.settings.idx2race(
                        random.choice([1, 2, 3]))
                    matchWidget.cb_race[team_idx][set_idx].setCurrentIndex(
                        scctool.settings.race2idx(new_race))
                    self.assert_race(team_idx, set_idx, new_race)

    @pytest.mark.parametrize("match_url", ['https://alpha.tl/match/4709'])
    def test_alpha_match_grabber(self, qtbot, scct_app, match_url):
        self.gui_setup(qtbot, scct_app)

        self.new_tab()
        self.assert_bo(3)
        self.main_window.tabs.setCurrentIndex(0)
        assert self.main_window.tabs.currentIndex() == 0
        self.insert_into_widget(self.main_window.le_url, match_url)
        assert self.main_window.le_url.text() == match_url
        with self.qtbot.waitSignal(self.cntlr.matchControl.metaChanged):
            self.qtbot.mouseClick(self.main_window.pb_refresh, Qt.LeftButton)

        assert self.main_window.cb_bestof.currentText() == str(5)
        assert self.main_window.cb_minSets.currentText() == '3'
        assert self.main_window.cb_ace_bo.isEnabled()
        match = self.cntlr.matchControl.activeMatch()
        assert match.getBestOf() == 5
        assert match.getNoSets() == 5
        assert match.getMinSets() == 3
        assert match.getNoAceSets() == 1

    def new_tab(self):
        self.qtbot.mouseClick(self.main_window.pb_add_match_tab, Qt.LeftButton)
        selected = self.cntlr.matchControl.selectedMatchId()
        while(self.main_window.matchDataTabWidget.count() > 1):
            self.qtbot.mouseClick(self.main_window.matchDataTabWidget.widget(
                0)._closeButton, Qt.LeftButton)
        assert self.main_window.matchDataTabWidget.count() == 1
        assert (self.cntlr.matchControl.selectedMatchId()
                == self.cntlr.matchControl.activeMatchId())
        assert self.cntlr.matchControl.selectedMatchIdx() == 0
        assert self.cntlr.matchControl.activeMatchIdx() == 0
        assert self.cntlr.matchControl.activeMatchId() == selected

    def test_allkill_update(self, qtbot, scct_app):
        self.gui_setup(qtbot, scct_app)

        self.new_tab()
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
        self.new_tab()
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

        with self.qtbot.waitSignal(self.cntlr.matchControl.metaChanged):
            self.qtbot.mouseClick(matchWidget.pb_swap, Qt.LeftButton)

        for team_idx in range(2):
            other_team = 1 - team_idx
            assert match.getTeam(
                team_idx) == f'My Test Team {other_team + 1}'
            for player_idx in range(bo):
                self.assert_player(team_idx, player_idx,
                                   f'Player {other_team+1} {player_idx+1}')
                race = scctool.settings.idx2race((other_team + player_idx) % 4)
                self.assert_race(team_idx, player_idx, race)

        for set_idx in range(bo):
            score = -((set_idx % 2) * 2 - 1)
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
        assert (self.main_window.cb_minSets.currentText()
                == str(int(bo / 2) + 1))
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

    def test_logo_manager(self, qtbot, caplog, scct_app):
        self.gui_setup(qtbot, caplog, scct_app)
        self.new_tab()
        matchWidget = self.main_window.matchDataTabWidget.widget(
            self.cntlr.matchControl.activeMatchIdx())
        teams = ['team pheeniX', 'Wolfs Lair', 'PaniC Fighters', 'Dark Oath']
        for logo_button in [matchWidget.qb_logo1, matchWidget.qb_logo2]:
            self.qtbot.mouseClick(logo_button, Qt.LeftButton)
            logo_dialog = self.main_window.mysubwindows['icons']
            self.qtbot.waitForWindowShown(logo_dialog)
            for liquipedia_button in [logo_dialog.pb_liquipedia_1,
                                      logo_dialog.pb_liquipedia_2]:
                team = random.choice(teams)
                self.qtbot.mouseClick(
                    liquipedia_button, Qt.LeftButton)
                self.qtbot.waitForWindowShown(logo_dialog.mysubwindow)
                self.insert_into_widget(
                    logo_dialog.mysubwindow.qle_search, team, True)
                assert (logo_dialog.mysubwindow.qle_search.text()
                        == team)
                self.qtbot.mouseClick(
                    logo_dialog.mysubwindow.searchButton, Qt.LeftButton)

                def check_for_result():
                    assert len(logo_dialog.mysubwindow.data) > 0
                    assert len(logo_dialog.mysubwindow.nams) > 0
                    logo_dialog.mysubwindow.nams
                    with qtbot.waitSignal(
                            logo_dialog.mysubwindow.nams[0].finished,
                            timeout=10000):
                        pass
                qtbot.waitUntil(check_for_result)
                self.qtbot.mouseClick(
                    logo_dialog.mysubwindow.selectButton, Qt.LeftButton)
            logo_dialog.closeWindow()

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
