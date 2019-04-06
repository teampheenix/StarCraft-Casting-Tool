"""Task to write out txt-files with match data."""
import logging
import queue

import scctool.settings
import scctool.settings.translation
from scctool.tasks.tasksthread import TasksThread

# from PyQt5.QtCore import pyqtSignal


# create logger
module_logger = logging.getLogger(__name__)
_ = scctool.settings.translation.gettext


class TextFilesThread(TasksThread):
    """Write streaming data to txt-files if needed."""

    def __init__(self, matchControl):
        """Init the thread."""
        super().__init__()
        self._matchControl = matchControl
        self._q = SetQueue()
        self._available_items = ['team', 'score',
                                 'meta', 'league', 'bestof',
                                 'cd_start', 'cd_end']
        self._matchControl.dataChanged.connect(self.put)
        self._matchControl.metaChanged.connect(self.put)
        self.addTask('write', self.__writeTask)
        self.activateTask('write')
        self.put('meta')

    def put(self, item='meta', *args):
        """Put a item into the queue."""
        if item == 'player' and self._matchControl.activeMatch().getSolo():
            self._q.put('team')
        elif item in self._available_items:
            self._q.put(item)

    def __writeTask(self):
        try:
            item = self._q.get(timeout=0.5)
            if item == "team":
                self.__writeTeam()
            elif item == "score":
                self.__writeScore()
            elif item == "bestof":
                self.__writeBestOf()
            elif item == "cd_start":
                self.__writeCountdown(True)
            elif item == "cd_end":
                self.__writeCountdown(False)
            else:
                self.__writeBestOf()
                self.__writeTeam()
                self.__writeScore()
                self.__writeLeague()
        except queue.Empty:
            pass
        finally:
            pass

    def __writeCountdown(self, start=True):
        file = scctool.settings.getAbsPath(
            scctool.settings.casting_data_dir
            + "/countdown.txt")
        if start:
            txt = scctool.settings.config.parser.get("Countdown", "pre_txt")
        else:
            txt = scctool.settings.config.parser.get("Countdown", "post_txt")
        with open(file, mode='w', encoding='utf-8') as f:
            f.write(txt)

    def __writeTeam(self):
        file = scctool.settings.getAbsPath(
            scctool.settings.casting_data_dir
            + "/teams_vs_long.txt")
        with open(file, mode='w', encoding='utf-8') as f:
            team1 = self._matchControl.activeMatch().getTeamOrPlayer(0)
            team2 = self._matchControl.activeMatch().getTeamOrPlayer(1)
            f.write(f'{team1} vs {team2}\n')

        file = scctool.settings.getAbsPath(
            scctool.settings.casting_data_dir
            + "/teams_vs_short.txt")
        with open(file, mode='w', encoding='utf-8') as f:
            f.write(self._matchControl.activeMatch().getTeamTag(0) + ' vs '
                    + self._matchControl.activeMatch().getTeamTag(1) + "\n")

        for idx in range(2):
            team = self._matchControl.activeMatch().getTeamOrPlayer(idx)
            file = scctool.settings.getAbsPath(
                f'{scctool.settings.casting_data_dir}/team{idx+1}.txt')
            with open(file, mode='w', encoding='utf-8') as f:
                f.write(team)

    def __writeScore(self):
        file = scctool.settings.getAbsPath(
            f"{scctool.settings.casting_data_dir}/score.txt")

        score = self._matchControl.activeMatch().getScore()
        score_str = f"{score[0]} - {score[1]}"

        with open(file, mode='w', encoding='utf-8') as f:
            f.write(score_str)

        for team in range(2):
            file = scctool.settings.getAbsPath(
                f"{scctool.settings.casting_data_dir}/score{team+1}.txt")
            with open(file, mode='w', encoding='utf-8') as f:
                f.write(f'{score[team]}')

    def __writeLeague(self):
        file = scctool.settings.getAbsPath(
            scctool.settings.casting_data_dir + "/league.txt")
        with open(file, mode='w', encoding='utf-8') as f:
            f.write(self._matchControl.activeMatch().getLeague())

    def __writeBestOf(self):
        file = scctool.settings.getAbsPath(
            scctool.settings.casting_data_dir + "/bestof.txt")
        with open(file, mode='w', encoding='utf-8') as f:
            bo = self._matchControl.activeMatch().getBestOf()
            f.write(f'Bo{bo}')


class SetQueue(queue.Queue):
    """Queue to write to txt-files."""

    def _init(self, maxsize):
        """Init queue."""
        self.queue = set()

    def _put(self, item):
        self.queue.add(item)

    def _get(self):
        return self.queue.pop()
