#!/usr/bin/env python
import logging

# create logger
module_logger = logging.getLogger('scctool.view.widgets')

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import os
import re
import shutil


class MapLineEdit(QLineEdit):
    textModified = pyqtSignal(str, str)  # (before, after)

    def __init__(self, contents='', parent=None):
        super(MapLineEdit, self).__init__(contents, parent)
        self.editingFinished.connect(self.__handleEditingFinished)
        self.textChanged.connect(self.__handleTextChanged)
        self._before = contents

    def __handleTextChanged(self, text):
        if not self.hasFocus():
            self._before = text

    def __handleEditingFinished(self):
        before, after = self._before, self.text()
        if before != after:
            after, known = scctool.matchdata.autoCorrectMap(after)
            self.setText(after)
            self._before = after
            self.textModified.emit(before, after)


class MonitoredLineEdit(QLineEdit):

    textModified = pyqtSignal()

    def __init__(self, contents='', parent=None):
        super(MonitoredLineEdit, self).__init__(contents, parent)
        self.editingFinished.connect(self.__handleEditingFinished)
        self.textChanged.connect(self.__handleTextChanged)
        self._before = contents

    def __handleTextChanged(self, text):
        if not self.hasFocus():
            self._before = text

    def setTextMonitored(self, after):
        if self._before != after:
            self.textModified.emit()

        self.setText(after)

    def __handleEditingFinished(self):
        before, after = self._before, self.text()
        if before != after:
            #after, known = scctool.matchdata.autoCorrectMap(after)
            self.setText(after)
            self._before = after
            self.textModified.emit()


class StyleComboBox(QComboBox):

    def __init__(self, style_dir, default="Default"):
        super(StyleComboBox, self).__init__()

        self.__style_dir = style_dir

        for fname in os.listdir(style_dir):
            full_fname = os.path.join(style_dir, fname)
            if os.path.isfile(full_fname):
                label = re.search('^(.+)\.css$', fname).group(1)
                self.addItem(label)

        index = self.findText(default, Qt.MatchFixedString)
        if index >= 0:
            self.setCurrentIndex(index)
        else:
            index = self.findText("Default", Qt.MatchFixedString)
            if index >= 0:
                self.setCurrentIndex(index)

    def apply(self, controller, file):
        newfile = os.path.join(self.__style_dir, self.currentText() + ".css")
        shutil.copy(newfile, file)

        fname = os.path.basename(file)
        dirs = os.path.dirname(file)
        back = dirs.split("/")
        for i in range(len(back)):
            back[i] = ".."
        back = "/".join(back)

        controller.ftpUploader.cwd(dirs)
        controller.ftpUploader.upload(file, fname)
        controller.ftpUploader.cwd(back)


class FTPsetup(QProgressDialog):

    def __init__(self, controller, mainWindow):
        QProgressDialog.__init__(self)
        self.progress = 0
        self.setWindowTitle("FTP Server Setup")
        self.setLabelText(
            "Setting up the required file structure on the FTP server...")
        self.canceled.connect(self.close)
        self.setRange(0, 100)
        self.setValue(self.minimum())

        self.resize(QSize(self.sizeHint().width(), self.sizeHint().height()))
        self.move(mainWindow.pos() + QPoint(mainWindow.size().width() / 2, mainWindow.size().height() / 3)
                  - QPoint(self.size().width() / 2, self.size().height() / 3))
        self.show()

        old_bool = mainWindow.mainWindow.cb_autoFTP.isChecked()
        mainWindow.mainWindow.cb_autoFTP.setChecked(False)
        controller.ftpUploader.empty_queque()
        mainWindow.mainWindow.cb_autoFTP.setChecked(True)

        signal, range = controller.ftpUploader.setup()
        signal.connect(self.setProgress)
        self.setRange(0, range)

        while not self.wasCanceled():
            QApplication.processEvents()
            time.sleep(0.05)

        mainWindow.mainWindow.cb_autoFTP.setChecked(False)

        if(self.progress != -2):
            controller.ftpUploader.empty_queque()
            mainWindow.mainWindow.cb_autoFTP.setChecked(old_bool)
        else:
            QMessageBox.warning(self, "Login error",
                                'FTP server login incorrect!')

        print("Done...")

    def setProgress(self, progress):
        self.progress = progress
        if(progress == -1):
            self.cancel()
        elif(progress == -2):
            print("Wrong login data")
            self.cancel()
        else:
            self.setValue(progress)


class BusyProgressBar(QProgressBar):

    def __init__(self):
        super().__init__()
        self.setRange(0, 0)
        self.setAlignment(Qt.AlignCenter)
        self._text = None

    def setText(self, text):
        self._text = text

    def text(self):
        return self._text


