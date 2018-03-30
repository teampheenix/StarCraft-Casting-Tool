"""Define PyQt5 widgets."""
import logging
import PyQt5
import os
import re
import shutil
import time
import scctool.matchdata
import scctool.settings.config
import scctool.tasks.updater
import humanize
import keyboard

# create logger
module_logger = logging.getLogger('scctool.view.widgets')


class MapLineEdit(PyQt5.QtWidgets.QLineEdit):
    """Define line edit for maps."""

    textModified = PyQt5.QtCore.pyqtSignal(str, str)  # (before, after)

    def __init__(self, contents='', parent=None):
        """Init lineedit."""
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


class MonitoredLineEdit(PyQt5.QtWidgets.QLineEdit):
    """Define moinitored line edit."""

    textModified = PyQt5.QtCore.pyqtSignal()

    def __init__(self, contents='', parent=None):
        """Init moinitored line edit."""
        super(MonitoredLineEdit, self).__init__(contents, parent)
        self.editingFinished.connect(self.__handleEditingFinished)
        self.textChanged.connect(self.__handleTextChanged)
        self._before = contents

    def __handleTextChanged(self, text):
        if not self.hasFocus():
            self._before = text

    def setTextMonitored(self, after):
        """Set the text and mointor change."""
        if self._before != after:
            self.textModified.emit()

        self.setText(after)

    def __handleEditingFinished(self):
        before, after = self._before, self.text()
        if before != after:
            # after, known = scctool.matchdata.autoCorrectMap(after)
            self.setText(after)
            self._before = after
            self.textModified.emit()


class StyleComboBox(PyQt5.QtWidgets.QComboBox):
    """Define combo box to change the styles."""

    def __init__(self, style_dir, default="Default"):
        """Init combo box to change the styles."""
        super(StyleComboBox, self).__init__()

        self.__style_dir = style_dir
        style_dir = scctool.settings.getAbsPath(style_dir)

        for fname in os.listdir(style_dir):
            full_fname = os.path.join(style_dir, fname)
            if os.path.isfile(full_fname):
                label = re.search('^(.+)\.css$', fname).group(1)
                self.addItem(label)

        index = self.findText(default, PyQt5.QtCore.Qt.MatchFixedString)
        if index >= 0:
            self.setCurrentIndex(index)
        else:
            index = self.findText("Default", PyQt5.QtCore.Qt.MatchFixedString)
            if index >= 0:
                self.setCurrentIndex(index)

    def apply(self, controller, file):
        """Apply the changes to the css files."""
        new_file = os.path.join(self.__style_dir, self.currentText() + ".css")
        new_file = scctool.settings.getAbsPath(new_file)
        shutil.copy(new_file, scctool.settings.getAbsPath(file))

        fname = os.path.basename(file)
        dirs = os.path.dirname(file)

        controller.ftpUploader.cwd(dirs)
        controller.ftpUploader.upload(file, fname)
        controller.ftpUploader.cwdback(dirs)

    def applyWebsocket(self, controller):
        controller.websocketThread.changeStyle(self.currentText())


