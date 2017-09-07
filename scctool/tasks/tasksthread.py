"""Define generic thread for various tasks."""
import logging
import time

from PyQt5.QtCore import QThread, pyqtSignal

# create logger
module_logger = logging.getLogger('scctool.tasks.tasksthread')


class TasksThread(QThread):
    """Define generic thread for various tasks."""

    signal0 = pyqtSignal(str)
    signal1 = pyqtSignal(str)
    signal2 = pyqtSignal(str)
    signal3 = pyqtSignal(str)
    signal4 = pyqtSignal(str)
    signal5 = pyqtSignal(str)

    def __init__(self):
        """Init thread."""
        QThread.__init__(self)

        self.__tasks = {}
        self.__run = {}
        self.__methods = {}
        self.signals = {}
        self.__timeout = 1
        self.__idx = 0

    def setTimeout(self, timeout):
        """Set the timeout between tasks."""
        self.__timeout = float(timeout)

    def addTask(self, task, method):
        """Add a task."""
        if(len(self.__tasks) > 5):
            raise UserWarning("Only {} tasks allowed per thread.".format(6))
        self.__tasks[task] = False
        self.__methods[task] = method
        idx = list(self.__tasks.keys()).index(task)
        self.signals[task] = getattr(self, 'signal' + str(idx))
        try:
            self.signals[task].disconnect()
        except:
            pass

    def connectSignal(self, task, connection):
        """Connect a signal of a task."""
        if not (task in self.__tasks):
            raise UserWarning("Task {} is not valid.".format(task))
        self.signals[task].connect(connection)

    def disconnectSignal(self, task):
        """Disconnect a signal of a task."""
        if not (task in self.__tasks):
            raise UserWarning("Task {} is not valid.".format(task))
        self.signals[task].disconnect()

    def hasActiveTask(self):
        """Check if any task is active."""
        return any(self.__tasks.values())

    def isActive(self, task):
        """Check if a sepcific task is active."""
        try:
            return self.__tasks[task]
        except:
            return False

    def activateTask(self, task):
        """Activate a task."""
        if not (task in self.__tasks):
            raise UserWarning("Task {} is not valid.".format(task))

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
            raise UserWarning("Task {} is not valid.".format(task))
        self.__tasks[task] = False

    def execTask(self, task):
        """Execute task."""
        self.__methods[task]()

    def execActiveTasks(self):
        """Exectute all active tasks."""
        for task, active in self.__tasks.items():
            if active:
                self.execTask(task)

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

    def emit(self, task, msg):
        """Emit signal."""
        if not (task in self.__tasks):
            raise UserWarning("Task {} is not valid.".format(task))
        self.signals[task].emit(str(msg))

    def run(self):
        """Run the thread."""
        print("Starting")
        module_logger.info("A TasksThread is starting.")

        while self.hasActiveTask():
            self.execActiveTasks()
            self.__wait()

        print("Done")
        module_logger.info("A TasksThread is done.")
