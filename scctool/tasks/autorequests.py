"""Sent request to Nightbot and Twitch if needed."""
import logging
import PyQt5

from scctool.tasks.tasksthread import TasksThread

import scctool.settings
import scctool.tasks.twitch
import scctool.tasks.nightbot

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
        self.addTask('twitch_once', self.__twitchOnceTask)
        self.addTask('nightbot', self.__nightbotTask)
        self.addTask('nightbot_once', self.__nightbotOnceTask)

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

    def __twitchOnceTask(self):
        try:
            self.__controller.updateData()
            title = scctool.settings.config.parser.get(
                "Twitch", "title_template")
            title = self.__controller.placeholders.replace(title)
            msg, success = scctool.tasks.twitch.updateTitle(title)
            self.twitchSignal.emit(msg)
        finally:
            self.deactivateTask('twitch_once')

    def __nightbotTask(self):
        for command, message in scctool.settings.nightbot_commands.items():
            message = self.__controller.placeholders.replace(message)
            if(scctool.tasks.nightbot.previousMsg.get(command, None) is None):
                scctool.tasks.nightbot.previousMsg[command] = message
            elif(scctool.tasks.nightbot.previousMsg[command] != message):
                msg, success = scctool.tasks.nightbot.updateCommand(
                    command, message)
                self.nightbotSignal.emit(msg)
                if not success:
                    self.disableCB.emit('nightbot')
                    self.deactivateTask('nightbot')
                    break

    def __nightbotOnceTask(self):
        try:
            self.__controller.updateData()
            for command, message in scctool.settings.nightbot_commands.items():
                message = self.__controller.placeholders.replace(message)
                msg, _ = scctool.tasks.nightbot.updateCommand(command, message)
                self.nightbotSignal.emit(msg)
        finally:
            self.deactivateTask('nightbot_once')
