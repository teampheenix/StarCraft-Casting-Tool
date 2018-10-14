"""Write streaming data to txt-files if needed."""
import logging
from datetime import datetime, timedelta, timezone

import requests
from PyQt5.QtCore import pyqtSignal

from scctool.tasks.tasksthread import TasksThread

# create logger
module_logger = logging.getLogger(__name__)


class HouseKeeperThread(TasksThread):
    """Write streaming data to txt-files if needed."""
    alphaMatches = pyqtSignal(object)

    def __init__(self, controller):
        """Init the thread."""
        super().__init__()
        self._controller = controller
        self.setTimeout(120)
        self.addTask('save', self.__saveData)
        self.addTask('alphatl', self.__loadAlphaMatches)
        self.addTask('clean', self.__clean)
        self.activateTask('clean')

    def __saveData(self):
        module_logger.info('Saving all to file!')
        self._controller.historyManager.enforeMaxLength()
        self._controller.saveAll()

    def __loadAlphaMatches(self):
        module_logger.info('Loading upcoming AlphaTL matches!')
        url = 'https://alpha.tl/api?upcomingmatches'
        try:
            data = requests.get(url=url).json()
            output = dict()
            for match in data:
                dt_obj = datetime.strptime(
                    match['datetime'], '%Y-%m-%d %H:%M:%S')
                dt_obj = dt_obj.replace(tzinfo=timezone(timedelta(hours=0)))
                dt_obj = dt_obj.astimezone()
                label = "{}: {} vs {} - {}".format(
                    match['tournament'].replace('Alpha ', ''),
                    match['team1']['name'],
                    match['team2']['name'],
                    dt_obj.strftime('%e %b, %H:%M'))
                url = 'https://alpha.tl/match/{}'.format(match['id'])
                output[label] = url
            self.alphaMatches.emit(output)
        except Exception:
            module_logger.exception("message")

    def __clean(self):
        module_logger.info('Performing cleaning tasks...')
        self._controller.logoManager.removeDeadMatches()
        self._controller.logoManager.removeDuplicates()
        self._controller.logoManager.clearFolder()
        self._controller.tts.cleanCache()
        self.deactivateTask('clean')
