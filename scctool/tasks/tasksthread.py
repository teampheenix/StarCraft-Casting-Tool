import logging
import time

from PyQt5.QtCore import QThread

import scctool.settings.translation

"""Define generic thread for various tasks."""


# create logger
module_logger = logging.getLogger(__name__)
_ = scctool.settings.translation.gettext


class TasksThread(QThread):
    """Define generic thread for various tasks."""

    def __init__(self):
        """Init thread."""
        QThread.__init__(self)

        self.__tasks = {}
        self.__run = {}
        self.__methods = {}
        self.__timeout = 1
        self.__idx = 0
        self.__wait_first = False

    def setWaitFirst(self, wait_first):
        self.__wait_first = bool(wait_first)

    def setTimeout(self, timeout):
        """Set the timeout between tasks."""
        self.__timeout = float(timeout)

    def addTask(self, task, method):
        """Add a task."""
        if(len(self.__tasks) > 5):
            raise UserWarning("Only {} tasks allowed per thread.".format(6))
        self.__tasks[task] = False
        self.__methods[task] = method

    def hasActiveTask(self):
        """Check if any task is active."""
        return any(self.__tasks.values())

    def isActive(self, task):
        """Check if a sepcific task is active."""
        try:
            return self.__tasks[task]
        except Exception:
            return False

    def activateTask(self, task):
        """Activate a task."""
        if not (task in self.__tasks):
            raise UserWarning(
                "Task {} of {} is not valid.".format(
                    task,
                    self.__class__.__name__))

        self.__tasks[task] = True

        if not self.isRunning():
            self.start()

    def terminate(self):
        """Deactivate all tasks and terminate thread."""
        for task in self.__tasks:
            self.__tasks[task] = False

    def deactivateTask(self, task):
        """Deactivate a Task."""
        if not (task in self.__tasks):
            raise UserWarning(
                "Task {} of {} is not valid.".format(
                    task,
                    self.__class__.__name__))
        self.__tasks[task] = False

    def execTask(self, task):
        """Execute task."""
        self.__methods[task]()

    def execActiveTasks(self):
        """Exectute all active tasks."""
        executedTasks = []
        continue_loop = True

        while continue_loop and self.hasActiveTask():
            continue_loop = False
            for task, active in self.__tasks.items():
                if active and task not in executedTasks:
                    self.execTask(task)
                    executedTasks.append(task)
                    continue_loop = True

    def __wait(self):
        if(not self.hasActiveTask()):
            return

        cycletime = 0.1
        cycles = int(self.__timeout / cycletime)
        rest = max(self.__timeout - cycles * cycletime, 0.0)

        for i in range(cycles):
            time.sleep(cycletime)
            if(not self.hasActiveTask()):
                return
        time.sleep(rest)

    def run(self):
        """Run the thread."""
        module_logger.info(
            "A {} is starting.".format(self.__class__.__name__))

        if self.__wait_first:
            self.__wait()

        while self.hasActiveTask():
            self.execActiveTasks()
            self.__wait()

        module_logger.info("A {} is done.".format(self.__class__.__name__))
