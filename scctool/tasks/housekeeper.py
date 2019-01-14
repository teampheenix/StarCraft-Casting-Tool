"""Housekeeper of StarCraft Casting Tool for cleaning and regular tasks."""
import logging
from datetime import datetime, timedelta, timezone

import requests
from PyQt5.QtCore import pyqtSignal

import scctool.settings.translation
from scctool.tasks.tasksthread import TasksThread

"""Write streaming data to txt-files if needed."""


# create logger
module_logger = logging.getLogger(__name__)
_ = scctool.settings.translation.gettext


class HouseKeeperThread(TasksThread):
    """Write streaming data to txt-files if needed."""

    alphaMatches = pyqtSignal(object)
    ip_updated = pyqtSignal(str)

    def __init__(self, controller):
        """Init the thread."""
        super().__init__()
        self._controller = controller
        self.setTimeout(120)
        self.addTask('save', self.__saveData)
        self.addTask('alphatl', self.__loadAlphaMatches)
        self.addTask('check_ip', self.__check_ip)
        self.addTask('clean', self.__clean)
        self.activateTask('clean')

        self._last_alpha_output = {}
        self._last_ip = ''

    def __saveData(self):
        """Save all data."""
        module_logger.info('Saving all to file!')
        self._controller.historyManager.enforeMaxLength()
        self._controller.saveAll()

    def __loadAlphaMatches(self):
        """Load latest upcoming alpha matches from alpha api."""
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
            if self._last_alpha_output != output:
                self._last_alpha_output = output
                self.alphaMatches.emit(output)
        except Exception:
            module_logger.exception("message")

    def __check_ip(self):
        """Check current external IP."""
        module_logger.info('Checking IP')
        url = 'https://api.ipify.org'
        try:
            ip = requests.get(url=url).text
            if self._last_ip != ip:
                self._last_ip = ip
                self.ip_updated.emit(ip)
        except Exception:
            module_logger.exception("message")

    def __clean(self):
        """Perform all cleaning tasks."""
        module_logger.info('Performing cleaning tasks...')
        self._controller.logoManager.removeDeadMatches()
        self._controller.logoManager.removeDuplicates()
        self._controller.logoManager.clearFolder()
        self._controller.tts.cleanCache()
        self.deactivateTask('clean')
