import logging

from PyQt5.QtCore import QDateTime, Qt, QTime
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import (QAction, QCheckBox, QDateTimeEdit, QGridLayout,
                             QLabel, QLineEdit, QMenu, QPushButton,
                             QRadioButton, QTimeEdit, QWidget)

import scctool.settings.config

module_logger = logging.getLogger(__name__)


class CountdownWidget(QWidget):
    """Define custom widget as countdown control panel."""

    def __init__(self, ctrl, parent=None):
        """Init completer."""
        super().__init__(parent)
        self.controller = ctrl
        self.createLayout()
        self.loadSettings()
        self.connect()

    def createLayout(self):
        """Create widget to control the countdown browser source."""
        layout = QGridLayout()
        self.rb_static = QRadioButton(
            _("Static Countdown to date:"), self)
        layout.addWidget(self.rb_static, 0, 0)
        self.rb_dynamic = QRadioButton(
            _("Dynamic Countdown duration:"), self)
        self.rb_dynamic.setChecked(True)
        self.rb_dynamic.toggled.connect(self.toggleRadio)
        layout.addWidget(self.rb_dynamic, 1, 0)
        self.te_datetime = QDateTimeEdit()
        self.te_datetime.setCalendarPopup(True)
        self.te_datetime.setContextMenuPolicy(Qt.CustomContextMenu)
        self.te_datetime.customContextMenuRequested.connect(
            self.openDateTimeMenu)
        layout.addWidget(self.te_datetime, 0, 1)
        self.te_duration = QTimeEdit()
        self.te_duration.setDisplayFormat("HH 'h' mm 'm' ss 's'")
        self.te_duration.setContextMenuPolicy(Qt.CustomContextMenu)
        self.te_duration.customContextMenuRequested.connect(
            self.openDurationMenu)
        layout.addWidget(self.te_duration, 1, 1)
        self.event_label = QLabel(' ' + _('Event description:'))
        layout.addWidget(self.event_label, 0, 2)
        self.le_desc = QLineEdit()
        self.le_desc.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.le_desc, 0, 3, 1, 2)
        self.cb_restart = QCheckBox(
            _('Restart countdown when source becomes active'))
        layout.addWidget(self.cb_restart, 1, 2, 1, 2)
        self.pb_start = QPushButton(" " + _('Start Countdown') + " ")
        layout.addWidget(self.pb_start, 1, 4)
        layout.setColumnStretch(2, 1)
        layout.setColumnStretch(3, 2)
        self.setLayout(layout)

    def openDateTimeMenu(self, position):
        menu = QMenu()
        act1 = QAction(_("Set Today"))
        act1.triggered.connect(self.setToday)
        menu.addAction(act1)
        menu.exec_(QCursor.pos())

    def openDurationMenu(self, position):
        menu = QMenu()
        for duration in [15, 10, 5, 3, 1]:
            act = QAction(_("Set {} min").format(duration), menu)
            act.triggered.connect(
                lambda x, duration=duration: self.setDuration(duration))
            menu.addAction(act)
        menu.exec_(QCursor.pos())

    def setToday(self):
        today = QDateTime.currentDateTime()
        today.setTime(self.te_datetime.time())
        self.te_datetime.setDateTime(today)

    def setDuration(self, duration):
        self.te_duration.setTime(QTime(0, duration, 0))

    def toggleRadio(self):
        static = self.rb_static.isChecked()
        self.te_datetime.setEnabled(static)
        self.te_duration.setEnabled(not static)
        self.cb_restart.setEnabled(not static)
        self.pb_start.setEnabled(not static)

    def loadSettings(self):
        static = scctool.settings.config.parser.getboolean(
            "Countdown", "static")
        if static:
            self.rb_static.setChecked(True)
        else:
            self.rb_dynamic.setChecked(True)
        description = scctool.settings.config.parser.get(
            'Countdown', 'description')
        self.le_desc.setText(description.strip())
        restart = scctool.settings.config.parser.getboolean(
            "Countdown", "restart")
        self.cb_restart.setChecked(restart)

        duration = QTime()
        string = scctool.settings.config.parser.get(
            'Countdown', 'duration').strip()
        duration = QTime.fromString(string, 'HH:mm:ss')
        self.te_duration.setTime(duration)

        string = scctool.settings.config.parser.get(
            'Countdown', 'datetime').strip()
        datetime = QDateTime.fromString(string, 'yyyy-MM-dd HH:mm')
        self.te_datetime.setDateTime(datetime)

    def connect(self):
        self.le_desc.textChanged.connect(self.changed_description)
        self.cb_restart.toggled.connect(self.changed_restart)
        self.te_datetime.dateTimeChanged.connect(self.changed_datetime)
        self.te_duration.timeChanged.connect(self.changed_duration)
        self.rb_static.toggled.connect(self.changed_static)
        self.pb_start.pressed.connect(self.start_pressed)

    def changed_description(self):
        desc = self.le_desc.text().strip()
        scctool.settings.config.parser.set('Countdown', 'description', desc)
        self.controller.websocketThread.sendData2Path(
            'countdown', "DESC", desc)

    def changed_restart(self):
        restart = self.cb_restart.isChecked()
        scctool.settings.config.parser.set(
            'Countdown', 'restart', str(restart))
        self.controller.websocketThread.sendData2Path(
            'countdown', "RESTART", restart)

    def changed_datetime(self, time):
        datetime = time.toString('yyyy-MM-dd HH:mm')
        scctool.settings.config.parser.set('Countdown', 'datetime', datetime)
        self.sendData()

    def changed_duration(self, time):
        duration = time.toString('HH:mm:ss')
        scctool.settings.config.parser.set('Countdown', 'duration', duration)
        self.sendData()

    def changed_static(self):
        static = self.rb_static.isChecked()
        scctool.settings.config.parser.set('Countdown', 'static', str(static))
        self.sendData()

    def start_pressed(self):
        self.controller.websocketThread.sendData2Path('countdown', 'START')

    def sendData(self):
        data = {}
        data['static'] = scctool.settings.config.parser.getboolean(
            'Countdown', 'static')
        data['desc'] = scctool.settings.config.parser.get(
            'Countdown', 'description')
        data['restart'] = scctool.settings.config.parser.getboolean(
            'Countdown', 'restart')
        data['datetime'] = scctool.settings.config.parser.get(
            'Countdown', 'datetime')
        data['duration'] = scctool.settings.config.parser.get(
            'Countdown', 'duration')
        data['replacement'] = scctool.settings.config.parser.get(
            'Countdown', 'replacement')
        self.controller.websocketThread.sendData2Path(
            'countdown', "DATA", data)