class FTPsetup(PyQt5.QtWidgets.QProgressDialog):
    """Define FTP setup progress dialog."""

    def __init__(self, controller, mainWindow):
        """Init progress dialog."""
        try:
            PyQt5.QtWidgets.QProgressDialog.__init__(self)
            self.setWindowModality(PyQt5.QtCore.Qt.ApplicationModal)
            self.progress = 0
            self.setWindowTitle(_("FTP Server Setup"))
            self.setLabelText(
                _("Setting up the required file structure on the FTP server..."))
            self.canceled.connect(self.close)
            self.setRange(0, 100)
            self.setValue(self.minimum())

            self.resize(PyQt5.QtCore.QSize(
                self.sizeHint().width(), self.sizeHint().height()))
            relativeChange = PyQt5.QtCore.QPoint(mainWindow.size().width() / 2,
                                                 mainWindow.size().height() / 3)\
                - PyQt5.QtCore.QPoint(self.size().width() / 2,
                                      self.size().height() / 3)
            self.move(mainWindow.pos() + relativeChange)
            self.show()

            old_bool = mainWindow.cb_autoFTP.isChecked()
            mainWindow.cb_autoFTP.setChecked(False)
            controller.ftpUploader.empty_queque()
            mainWindow.cb_autoFTP.setChecked(True)

            signal, range = controller.ftpUploader.setup()
            signal.connect(self.setProgress)
            self.setRange(0, range)

            while not self.wasCanceled():
                PyQt5.QtWidgets.QApplication.processEvents()
                time.sleep(0.05)

            mainWindow.cb_autoFTP.setChecked(False)

            if(self.progress != -2):
                controller.ftpUploader.empty_queque()
                mainWindow.cb_autoFTP.setChecked(old_bool)
            else:
                PyQt5.QtWidgets.QMessageBox.warning(self, _("Login error"),
                                                    _('FTP server login incorrect!'))

        except Exception as e:
            module_logger.exception("message")
            mainWindow.cb_autoFTP.setChecked(False)

    def setProgress(self, progress):
        """Set the progress of the bar."""
        self.progress = progress
        if(progress == -1):
            self.cancel()
        elif(progress == -2):
            module_logger.info(_("Wrong login data for FTP"))
            self.cancel()
        else:
            self.setValue(progress)


class ToolUpdater(PyQt5.QtWidgets.QProgressDialog):
    """Define FTP setup progress dialog."""

    def __init__(self, controller, mainWindow):
        """Init progress dialog."""
        PyQt5.QtWidgets.QProgressDialog.__init__(self)
        self.setWindowModality(PyQt5.QtCore.Qt.ApplicationModal)
        self.progress = 0
        self.setWindowTitle(_("Updater"))
        self.setLabelText(
            _("Updating to a new version..."))
        self.setCancelButton(None)
        self.setRange(0, 1000)
        self.setValue(self.minimum())

        self.resize(PyQt5.QtCore.QSize(
            mainWindow.size().width() * 0.8, self.sizeHint().height()))
        relativeChange = PyQt5.QtCore.QPoint(mainWindow.size().width() / 2,
                                             mainWindow.size().height() / 3)\
            - PyQt5.QtCore.QPoint(self.size().width() / 2,
                                  self.size().height() / 3)
        self.move(mainWindow.pos() + relativeChange)
        self.show()

        controller.versionHandler.progress.connect(self.setProgress)
        controller.versionHandler.activateTask('update_app')

        while not self.wasCanceled():
            PyQt5.QtWidgets.QApplication.processEvents()
            time.sleep(0.05)

        controller.versionHandler.progress.disconnect(self.setProgress)

    def setProgress(self, data):
        """Set the progress of the bar."""
        # TODO: What is the data structure in case of a patch?
        try:
            text = _(
                'Downloading a new version: Total file size {}, Time remaining {}.')
            text = text.format(humanize.naturalsize(
                data['total']), data['time'])
            self.setLabelText(text)
            self.setValue(int(float(data['percent_complete']) * 10))
        except Exception as e:
            module_logger.exception("message")


class BusyProgressBar(PyQt5.QtWidgets.QProgressBar):
    """Define a busy progress bar."""

    def __init__(self):
        """Init the progress of the bar."""
        super().__init__()
        self.setRange(0, 0)
        self.setAlignment(PyQt5.QtCore.Qt.AlignCenter)
        self._text = None

    def setText(self, text):
        """Set the text of the bar."""
        self._text = text

    def text(self):
        """Return the text of the bar."""
        return self._text