class ColorLayout(QHBoxLayout):
    def __init__(self, parent, label="Color:", color="#ffffff", default_color="#ffffff"):
        super(QHBoxLayout, self).__init__()
        self.__parent = parent
        self.__defaultColor = default_color
        label = QLabel(label)
        label.setMinimumWidth(110)
        self.addWidget(label, 1)
        self.__preview = QLineEdit()
        self.__preview.setReadOnly(True)
        self.__preview.setAlignment(Qt.AlignCenter)
        self.setColor(color, False)
        self.addWidget(self.__preview, 2)
        self.__pb_selectColor = QPushButton('Select')
        self.__pb_selectColor.clicked.connect(self.__openColorDialog)
        self.addWidget(self.__pb_selectColor, 0)
        self.__pb_default = QPushButton('Default')
        self.__pb_default.clicked.connect(self.reset)
        self.addWidget(self.__pb_default, 0)

    def __openColorDialog(self):
        color = QColorDialog.getColor(self.__currentColor)

        if color.isValid():
            self.setColor(color.name())

    def setColor(self, color, trigger=True):
        new_color = QColor(color)
        if(trigger and self.__currentColor != new_color):
            self.__parent.changed()
        self.__currentColor = new_color
        self.__preview.setText(color)
        self.__preview.setStyleSheet('background: ' + color)

        if(self.__currentColor.lightnessF() >= 0.5):
            self.__preview.setStyleSheet(
                'background: ' + color + ';color: black')
        else:
            self.__preview.setStyleSheet(
                'background: ' + color + ';color: white')

    def reset(self):
        self.setColor(self.__defaultColor)

    def getColor(self):
        return self.__currentColor.name()


class IconPushButton(QPushButton):
    def __init__(self, label=None, parent=None):
        super(IconPushButton, self).__init__(label, parent)

        self.pad = 4     # padding between the icon and the button frame
        self.minSize = 8  # minimum size of the icon

        sizePolicy = QSizePolicy(QSizePolicy.Expanding,
                                 QSizePolicy.Expanding)
        self.setSizePolicy(sizePolicy)

    def paintEvent(self, event):

        qp = QPainter()
        qp.begin(self)

        #---- get default style ----

        opt = QStyleOptionButton()
        self.initStyleOption(opt)

        #---- scale icon to button size ----

        Rect = opt.rect

        h = Rect.height()
        w = Rect.width()
        iconSize = max(min(h, w) - 2 * self.pad, self.minSize)

        opt.iconSize = QSize(iconSize, iconSize)

        #---- draw button ----

        self.style().drawControl(QStyle.CE_PushButton, opt, qp, self)

        qp.end()


class ListTable(QTableWidget):
    dataModified = pyqtSignal()

    def __init__(self, noColumns=1, data=[]):
        super(ListTable, self).__init__()

        data = self.__processData(data)
        self.__noColumns = noColumns

        self.setCornerButtonEnabled(False)
        self.horizontalHeader().hide()
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.verticalHeader().hide()
        self.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.setData(data)

    def __handleDataChanged(self, item):
        self.setData(self.getData())
        self.dataModified.emit()

    def __processData(self, data):
        seen = set()
        uniq = [x for x in data if x not in seen and not seen.add(x)]
        uniq.sort()
        return uniq

    def setData(self, data):
        try:
            self.itemChanged.disconnect()
        except:
            pass

        self.setColumnCount(self.__noColumns)
        self.setRowCount(int(len(data) / self.__noColumns) + 1)
        for idx, entry in enumerate(data):
            row, column = divmod(idx, self.__noColumns)
            self.setItem(row, column, QTableWidgetItem(entry))

        row = int(len(data) / self.__noColumns)
        for col in range(len(data) % self.__noColumns, self.__noColumns):
            self.setItem(row, col, QTableWidgetItem(""))

        row = int(len(data) / self.__noColumns) + 1
        for col in range(self.__noColumns):
            self.setItem(row, col, QTableWidgetItem(""))

        self.itemChanged.connect(self.__handleDataChanged)

    def getData(self):
        data = []
        for row in range(self.rowCount()):
            for col in range(self.columnCount()):
                try:
                    element = self.item(row, col).text().strip()
                    if(element == ""):
                        continue
                    data.append(element)
                except:
                    pass
        return self.__processData(data)


class Completer(QCompleter):

    def __init__(self, list, parent=None):
        super(Completer, self).__init__(list, parent)

        self.setCaseSensitivity(Qt.CaseInsensitive)
        self.setCompletionMode(QCompleter.PopupCompletion)
        self.setWrapAround(False)

    # Add texts instead of replace
    def pathFromIndex(self, index):
        path = QCompleter.pathFromIndex(self, index)

        lst = str(self.widget().text()).split(' ')

        if len(lst) > 1:
            path = '%s %s' % (' '.join(lst[:-1]), path)

        return path

    # Add operator to separate between texts
    def splitPath(self, path):
        path = str(path.split(' ')[-1]).lstrip(' ')
        return [path]


class QHLine(QFrame):

    def __init__(self):
        super(QHLine, self).__init__()
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)


class MapDialog(QDialog):

    def __init__(self, parent=None):
        super(Form, self).__init__(parent)
        # Create widgets
        self.edit = QLineEdit("Write my name here")
        self.button = QPushButton("Show Greetings")
        # Create layout and add widgets
        layout = QVBoxLayout()
        layout.addWidget(self.edit)
        layout.addWidget(self.button)
        # Set dialog layout
        self.setLayout(layout)
        # Add button signal to greetings slot
        self.button.clicked.connect(self.greetings)

    # Greets the user
    def greetings(self):
        print("Hello %s" % self.edit.text())
