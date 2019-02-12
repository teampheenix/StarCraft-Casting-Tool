from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

from scctool.controller import MainController
from scctool.view.main import MainWindow
import scctool.settings
import sys
import logging


class TestGUI(object):

    def gui_setup(self):
        scctool.settings.loadSettings()
        self.cntlr = MainController()
        self.main_window = MainWindow(
            self.cntlr, QApplication(sys.argv), False)
        self.main_window.show()
        self.qtbot.addWidget(self.main_window)
        self.qtbot.waitForWindowShown(self.main_window)

    def test_gui(self, qtbot, caplog):
        caplog.set_level(logging.ERROR)
        self.qtbot = qtbot
        self.gui_setup()
        self.qtbot.wait(1000)
        self.assert_match_format()
        self.assert_subwindows()

        for record in caplog.records:
            assert record.levelname != 'CRITICAL'
            assert record.levelname != 'ERROR'

    def assert_match_format(self):
        self.qtbot.mouseClick(self.main_window.pb_resetdata, Qt.LeftButton)
        self.main_window.tabs.setCurrentIndex(1)
        assert self.main_window.tabs.currentIndex() == 1
        matchWidget = self.main_window.matchDataTabWidget.widget(
            self.cntlr.matchControl.activeMatchIdx())
        assert matchWidget.le_league.text() == 'TBD'
        self.insert_into_widget(matchWidget.le_league, 'My Test League')
        assert self.cntlr.matchControl.activeMatch().getLeague() == 'My Test League'

        for bo in range(1, scctool.settings.max_no_sets - 3):
            self.assert_bo(bo)

        for team_idx in range(2):
            assert matchWidget.le_team[team_idx].text() == 'TBD'
            self.insert_into_widget(
                matchWidget.le_team[team_idx], f'My Test Team {team_idx + 1}')
            assert self.cntlr.matchControl.activeMatch().getTeam(
                team_idx) == f'My Test Team {team_idx + 1}'
            for player_idx in range(bo):
                assert matchWidget.le_player[team_idx][player_idx].text(
                ) == 'TBD'
                self.insert_into_widget(
                    matchWidget.le_player[team_idx][player_idx],
                    f'Player {team_idx} {player_idx}')
                assert self.cntlr.matchControl.activeMatch().getPlayer(
                    team_idx, player_idx) == f'Player {team_idx} {player_idx}'

    def assert_bo(self, bo):
        self.main_window.cb_bestof.setCurrentIndex(bo - 1)
        assert self.main_window.cb_bestof.currentText() == str(bo)
        assert self.main_window.cb_minSets.currentText() == str(int(bo / 2) + 1)
        assert self.main_window.cb_minSets.count() == bo
        self.main_window.cb_extend_ace.setChecked(False)
        assert self.main_window.cb_ace_bo.isEnabled() == False
        self.qtbot.mouseClick(self.main_window.pb_applycustom, Qt.LeftButton)
        match = self.cntlr.matchControl.activeMatch()
        assert match.getBestOf() == bo
        assert match.getNoSets() == bo
        assert match.getMinSets() == int(bo / 2) + 1

    def insert_into_widget(self, widget, text):
        widget.setFocus(Qt.TabFocusReason)
        widget.selectAll()
        self.qtbot.keyClicks(widget, text, Qt.NoModifier, 10)
        assert widget.text() == text
        widget.clearFocus()
        self.qtbot.wait(100)

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