class HotkeyLayout(PyQt5.QtWidgets.QHBoxLayout):

    modified = PyQt5.QtCore.pyqtSignal(str)

    def __init__(self, parent, label="Hotkey", hotkey=""):
        """Init box."""
        super(PyQt5.QtWidgets.QHBoxLayout, self).__init__()
        self.data = scctool.settings.config.loadHotkey(hotkey)
        self.__parent = parent
        label = PyQt5.QtWidgets.QLabel(label + ":")
        label.setMinimumWidth(50)
        self.addWidget(label, 1)
        self.__preview = PyQt5.QtWidgets.QLineEdit()
        self.__preview.setReadOnly(True)
        self.__preview.setText(self.data['name'])
        self.__preview.setPlaceholderText(_("Not set"))
        self.__preview.setAlignment(PyQt5.QtCore.Qt.AlignCenter)
        self.addWidget(self.__preview, 1)
        # self.__pb_setHotKey = PyQt5.QtWidgets.QPushButton(_('Set Hotkey'))
        # self.__pb_setHotKey.clicked.connect(self.setHotkey)
        # self.addWidget(self.__pb_setHotKey, 0)
        self.__pb_set = PyQt5.QtWidgets.QPushButton(_('Set Hotkey'))
        self.__pb_set.clicked.connect(self.setKey)
        self.addWidget(self.__pb_set, 0)
        self.__pb_clear = PyQt5.QtWidgets.QPushButton(_('Clear'))
        self.__pb_clear.clicked.connect(self.clear)
        self.addWidget(self.__pb_clear, 0)

    def setKey(self):
        event = keyboard.read_event()

        self.data['scan_code'] = event.scan_code
        self.data['is_keypad'] = event.is_keypad
        self.data['name'] = event.name
        if event.is_keypad:
            self.data['name'] = "num " + self.data['name']
        self.data['name'] = self.data['name'].upper().replace(
            "LEFT ", '').replace("RIGHT ", '')
        self.__preview.setText(self.data['name'])
        self.modified.emit(self.data['name'])

    def setHotkey(self):
        key = keyboard.read_hotkey()
        self.__preview.setText(key)
        self.modified.emit(key)

    def clear(self):
        self.__preview.setText("")
        self.data = {'name': '', 'scan_code': 0, 'is_keypad': False}
        self.modified.emit("")

    def getKey(self):
        return self.data

    def check_dublicate(self, key):
        if str(key) and key == self.data['name']:
            self.clear()


class ColorLayout(PyQt5.QtWidgets.QHBoxLayout):
    """Define box the select colors."""

    def __init__(self, parent, label="Color:", color="#ffffff", default_color="#ffffff"):
        """Init box."""
        super(PyQt5.QtWidgets.QHBoxLayout, self).__init__()
        self.__parent = parent
        self.__defaultColor = default_color
        label = PyQt5.QtWidgets.QLabel(label)
        label.setMinimumWidth(110)
        self.addWidget(label, 1)
        self.__preview = PyQt5.QtWidgets.QLineEdit()
        self.__preview.setReadOnly(True)
        self.__preview.setAlignment(PyQt5.QtCore.Qt.AlignCenter)
        self.setColor(color, False)
        self.addWidget(self.__preview, 2)
        self.__pb_selectColor = PyQt5.QtWidgets.QPushButton(_('Select'))
        self.__pb_selectColor.clicked.connect(self.__openColorDialog)
        self.addWidget(self.__pb_selectColor, 0)
        self.__pb_default = PyQt5.QtWidgets.QPushButton(_('Default'))
        self.__pb_default.clicked.connect(self.reset)
        self.addWidget(self.__pb_default, 0)

    def __openColorDialog(self):
        color = PyQt5.QtWidgets.QColorDialog.getColor(self.__currentColor)

        if color.isValid():
            self.setColor(color.name())

    def setColor(self, color, trigger=True):
        """Set the new color."""
        new_color = PyQt5.QtGui.QColor(color)
        if(trigger and self.__currentColor != new_color):
            self.__parent.changed()
        self.__currentColor = new_color
        self.__preview.setText(color)
        self.__preview.setStyleSheet('background:' + ' ' + color)

        if(self.__currentColor.lightnessF() >= 0.5):
            self.__preview.setStyleSheet(
                'background: ' + color + ';color: black')
        else:
            self.__preview.setStyleSheet(
                'background: ' + color + ';color: white')

    def reset(self):
        """Set the color to the default value."""
        self.setColor(self.__defaultColor)

    def getColor(self):
        """Get the hex of the color."""
        return self.__currentColor.name()


