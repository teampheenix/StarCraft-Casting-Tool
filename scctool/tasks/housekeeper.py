"""Write streaming data to txt-files if needed."""
import logging
import queue

import scctool.settings
from scctool.tasks.tasksthread import TasksThread

# from PyQt5.QtCore import pyqtSignal


# create logger
module_logger = logging.getLogger(__name__)


class HouseKeeperThread(TasksThread):
    """Write streaming data to txt-files if needed."""

    def __init__(self, controller):
        """Init the thread."""
        super().__init__()
        self._controller = controller
        self.setTimeout(120)
        self.addTask('save', self.__saveData)
        self.addTask('clean', self.__clean)
        self.activateTask('clean')

    def __saveData(self):
        module_logger.info('Saving all to file!')
        self._controller.historyManager.enforeMaxLength()
        self._controller.saveAll()

    def __clean(self):
        module_logger.info('Performing cleaning tasks...')
        self._controller.logoManager.removeDeadMatches()
        self._controller.logoManager.removeDuplicates()
        self._controller.logoManager.clearFolder()
        self.deactivateTask('clean')
