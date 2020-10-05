"""Housekeeper of StarCraft Casting Tool for cleaning and regular tasks."""
import logging
from datetime import datetime, timedelta, timezone

import requests
from PyQt5.QtCore import pyqtSignal

import scctool.settings.translation
from scctool.tasks.tasksthread import TasksThread

# create logger
module_logger = logging.getLogger(__name__)
_ = scctool.settings.translation.gettext


class HouseKeeperThread(TasksThread):
    """Do cleaning and other regular tasks."""

    spireMatches = pyqtSignal(object)
    ip_updated = pyqtSignal(str)

    def __init__(self, controller):
        """Init the thread."""
        super().__init__()
        self._controller = controller
        self.setTimeout(120)
        self.addTask('save', self.__saveData)
        self.addTask('spiregg', self.__loadSpireMatches)
        self.addTask('check_ip', self.__check_ip)
        self.addTask('clean', self.__clean)
        self.activateTask('clean')

        self._last_spire_output = {}
        self._last_ip = ''

    def __saveData(self):
        """Save all data."""
        module_logger.info('Saving all to file!')
        self._controller.historyManager.enforeMaxLength()
        self._controller.saveAll()

    def __loadSpireMatches(self):
        """Load latest upcoming spire.gg matches from their API."""
        module_logger.info('Loading upcoming Spire.gg matches!')
        try:
            output = dict()
            for match in self.__yieldSpireMatches():
                dt_obj = datetime.fromisoformat(match['datetime'])
                label = "{}: {} vs {} - {}".format(
                    'Spire.gg',
                    match['lineups']['A']['name'],
                    match['lineups']['B']['name'],
                    dt_obj.strftime('%e %b, %H:%M'))
                url = 'https://spire.gg/match/{}'.format(match['id'])
                output[label] = url
            if self._last_spire_output != output:
                self._last_spire_output = output
                self.spireMatches.emit(output)
        except Exception:
            module_logger.exception("message")

    def __yieldSpireMatches(self):
        url = 'https://api.spire.gg/matches'
        for pageNum in range(0, 5):
            params = {
                'past': 'false',
                'solo': 'false',
                'gameId': 'SC2',
                'pageNum': pageNum,
            }
            data = requests.get(url=url, params=params).json()
            if data.get('code', '') != 'ok':
                return
            results = data.get('result', {})
            if results.get('empty', True):
                return
            for match in results.get('content', []):
                yield match

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