class IconPushButton(PyQt5.QtWidgets.QPushButton):
    """Define push button with icon."""

    def __init__(self, label=None, parent=None):
        """Init button."""
        super(IconPushButton, self).__init__(label, parent)

        self.pad = 4     # padding between the icon and the button frame
        self.minSize = 8  # minimum size of the icon

        sizePolicy = PyQt5.QtWidgets.QSizePolicy(PyQt5.QtWidgets.QSizePolicy.Expanding,
                                                 PyQt5.QtWidgets.QSizePolicy.Expanding)
        self.setSizePolicy(sizePolicy)

    def paintEvent(self, event):
        """Paint event."""
        qp = PyQt5.QtGui.QPainter()
        qp.begin(self)

        # ---- get default style ----

        opt = PyQt5.QtWidgets.QStyleOptionButton()
        self.initStyleOption(opt)

        # ---- scale icon to button size ----

        Rect = opt.rect

        h = Rect.height()
        w = Rect.width()
        iconSize = max(min(h, w) - 2 * self.pad, self.minSize)

        opt.iconSize = PyQt5.QtCore.QSize(iconSize, iconSize)

        # ---- draw button ----

        self.style().drawControl(PyQt5.QtWidgets.QStyle.CE_PushButton, opt, qp, self)

        qp.end()


class ListTable(PyQt5.QtWidgets.QTableWidget):
    """Define a custom table list."""

    dataModified = PyQt5.QtCore.pyqtSignal()

    def __init__(self, noColumns=1, data=[]):
        """Init table list."""
        super(ListTable, self).__init__()

        data = self.__processData(data)
        self.__noColumns = noColumns

        self.setCornerButtonEnabled(False)
        self.horizontalHeader().hide()
        self.horizontalHeader().setSectionResizeMode(
            PyQt5.QtWidgets.QHeaderView.Stretch)
        self.verticalHeader().hide()
        self.verticalHeader().setSectionResizeMode(
            PyQt5.QtWidgets.QHeaderView.ResizeToContents)
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
        """Set the data."""
        try:
            self.itemChanged.disconnect()
        except Exception:
            pass

        self.setColumnCount(self.__noColumns)
        self.setRowCount(int(len(data) / self.__noColumns) + 1)
        for idx, entry in enumerate(data):
            row, column = divmod(idx, self.__noColumns)
            self.setItem(row, column, PyQt5.QtWidgets.QTableWidgetItem(entry))

        row = int(len(data) / self.__noColumns)
        for col in range(len(data) % self.__noColumns, self.__noColumns):
            self.setItem(row, col, PyQt5.QtWidgets.QTableWidgetItem(""))

        row = int(len(data) / self.__noColumns) + 1
        for col in range(self.__noColumns):
            self.setItem(row, col, PyQt5.QtWidgets.QTableWidgetItem(""))

        self.itemChanged.connect(self.__handleDataChanged)

    def getData(self):
        """Get the data."""
        data = []
        for row in range(self.rowCount()):
            for col in range(self.columnCount()):
                try:
                    element = self.item(row, col).text().strip()
                    if(element == ""):
                        continue
                    data.append(element)
                except Exception:
                    pass
        return self.__processData(data)


class Completer(PyQt5.QtWidgets.QCompleter):
    """Define custom auto completer for multiple words."""

    def __init__(self, list, parent=None):
        """Init completer."""
        super(Completer, self).__init__(list, parent)

        self.setCaseSensitivity(PyQt5.QtCore.Qt.CaseInsensitive)
        self.setCompletionMode(PyQt5.QtWidgets.QCompleter.PopupCompletion)
        self.setWrapAround(False)

    def pathFromIndex(self, index):
        """Add texts instead of replace."""
        path = PyQt5.QtWidgets.QCompleter.pathFromIndex(self, index)

        lst = str(self.widget().text()).split(' ')

        if len(lst) > 1:
            path = '%s %s' % (' '.join(lst[:-1]), path)

        return path

    def splitPath(self, path):
        """Add operator to separate between texts."""
        path = str(path.split(' ')[-1]).lstrip(' ')
        return [path]


