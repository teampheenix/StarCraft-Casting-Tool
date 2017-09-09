"""Sent request to Nightbot and Twitch if needed."""
import logging
import PyQt5

from scctool.tasks.tasksthread import TasksThread

import scctool.settings
import scctool.tasks.twitch

# create logger
module_logger = logging.getLogger('scctool.tasks.autorequests')


class AutoRequestsThread(TasksThread):
    """Sent request to Nightbot and Twitch if needed."""

    twitchSignal = PyQt5.QtCore.pyqtSignal(str)
    nightbotSignal = PyQt5.QtCore.pyqtSignal(str)
    disableCB = PyQt5.QtCore.pyqtSignal(str)

    def __init__(self, controller):
        """Init the thread."""
        super(AutoRequestsThread, self).__init__()

        self.__controller = controller
        self.setTimeout(10)

        self.addTask('twitch', self.__twitchTask)
        self.addTask('nightbot', self.__nightbotTask)

        self.twitchSignal.connect(controller.displayWarning)
        self.nightbotSignal.connect(controller.displayWarning)
        self.disableCB.connect(controller.uncheckCB)

    def __twitchTask(self):
        title = scctool.settings.config.parser.get("Twitch", "title_template")
        title = self.__controller.placeholders.replace(title)

        if(scctool.tasks.twitch.previousTitle is None):
            scctool.tasks.twitch.previousTitle = title
        elif(scctool.tasks.twitch.previousTitle != title):
            msg, success = scctool.tasks.twitch.updateTitle(title)
            self.twitchSignal.emit(msg)
            if not success:
                self.disableCB.emit('twitch')
                self.deactivateTask('twitch')

    def __nightbotTask(self):
        message = scctool.settings.config.parser.get("Nightbot", "message")
        message = self.__controller.placeholders.replace(message)
        if(scctool.tasks.nightbot.previousMsg is None):
            scctool.tasks.nightbot.previousMsg = message
        elif(scctool.tasks.nightbot.previousMsg != message):
            msg, success = scctool.tasks.nightbot.updateCommand(message)
            self.nightbotSignal.emit(msg)
            if not success:
                self.disableCB.emit('nightbot')
                self.deactivateTask('nightbot')