class QHLine(PyQt5.QtWidgets.QFrame):
    """Define a vertical line."""

    def __init__(self):
        """Init frame."""
        super(QHLine, self).__init__()
        self.setFrameShape(PyQt5.QtWidgets.QFrame.HLine)
        self.setFrameShadow(PyQt5.QtWidgets.QFrame.Sunken)


class InitialUpdater(PyQt5.QtWidgets.QProgressDialog):
    """Define initial progress dialog to download data."""

    def __init__(self, version='0.0.0'):
        """Init progress dialog."""
        PyQt5.QtWidgets.QProgressDialog.__init__(self)
        self.setWindowModality(PyQt5.QtCore.Qt.ApplicationModal)
        self.progress = 0
        self.setWindowTitle("SCC-Tool")
        self.setLabelText(_("Collecting data..."))
        self.setCancelButton(None)
        self.setRange(0, 1010)
        self.setValue(50)
        self.version = version

        self.show()
        for i in range(10):
            PyQt5.QtWidgets.QApplication.processEvents()
        self.run()

    def run(self):
        """Run the initial process."""
        try:
            from scctool.settings.client_config import ClientConfig
            from scctool.tasks.updater import extractData
            from pyupdater.client import Client
            client = Client(ClientConfig())
            client.refresh()
            client.add_progress_hook(self.setProgress)

            lib_update = client.update_check(
                scctool.tasks.updater.VersionHandler.ASSET_NAME, self.version)
            if lib_update is not None:
                lib_update.download(async=False)
                self.setValue(500)
                self.setLabelText(_("Extracting data..."))
                extractData(lib_update, self.setCopyProgress)
                self.setLabelText(_("Done."))
                time.sleep(1)
                self.setValue(1010)
        except Exception as e:
            module_logger.exception("message")

    def setCopyProgress(self, int):
        """Set progress."""
        self.setValue(500 + int * 5)

    def setProgress(self, data):
        """Set the progress of the bar."""
        # TODO: What is the data structure in case of a patch?
        module_logger.info("Progress {}".format(data))
        try:
            text = _(
                'Downloading required files...: Total file size {}, Time remaining {}.')
            text = text.format(humanize.naturalsize(
                data['total']), data['time'])
            self.setLabelText(text)
            self.setValue(int(float(data['percent_complete']) * 5))
        except Exception as e:
            module_logger.exception("message")


class DragImageLabel(PyQt5.QtWidgets.QLabel):

    def __init__(self, logo, team=0):
        super(PyQt5.QtWidgets.QLabel, self).__init__()

        self._team = team

        self._iconsize = logo._iconsize
        self._logomanager = logo._manager

        self.setFixedWidth(self._iconsize)
        self.setFixedHeight(self._iconsize)
        self.setAlignment(PyQt5.QtCore.Qt.AlignCenter)

        self.setLogo(logo)
        self.setAcceptDrops(False)

    def setLogo(self, logo):
        self.setPixmap(logo.provideQPixmap())

    def dragEnterEvent(self, e):
        data = e.mimeData()
        if data.hasFormat("application/x-qabstractitemmodeldatalist"):
            e.accept()
        else:
            e.ignore()

    def dropEvent(self, e):
        result = self.decodeMimeData(e.mimeData().data(
            "application/x-qabstractitemmodeldatalist"))
        map = result[0][1].pixmap(self._iconsize)
        self.setPixmap(map)

        if self._team == 1:
            ident = self._logomanager.pixmap2ident(map)
            print("Ident: ", ident)
            logo = self._logomanager.findLogo(ident)
            self._logomanager.setTeam1Logo(logo)
        elif self._team == 2:
            ident = self._logomanager.pixmap2ident(map)
            logo = self._logomanager.findLogo(ident)
            self._logomanager.setTeam2Logo(logo)

    def decodeMimeData(self, data):
        result = {}
        value = PyQt5.QtCore.QVariant()
        stream = PyQt5.QtCore.QDataStream(data)
        while not stream.atEnd():
            stream.readInt32()
            col = stream.readInt32()
            item = result.setdefault(col, {})
            for role in range(stream.readInt32()):
                key = PyQt5.QtCore.Qt.ItemDataRole(stream.readInt32())
                stream >> value
                item[key] = value.value()
        return result
