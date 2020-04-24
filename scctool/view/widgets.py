"""Various custom PyQt5 widgets."""
import logging
import os
import re
import time

import humanize
import keyboard
import requests
from PyQt5.QtCore import (QMimeData, QPoint, QPointF, QSettings, QSize, Qt,
                          pyqtProperty, pyqtSignal)
from PyQt5.QtGui import (QBrush, QColor, QDrag, QIcon, QKeySequence, QPainter,
                         QPen, QRadialGradient)
from PyQt5.QtWidgets import (QAbstractButton, QAction, QApplication, QCheckBox,
                             QColorDialog, QComboBox, QCompleter, QFileDialog,
                             QFormLayout, QFrame, QGroupBox, QHBoxLayout,
                             QHeaderView, QInputDialog, QLabel, QLineEdit,
                             QListWidget, QListWidgetItem, QMenu, QMessageBox,
                             QProgressBar, QProgressDialog, QPushButton,
                             QRadioButton, QShortcut, QSizePolicy, QStyle,
                             QStyleOptionButton, QTableWidget,
                             QTableWidgetItem, QTextBrowser, QTreeWidget,
                             QTreeWidgetItem)

import scctool.matchdata
import scctool.settings.config
import scctool.settings.translation
import scctool.tasks.updater
from scctool.settings.client_config import ClientConfig
from scctool.tasks.tasksthread import TasksThread


# create logger
module_logger = logging.getLogger(__name__)
_ = scctool.settings.translation.gettext


class MapLineEdit(QLineEdit):
    """Define line edit for maps."""

    textModified = pyqtSignal()  # (before, after)

    def __init__(self, contents='', parent=None):
        """Init lineedit."""
        super().__init__(contents, parent)
        self.editingFinished.connect(self.__handleEditingFinished)
        self.textChanged.connect(self.__handleTextChanged)
        self._before = contents

    def __handleTextChanged(self, text):
        if not self.hasFocus():
            self._before = text

    def __handleEditingFinished(self):
        text = self.text()
        before, after = self._before, text
        if before != after:
            after, __ = scctool.matchdata.autoCorrectMap(after)
            self.setText(after)
            self._before = after
            self.textModified.emit()

    def completerFinished(self, text):
        """Get called when the completer is finished to emit a signal."""
        before, after = self._before, text
        if before != after:
            self.setText(after)
            self._before = after
            self.textModified.emit()


class MonitoredLineEdit(QLineEdit):
    """Define moinitored line edit."""

    textModified = pyqtSignal()

    def __init__(self, contents='', parent=None):
        """Init moinitored line edit."""
        super().__init__(contents, parent)
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
            self.setText(after)
            self._before = after
            self.textModified.emit()

    def completerFinished(self, text):
        """Get called when the completer is finished to emit a signal."""
        before, after = self._before, text
        if before != after:
            self.setText(after)
            self._before = after
            self.textModified.emit()


class StyleComboBox(QComboBox):
    """Define combo box to change the styles."""

    def __init__(self, style_dir, scope):
        """Init combo box to change the styles."""
        super().__init__()

        self.__style_dir = style_dir
        self.__scope = scope
        style_dir = scctool.settings.getAbsPath(style_dir)
        default = scctool.settings.config.parser.get("Style", self.__scope)

        for fname in os.listdir(style_dir):
            full_fname = os.path.join(style_dir, fname)
            if os.path.isfile(full_fname):
                match = re.search(r'^(.+)\.css$', fname)
                if not match:
                    continue
                else:
                    label = match.group(1)
                if ' ' in label:
                    os.rename(full_fname, os.path.join(
                        style_dir, label.replace(' ', '-') + '.css'))
                label = label.replace('-', ' ')
                self.addItem(label)

        index = self.findText(default.replace('-', ' '), Qt.MatchFixedString)
        if index >= 0:
            self.setCurrentIndex(index)
        else:
            index = self.findText("Default", Qt.MatchFixedString)
            if index >= 0:
                self.setCurrentIndex(index)

        self.currentIndexChanged.connect(self.save)

    def connect2WS(self, controller, path):
        """Connect the style box to a websocket."""
        self.currentIndexChanged.connect(
            lambda x, controller=controller, path=path:
            self.applyWS(controller, path))

    def applyWS(self, controller, path):
        """Apply the stlye change to a websocket."""
        controller.websocketThread.changeStyle(
            path, self.currentText().replace(' ', '-'))

    def save(self):
        """Save the style to the config."""
        scctool.settings.config.parser.set(
            "Style", self.__scope,
            self.currentText().replace(' ', '-'))


class MapDownloader(QProgressDialog):
    """Map logo downloader dialog."""

    def __init__(self, mainWindow, map_name, url):
        """Init progress dialog."""
        super().__init__(mainWindow)
        self.setWindowModality(Qt.ApplicationModal)
        self.progress = 0

        self.url = url
        self._session = requests.Session()
        self._session.trust_env = False
        __, ext = os.path.splitext(url)
        ext = ext.split("?")[0].lower()
        sc2_map = map_name.strip().replace(" ", "_") + ext
        mapdir = scctool.settings.getAbsPath(scctool.settings.casting_html_dir)
        if ext not in ['.jpg', '.png']:
            raise ValueError('Not supported image format.')
        self.file_name = os.path.normpath(
            os.path.join(mapdir, "src/img/maps", sc2_map))

        self.setWindowTitle(_("Map Downloader"))
        self.setLabelText(
            _("Downloading {}".format(self.file_name)))
        self.setCancelButton(None)
        self.setRange(0, 100)
        self.setValue(self.minimum())

        self.resize(QSize(
            mainWindow.size().width() * 0.8, self.sizeHint().height()))
        relativeChange = QPoint(int(mainWindow.size().width() / 2),
                                int(mainWindow.size().height() / 3))\
            - QPoint(int(self.size().width() / 2),
                     int(self.size().height() / 3))
        self.move(mainWindow.pos() + relativeChange)

    def download(self):
        """Download a map."""
        self.show()
        for __ in range(10):
            QApplication.processEvents()

        with open(self.file_name, "wb") as f:
            module_logger.info("Downloading {} from {}".format(
                self.file_name, self.url))
            response = self._session.get(self.url, stream=True)
            total_length = response.headers.get('content-length')

            if total_length is None:  # no content length header
                f.write(response.content)
            else:
                dl = 0
                total_length = int(total_length)
                for data in response.iter_content(chunk_size=4096):
                    dl += len(data)
                    f.write(data)
                    done = int(100 * dl / total_length)
                    self.setProgress(done)

        return True

    def setProgress(self, value):
        """Set the progress of the bar."""
        try:
            self.setValue(value)
        except Exception:
            module_logger.exception("message")


class HotkeyLayout(QHBoxLayout):
    """Layout to set hotkeys."""

    modified = pyqtSignal(str, str)

    def __init__(self, parent, ident, label="Hotkey", hotkey=""):
        """Init box."""
        super().__init__()
        self.data = scctool.settings.config.loadHotkey(hotkey)
        self.__parent = parent
        self.__label = label
        self.__ident = ident
        self.__qlabel = QLabel(label + ":")
        self.__qlabel.setMinimumWidth(50)
        self.addWidget(self.__qlabel, 1)
        self.__preview = QLineEdit()
        self.__preview.setReadOnly(True)
        self.__preview.setText(self.data['name'])
        self.__preview.setPlaceholderText(_("Not set"))
        self.__preview.setAlignment(Qt.AlignCenter)
        self.addWidget(self.__preview, 1)
        self.__pb_set = QPushButton(_('Set Hotkey'))
        self.__pb_set.clicked.connect(self.setKey)
        self.addWidget(self.__pb_set, 0)
        self.__pb_clear = QPushButton(_('Clear'))
        self.__pb_clear.clicked.connect(self.clear)
        self.addWidget(self.__pb_clear, 0)

    def setDisabled(self, disabled=True):
        """Disable a hotkey."""
        self.__preview.setDisabled(disabled)
        self.__pb_set.setDisabled(disabled)
        self.__pb_clear.setDisabled(disabled)
        self.__qlabel.setDisabled(disabled)

    def setKey(self):
        """Record a new hotkey."""
        recorder = HotkeyRecorder(self.__parent, self.data, self.__label)
        self.data = recorder.run()
        self.__preview.setText(self.data['name'])
        self.modified.emit(self.data['name'], self.__ident)

    def setData(self, data):
        """Set the data."""
        self.data = data
        self.__preview.setText(self.data['name'])
        self.modified.emit(self.data['name'], self.__ident)

    def clear(self):
        """Clear the hotkey."""
        self.__preview.setText("")
        self.data = {'name': '', 'scan_code': 0, 'is_keypad': False}
        self.modified.emit("", self.__ident)

    def getKey(self):
        """Return the hotkey."""
        return self.data

    def check_dublicate(self, key, ident):
        """Check for a dublicate hotkey."""
        if str(key) and key == self.data['name']:
            self.clear()


class HotkeyRecorder(QProgressDialog):
    """Map logo downloader dialog."""

    def __init__(self, mainWindow, hotkeyData, name):
        """Init progress dialog."""
        super().__init__(mainWindow)
        self.setWindowModality(Qt.ApplicationModal)
        self.progress = 0
        self.hotkeyData = hotkeyData
        self.thread = TasksThread()

        self.setWindowTitle(_("Recording Hotkey") + "...")
        self.setLabelText(
            _("Press a Hotkey for {}").format(name) + "...")
        self.setRange(0, 0)
        self.setValue(self.minimum())

        self.resize(QSize(
            mainWindow.size().width() * 0.8, self.sizeHint().height()))
        relativeChange = QPoint(int(mainWindow.size().width() / 2),
                                int(mainWindow.size().height() / 3))\
            - QPoint(int(self.size().width() / 2),
                     int(self.size().height() / 3))
        self.move(mainWindow.pos() + relativeChange)

    def run(self):
        """Run the hotkey recorder."""
        self.show()
        self.thread = TasksThread()
        self.thread.addTask('hotkey', self.__record)
        self.thread.activateTask('hotkey')

        while self.thread.isRunning() and not self.wasCanceled():
            QApplication.processEvents()
            time.sleep(0.05)

        self.thread.terminate()
        self.close()

        return self.hotkeyData

    def __record(self):
        event = keyboard.read_event()

        self.hotkeyData['scan_code'] = event.scan_code
        self.hotkeyData['is_keypad'] = event.is_keypad
        self.hotkeyData['name'] = event.name
        if event.is_keypad:
            self.hotkeyData['name'] = "num " + self.hotkeyData['name']
        self.hotkeyData['name'] = self.hotkeyData['name'].upper().replace(
            "LEFT ", '').replace("RIGHT ", '')
        self.thread.deactivateTask('hotkey')


class LogoDownloader(QProgressDialog):
    """Define logo downloader dialog."""

    def __init__(self, controller, mainWindow, url):
        """Init progress dialog."""
        super().__init__()
        self.setWindowModality(Qt.ApplicationModal)
        self.progress = 0

        self.logo = controller.logoManager.newLogo()
        self.url = url
        self.file_name = self.logo.fromURL(self.url, False)
        self._session = requests.Session()
        self._session.trust_env = False

        self.setWindowTitle(_("Logo Downloader"))
        self.setLabelText(
            _("Downloading {}".format(self.file_name)))
        self.setCancelButton(None)
        self.setRange(0, 100)
        self.setValue(self.minimum())

        self.resize(QSize(
            mainWindow.size().width() * 0.8, self.sizeHint().height()))
        relativeChange = QPoint(int(mainWindow.size().width() / 2),
                                int(mainWindow.size().height() / 3))\
            - QPoint(int(self.size().width() / 2),
                     int(self.size().height() / 3))
        self.move(mainWindow.pos() + relativeChange)

    def download(self):
        """Download a logo."""
        self.show()
        self.setProgress(1)
        with open(self.file_name, "wb") as f:
            self.setProgress(5)
            module_logger.info("Downloading {}".format(self.file_name))
            response = self._session.get(self.url, stream=True)
            total_length = response.headers.get('content-length')

            if total_length is None:  # no content length header
                f.write(response.content)
            else:
                dl = 0
                total_length = int(total_length)
                for data in response.iter_content(chunk_size=4096):
                    dl += len(data)
                    f.write(data)
                    done = int(100 * dl / total_length)
                    self.setProgress(done)

        self.close()

        return self.logo

    def setProgress(self, value):
        """Set the progress of the bar."""
        try:
            self.setValue(value)
        except Exception:
            module_logger.exception("message")


class ToolUpdater(QProgressDialog):
    """Define updater dialog."""

    def __init__(self, controller, mainWindow):
        """Init progress dialog."""
        QProgressDialog.__init__(self)
        self.setWindowModality(Qt.ApplicationModal)
        self.progress = 0
        self.setWindowTitle(_("Updater"))
        self.setLabelText(
            _("Updating to a new version..."))
        self.setCancelButton(None)
        self.setRange(0, 1000)
        self.setValue(self.minimum())

        self.resize(QSize(
            mainWindow.size().width() * 0.8, self.sizeHint().height()))
        relativeChange = QPoint(int(mainWindow.size().width() / 2),
                                int(mainWindow.size().height() / 3))\
            - QPoint(int(self.size().width() / 2),
                     int(self.size().height() / 3))
        self.move(mainWindow.pos() + relativeChange)
        self.show()

        controller.versionHandler.progress.connect(self.setProgress)
        controller.versionHandler.activateTask('update_app')

        while not self.wasCanceled():
            QApplication.processEvents()
            time.sleep(0.05)

        controller.versionHandler.progress.disconnect(self.setProgress)

    def setProgress(self, data):
        """Set the progress of the bar."""
        # TODO: What is the data structure in case of a patch?
        try:
            text = _('Downloading a new version: Total file size {},'
                     ' Time remaining {}.')
            text = text.format(humanize.naturalsize(
                data.get('total', 0)), data.get('time', 0))
            self.setLabelText(text)
            self.setValue(int(float(data['percent_complete']) * 10))
        except Exception:
            module_logger.exception("message")


class BusyProgressBar(QProgressBar):
    """Define a busy progress bar."""

    def __init__(self):
        """Init the progress of the bar."""
        super().__init__()
        self.setRange(0, 0)
        self.setAlignment(Qt.AlignCenter)
        self._text = None

    def setText(self, text):
        """Set the text of the bar."""
        self._text = text

    def text(self):
        """Return the text of the bar."""
        return self._text


class ColorLayout(QHBoxLayout):
    """Define box the select colors."""

    def __init__(self, parent, label="Color:",
                 color="#ffffff", default_color="#ffffff"):
        """Init box."""
        super().__init__()
        self.__parent = parent
        self.__defaultColor = default_color
        self.__currentColor = default_color
        label = QLabel(label)
        label.setMinimumWidth(110)
        self.addWidget(label, 1)
        self.__preview = QLineEdit()
        self.__preview.setReadOnly(True)
        self.__preview.setAlignment(Qt.AlignCenter)
        self.setColor(color, False)
        self.addWidget(self.__preview, 2)
        self.__pb_selectColor = QPushButton(_('Select'))
        self.__pb_selectColor.clicked.connect(self.__openColorDialog)
        self.addWidget(self.__pb_selectColor, 0)
        self.__pb_default = QPushButton(_('Default'))
        self.__pb_default.clicked.connect(self.reset)
        self.addWidget(self.__pb_default, 0)

    def __openColorDialog(self):
        color = QColorDialog.getColor(self.__currentColor)

        if color.isValid():
            self.setColor(color.name())

    def setColor(self, color, trigger=True):
        """Set the new color."""
        new_color = QColor(color)
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


class IconPushButton(QPushButton):
    """Define push button with icon."""

    def __init__(self, label=None, parent=None):
        """Init button."""
        super().__init__(label, parent)

        self.pad = 4     # padding between the icon and the button frame
        self.minSize = 8  # minimum size of the icon

        sizePolicy = QSizePolicy(QSizePolicy.Expanding,
                                 QSizePolicy.Expanding)
        self.setSizePolicy(sizePolicy)

    def paintEvent(self, event):
        """Paint event."""
        qp = QPainter()
        qp.begin(self)

        # ---- get default style ----

        opt = QStyleOptionButton()
        self.initStyleOption(opt)

        # ---- scale icon to button size ----

        Rect = opt.rect

        h = Rect.height()
        w = Rect.width()
        iconSize = max(min(h, w) - 2 * self.pad, self.minSize)

        opt.iconSize = QSize(iconSize, iconSize)

        # ---- draw button ----

        self.style().drawControl(QStyle.CE_PushButton, opt, qp, self)

        qp.end()


class AligulacTreeView(QTreeWidget):
    """Tree view to connect players to aligulac ids."""

    def __init__(self, parent, manager):
        """Init the tree view."""
        super().__init__(parent)
        self.parent = parent
        self.manager = manager
        self.items = dict()
        self.setAnimated(True)
        self.headerItem().setText(0, "Playername")
        self.headerItem().setText(1, "Aligluac ID")

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.openMenu)

        self._insertData(self.manager.getList())

        self.shortcut1 = QShortcut(QKeySequence("DEL"), self)
        self.shortcut1.setAutoRepeat(False)
        self.shortcut1.setContext(Qt.WidgetWithChildrenShortcut)
        self.shortcut1.activated.connect(self.removeSelected)

        self.shortcut2 = QShortcut(QKeySequence("Return"), self)
        self.shortcut2.setAutoRepeat(False)
        self.shortcut2.setContext(Qt.WidgetWithChildrenShortcut)
        self.shortcut2.activated.connect(self.editSelected)

    def _insertData(self, data):
        for player, ident in data.items():
            self.items[player] = QTreeWidgetItem(
                self, [player, str(ident)])

        self.sortItems(0, Qt.AscendingOrder)

    def insertItem(self, name, new_id):
        """Insert item."""
        name = str(name).strip()
        if name in self.items:
            self.takeTopLevelItem(self.indexOfTopLevelItem(self.items[name]))
        self.manager.addID(name, new_id)
        self.items[name] = QTreeWidgetItem(
            self, [name, str(new_id)])

        self.sortItems(0, Qt.AscendingOrder)
        self.setCurrentItem(self.items[name])
        self.setFocus()

    def removeItem(self, name):
        """Remove item."""
        try:
            self.takeTopLevelItem(self.indexOfTopLevelItem(self.items[name]))
            self.manager.removeID(name)
            del self.items[name]
        except KeyError:
            pass

    def removeSelected(self):
        """Remove selected item."""
        indexes = self.selectedIndexes()

        if len(indexes) > 0:
            level = 0
            index = indexes[0]
            text = self.itemFromIndex(index).text(0)
            while index.parent().isValid():
                index = index.parent()
                level += 1

            if level == 0:
                self.removeItem(text)

    def editSelected(self):
        """Edit selected item."""
        indexes = self.selectedIndexes()
        name = ""
        ident = 1
        if len(indexes) > 0:
            index = indexes[0]
            name = self.itemFromIndex(index).text(0)
            ident = int(self.itemFromIndex(index).text(1))
        self.parent.addAligulacID(name, ident)

    def openMenu(self, position):
        """Open menu."""
        indexes = self.selectedIndexes()

        if len(indexes) > 0:
            level = 0
            index = indexes[0]
            text = self.itemFromIndex(index).text(0)
            ident = int(self.itemFromIndex(index).text(1))
            while index.parent().isValid():
                index = index.parent()
                level += 1

            menu = QMenu()
            if level == 0:
                act1 = QAction(_("Add Entry"))
                act1.triggered.connect(
                    lambda x:
                        self.parent.addAligulacID())
                menu.addAction(act1)
                act2 = QAction(_("Edit Entry"))
                act2.triggered.connect(
                    lambda x, text=text, ident=ident:
                        self.parent.addAligulacID(text, ident))
                menu.addAction(act2)
                act3 = QAction(_("Remove Entry"))
                act3.triggered.connect(
                    lambda x, text=text: self.removeItem(text))
                menu.addAction(act3)
                act4 = QAction(_("Open on Aligulac.com"))
                act4.triggered.connect(
                    lambda x, id=id: self.parent.controller.openURL(
                        f"http://aligulac.com/players/{ident}"))
                menu.addAction(act4)

            menu.exec_(self.viewport().mapToGlobal(position))


class AliasTreeView(QTreeWidget):
    """Tree View to edit alias names of players and teams."""

    aliasRemoved = pyqtSignal(str, str)

    def __init__(self, parent):
        """Init table list."""
        super().__init__(parent)
        self.parent = parent
        self.items = dict()
        self.header().hide()
        self.setAnimated(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.openMenu)

        self.shortcut1 = QShortcut(QKeySequence("DEL"), self)
        self.shortcut1.setAutoRepeat(False)
        self.shortcut1.setContext(Qt.WidgetWithChildrenShortcut)
        self.shortcut1.activated.connect(self.delClicked)

        self.shortcut2 = QShortcut(QKeySequence("Return"), self)
        self.shortcut2.setAutoRepeat(False)
        self.shortcut2.setContext(Qt.WidgetWithChildrenShortcut)
        self.shortcut2.activated.connect(self.enterClicked)

    def insertAliasList(self, name, aliasList):
        """Insert alias to list."""
        name = str(name).strip()
        self.items[name] = QTreeWidgetItem(self, [name])
        for alias in aliasList:
            QTreeWidgetItem(self.items[name], [str(alias).strip()])

        self.sortItems(0, Qt.AscendingOrder)

    def insertAlias(self, name, alias, expand=False):
        """Insert alias."""
        name = str(name).strip()
        if name not in self.items.keys():
            self.items[name] = QTreeWidgetItem(self, [name])

        newitem = QTreeWidgetItem(self.items[name], [str(alias).strip()])

        self.sortItems(0, Qt.AscendingOrder)
        self.items[name].setExpanded(expand)
        if expand:
            self.setCurrentItem(newitem)
            self.setFocus()

    def removeName(self, name):
        """Remove name and it's aliases from list."""
        try:
            for child in self.items[name].takeChildren():
                self.aliasRemoved.emit(name, child.text(0))
            self.takeTopLevelItem(self.indexOfTopLevelItem(self.items[name]))
            del self.items[name]
        except KeyError:
            pass

    def removeAlias(self, alias):
        """Remove alias."""
        items = self.findItems(alias, Qt.MatchExactly | Qt.MatchRecursive)
        for item in items:
            parent = item.parent()

            try:
                parent.takeChild(parent.indexOfChild(item))
                self.aliasRemoved.emit(parent.text(0), item.text(0))
                if parent.childCount() == 0:
                    self.takeTopLevelItem(self.indexOfTopLevelItem(parent))
                    del self.items[parent.text(0)]
            except AttributeError:
                pass

    def delClicked(self):
        """Handle click on delete."""
        indexes = self.selectedIndexes()

        if len(indexes) > 0:
            level = 0
            index = indexes[0]
            text = self.itemFromIndex(index).text(0)
            while index.parent().isValid():
                index = index.parent()
                level += 1

            if level == 0:
                self.removeName(text)
            elif level == 1:
                self.removeAlias(text)

    def enterClicked(self):
        """Handle click on enter."""
        indexes = self.selectedIndexes()

        if len(indexes) > 0:
            level = 0
            index = indexes[0]
            while index.parent().isValid():
                index = index.parent()
                level += 1

            if level == 0 or level == 1:
                self.parent.addAlias(
                    self,
                    _('Name'),
                    self.itemFromIndex(index).text(0))

    def openMenu(self, position):
        """Open menu."""
        indexes = self.selectedIndexes()

        if len(indexes) > 0:
            level = 0
            index = indexes[0]
            text = self.itemFromIndex(index).text(0)
            while index.parent().isValid():
                index = index.parent()
                level += 1

            menu = QMenu()
            if level == 0:
                act1 = QAction(_("Add Alias"))
                act1.triggered.connect(
                    lambda x, self=self, text=text:
                        self.parent.addAlias(self, _('Name'), text))
                menu.addAction(act1)
                act2 = QAction(_("Remove with Aliases"))
                act2.triggered.connect(
                    lambda x, text=text: self.removeName(text))
                menu.addAction(act2)
            elif level == 1:
                action = QAction(_("Remove Alias"))
                action.triggered.connect(
                    lambda x, text=text: self.removeAlias(text))
                menu.addAction(action)

            menu.exec_(self.viewport().mapToGlobal(position))


class ListTable(QTableWidget):
    """Define a custom table list."""

    dataModified = pyqtSignal()

    def __init__(self, noColumns=1, data=None):
        """Init table list."""
        super().__init__()
        if data is None:
            data = []
        data = self.__processData(data)
        self.__noColumns = noColumns

        self.setCornerButtonEnabled(False)
        self.horizontalHeader().hide()
        self.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch)
        self.verticalHeader().hide()
        self.verticalHeader().setSectionResizeMode(
            QHeaderView.ResizeToContents)
        self.setData(data)
        self.shortcut = QShortcut(QKeySequence("DEL"), self)
        self.shortcut.setAutoRepeat(False)
        self.shortcut.setContext(Qt.WidgetWithChildrenShortcut)
        self.shortcut.activated.connect(self.delClicked)

    def __handleDataChanged(self, item):
        self.setData(self.getData(), item)
        self.dataModified.emit()

    def __processData(self, data):
        seen = set()
        uniq = [x for x in data if x not in seen and not seen.add(x)]
        uniq.sort()
        return uniq

    def delClicked(self):
        """Handle click of delete button."""
        item = self.currentItem()
        if item and item.isSelected() and item.text().strip():
            item.setText("")

    def setData(self, data, item=""):
        """Set the data."""
        try:
            self.itemChanged.disconnect()
        except Exception:
            pass

        if item:
            item = item.text()

        self.setColumnCount(self.__noColumns)
        self.setRowCount(int(len(data) / self.__noColumns) + 1)
        for idx, entry in enumerate(data):
            row, column = divmod(idx, self.__noColumns)
            self.setItem(row, column, QTableWidgetItem(entry))
            if entry == item:
                self.setCurrentCell(row, column)

        row = int(len(data) / self.__noColumns)
        for col in range(len(data) % self.__noColumns, self.__noColumns):
            self.setItem(row, col, QTableWidgetItem(""))

        row = int(len(data) / self.__noColumns) + 1
        for col in range(self.__noColumns):
            self.setItem(row, col, QTableWidgetItem(""))

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


class Completer(QCompleter):
    """Define custom auto completer for multiple words."""

    def __init__(self, items_list, parent=None):
        """Init completer."""
        super().__init__(items_list, parent)

        self.setCaseSensitivity(Qt.CaseInsensitive)
        self.setCompletionMode(QCompleter.UnfilteredPopupCompletion)
        self.setFilterMode(Qt.MatchContains)
        self.setWrapAround(False)

    def pathFromIndex(self, index):
        """Add texts instead of replace."""
        path = QCompleter.pathFromIndex(self, index)

        lst = str(self.widget().text()).split(' ')

        if len(lst) > 1:
            path = '%s %s' % (' '.join(lst[:-1]), path)

        return path

    @classmethod
    def splitPath(cls, path):
        """Add operator to separate between texts."""
        path = str(path.split(' ')[-1]).lstrip(' ')
        return [path]


class QHLine(QFrame):
    """Define a vertical line."""

    def __init__(self):
        """Init frame."""
        super().__init__()
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)


class GenericProgressDialog(QProgressDialog):
    """Define a generic progress dialog used for various tasks."""

    def __init__(self, main_window, callback_job=None):
        super().__init__()
        self.callback = callback_job
        self.setWindowModality(Qt.ApplicationModal)
        self.progress = 0
        self.setWindowTitle("StarCraft Casting Tool")
        self.setLabelText(_("Processing..."))
        self.setCancelButton(None)
        self.setRange(0, 100)
        self.setValue(0)

        self.resize(QSize(int(main_window.size().width() * 0.66),
                          self.sizeHint().height()))
        relativeChange = QPoint(int(main_window.size().width() / 2),
                                int(main_window.size().height() / 3))\
            - QPoint(int(self.size().width() / 2),
                     int(self.size().height() / 3))
        self.move(main_window.pos() + relativeChange)

        self.show()
        for __ in range(10):
            QApplication.processEvents()
        self.run()

    def run(self):
        """Run the generic task."""
        try:
            self.callback(self)
        except Exception:
            module_logger.exception('message')

        self.setValue(100)
        time.sleep(0.1)


class InitialUpdater(QProgressDialog):
    """Define initial progress dialog to download data."""

    def __init__(self, version='0.0.0'):
        """Init progress dialog."""
        QProgressDialog.__init__(self)
        self.setWindowModality(Qt.ApplicationModal)
        self.progress = 0
        self.setWindowTitle("SCC-Tool")
        self.setLabelText(_("Collecting data..."))
        self.setCancelButton(None)
        self.setRange(0, 1010)
        self.setValue(50)
        self.version = version

        settings = QSettings(ClientConfig.APP_NAME, ClientConfig.COMPANY_NAME)
        self.restoreGeometry(settings.value("geometry", self.saveGeometry()))
        m_width = self.size().width()
        m_height = self.size().height()
        self.resize(QSize(self.sizeHint().width(), self.sizeHint().height()))
        relativeChange = QPoint(int(m_width / 2), int(m_height / 2))\
            - QPoint(int(self.size().width() / 2),
                     int(self.size().height() / 2))
        self.move(self.pos() + relativeChange)

        self.show()
        for __ in range(10):
            QApplication.processEvents()
        self.run()

    def run(self):
        """Run the initial process."""
        try:
            from scctool.tasks.updater import extractData
            from pyupdater.client import Client
            client = Client(ClientConfig())
            client.refresh()
            client.platform = 'win'
            client.add_progress_hook(self.setProgress)

            channel = scctool.tasks.updater.getChannel()
            lib_update = client.update_check(
                scctool.tasks.updater.VersionHandler.ASSET_NAME,
                self.version,
                channel=channel)
            if lib_update is not None:
                lib_update.download(False)
                self.setValue(500)
                self.setLabelText(_("Extracting data..."))
                extractData(lib_update, self.setCopyProgress)
                self.setLabelText(_("Done."))
                time.sleep(1)
                self.setValue(1010)
        except Exception:
            module_logger.exception("message")

    def setCopyProgress(self, value):
        """Set progress."""
        self.setValue(500 + value * 5)

    def setProgress(self, data):
        """Set the progress of the bar."""
        # TODO: What is the data structure in case of a patch?
        module_logger.info("Progress {}".format(data))
        try:
            text = _('Downloading required files:'
                     ' Total file size {}, Time remaining {}.')
            text = text.format(humanize.naturalsize(
                data['total']), data['time'])
            self.setLabelText(text)
            self.setValue(int(float(data['percent_complete']) * 5))
        except Exception:
            module_logger.exception("message")


class DragDropLogoList(QListWidget):
    """QListWidget for logos with drag and drop."""

    def __init__(self, logoManager, addIdent=lambda: None):
        """Init the list widget."""
        super().__init__()
        self.setViewMode(QListWidget.IconMode)
        self.setIconSize(QSize(75, 75))
        # self.setMaximumHeight(200)
        self.setDragEnabled(True)
        self._logoManager = logoManager
        self._iconsize = scctool.settings.logoManager.Logo._iconsize
        self._addIdent = addIdent

    def dragEnterEvent(self, e):
        """Handle drag enter event."""
        data = e.mimeData()
        if(data.hasFormat("application/x-qabstractitemmodeldatalist")
           and e.source() != self):
            e.accept()
        elif data.hasFormat("logo/ident"):
            e.accept()
        else:
            e.ignore()

    def dragMoveEvent(self, e):
        """Handle drag move event."""
        data = e.mimeData()
        if(data.hasFormat("application/x-qabstractitemmodeldatalist")
           or data.hasFormat("logo/ident")):
            e.setDropAction(Qt.CopyAction)
            e.accept()
        else:
            e.ignore()

    def dropEvent(self, e):
        """Handle drop event."""
        data = e.mimeData()
        if(data.hasFormat("application/x-qabstractitemmodeldatalist")
           and e.source() != self):
            item = e.source().currentItem()
            pixmap = item.icon().pixmap(self._iconsize)
            ident = self._logoManager.pixmap2ident(pixmap)
        elif data.hasFormat("logo/ident"):
            ident = data.text()
            pixmap = e.source().pixmap()
        else:
            return
        logo = self._logoManager.findLogo(ident)
        item = QListWidgetItem(
            QIcon(pixmap), logo.getDesc())

        if self._addIdent(ident):
            self.addItem(item)


class DragImageLabel(QLabel):
    """Draggable image label."""

    def __init__(self, parent, logo, team=0):
        """Init the drag image label."""
        super().__init__()

        self._parent = parent
        self._team = team
        self._ident = ""

        self._iconsize = logo._iconsize
        self._logomanager = logo._manager

        self.setFixedWidth(self._iconsize)
        self.setFixedHeight(self._iconsize)
        self.setAlignment(Qt.AlignCenter)

        self.setLogo(logo)
        self.setAcceptDrops(True)

    def setLogo(self, logo):
        """Set the logo."""
        self.setPixmap(logo.provideQPixmap())
        self._ident = logo.getIdent()

    def dragEnterEvent(self, e):
        """Handle drag enter event."""
        data = e.mimeData()
        if data.hasFormat("application/x-qabstractitemmodeldatalist"):
            e.accept()
        elif data.hasFormat("logo/ident") and e.source() != self:
            e.accept()
        else:
            e.ignore()

        return

    def dropEvent(self, e):
        """Handle drop event."""
        data = e.mimeData()
        if data.hasFormat("application/x-qabstractitemmodeldatalist"):
            item = e.source().currentItem()
            pixmap = item.icon().pixmap(self._iconsize)
            ident = self._logomanager.pixmap2ident(pixmap)
            logo = self._logomanager.findLogo(ident)
            if self._team == 1:
                self._logomanager.setTeam1Logo(logo)
            elif self._team == 2:
                self._logomanager.setTeam2Logo(logo)
            self.setPixmap(pixmap)
            self._ident = ident
            self._parent.refreshLastUsed()
        elif data.hasFormat("logo/ident") and e.source() != self:
            ident = data.text()
            pixmap = e.source().pixmap()
            logo = self._logomanager.findLogo(ident)
            if self._team == 1:
                self._logomanager.setTeam1Logo(logo)
            elif self._team == 2:
                self._logomanager.setTeam2Logo(logo)
            self._ident = ident
            self.setPixmap(pixmap)
            self._parent.refreshLastUsed()

    def mousePressEvent(self, event):
        """Handle mouse press event."""
        mimeData = QMimeData()
        b = bytearray()
        b.extend(self._ident.encode())
        mimeData.setData('logo/ident', b)
        mimeData.setText(self._ident)

        drag = QDrag(self)
        drag.setPixmap(self.pixmap())
        drag.setMimeData(mimeData)
        drag.setHotSpot(event.pos() - self.rect().topLeft())

        drag.exec(Qt.CopyAction | Qt.CopyAction, Qt.CopyAction)


class TextPreviewer(QTextBrowser):
    """Text and font previewer."""

    def __init__(self):
        """Init the previewer."""
        super().__init__()
        self.setReadOnly(True)
        self.setMaximumHeight(50)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setTextInteractionFlags(Qt.NoTextInteraction)

    def setFont(self, font):
        """Set font."""
        font = font.strip()
        css = dict()
        css['font-family'] = font
        css['font-size'] = '25px'
        css['height'] = '50px'
        css['width'] = '100%'
        css['text-align'] = 'center'
        css['display'] = 'table'
        style = ""
        for key, value in css.items():
            style += f"{key}: {value};"
        self.setHtml(
            f"<div style='{style}'><span style='display: table-cell;"
            f" vertical-align: middle;'>{font}</span></div>")

    def wheelEvent(self, e):
        """Ignore scrolling."""
        e.ignore()


class LedIndicator(QAbstractButton):
    """LED Indicator."""

    scaledSize = 1000.0

    def __init__(self, parent=None):
        """Init the LED."""
        QAbstractButton.__init__(self, parent)

        self.setMinimumSize(16, 16)
        self.setCheckable(True)

        # Green
        self.on_color_1 = QColor(0, 255, 0)
        self.on_color_2 = QColor(0, 192, 0)
        self.off_color_1 = QColor(0, 28, 0)
        self.off_color_2 = QColor(0, 128, 0)

    def resizeEvent(self, QResizeEvent):
        """Handle resize event."""
        self.update()

    def paintEvent(self, QPaintEvent):
        """Handle paint event."""
        realSize = min(self.width(), self.height())

        painter = QPainter(self)
        pen = QPen(Qt.black)
        pen.setWidth(1)

        painter.setRenderHint(QPainter.Antialiasing)
        painter.translate(self.width() / 2, self.height() / 2)
        painter.scale(realSize / self.scaledSize, realSize / self.scaledSize)

        gradient = QRadialGradient(
            QPointF(-500, -500), 1500, QPointF(-500, -500))
        gradient.setColorAt(0, QColor(224, 224, 224))
        gradient.setColorAt(1, QColor(28, 28, 28))
        painter.setPen(pen)
        painter.setBrush(QBrush(gradient))
        painter.drawEllipse(QPointF(0, 0), 500, 500)

        gradient = QRadialGradient(QPointF(500, 500), 1500, QPointF(500, 500))
        gradient.setColorAt(0, QColor(224, 224, 224))
        gradient.setColorAt(1, QColor(28, 28, 28))
        painter.setPen(pen)
        painter.setBrush(QBrush(gradient))
        painter.drawEllipse(QPointF(0, 0), 450, 450)

        painter.setPen(pen)
        if self.isChecked():
            gradient = QRadialGradient(
                QPointF(-500, -500), 1500, QPointF(-500, -500))
            gradient.setColorAt(0, self.on_color_1)
            gradient.setColorAt(1, self.on_color_2)
        else:
            gradient = QRadialGradient(
                QPointF(500, 500), 1500, QPointF(500, 500))
            gradient.setColorAt(0, self.off_color_1)
            gradient.setColorAt(1, self.off_color_2)

        painter.setBrush(gradient)
        painter.drawEllipse(QPointF(0, 0), 400, 400)

    @pyqtProperty(QColor)
    def onColor1(self):
        """Return Color 1."""
        return self.on_color_1

    @onColor1.setter
    def onColor1(self, color):
        """Set color 1."""
        self.on_color_1 = color

    @pyqtProperty(QColor)
    def onColor2(self):
        """Return color 2."""
        return self.on_color_2

    @onColor2.setter
    def onColor2(self, color):
        """Set color 2."""
        self.on_color_2 = color

    @pyqtProperty(QColor)
    def offColor1(self):
        """Return off color 1."""
        return self.off_color_1

    @offColor1.setter
    def offColor1(self, color):
        """Set off color 1."""
        self.off_color_1 = color

    @pyqtProperty(QColor)
    def offColor2(self):
        """Return off color 2."""
        return self.off_color_2

    @offColor2.setter
    def offColor2(self, color):
        """Set off color 2."""
        self.off_color_2 = color


class ProfileMenu(QMenu):
    """Construct profil Menu."""

    def __init__(self, parrent_widget, controller):
        """Init the menu."""

        self._parent = parrent_widget
        self._controller = controller

        super().__init__(self._parent)

        self._menu = parrent_widget.menuBar().addMenu(_('Profile'))

        action = self._menu.addAction(QIcon(scctool.settings.getResFile(
            'folder.png')), _('Open current Profile Folder'))
        action.triggered.connect(self.openFolder)

        action = self._menu.addAction(QIcon(scctool.settings.getResFile(
            'add.png')), _('New'))
        action.triggered.connect(self.newProfile)

        action = self._menu.addAction(QIcon(scctool.settings.getResFile(
            'copy.png')), _('Duplicate'))
        action.triggered.connect(self.duplicateProfile)

        action = self._menu.addAction(QIcon(scctool.settings.getResFile(
            'edit.png')), _('Rename'))
        action.triggered.connect(self.renameProfile)

        action = self._menu.addAction(QIcon(scctool.settings.getResFile(
            'delete.png')), _('Remove'))
        action.triggered.connect(self.removeProfile)

        action = self._menu.addAction(QIcon(scctool.settings.getResFile(
            'import.png')), _('Import as New'))
        action.triggered.connect(self.importProfile)

        action = self._menu.addAction(QIcon(scctool.settings.getResFile(
            'import.png')), _('Import && Overwrite'))
        action.triggered.connect(self.importProfileOverwrite)

        action = self._menu.addAction(QIcon(scctool.settings.getResFile(
            'export.png')), _('Export'))
        action.triggered.connect(self.exportProfile)

        self._menu.addSeparator()

        self._profiles = dict()

        for profile in scctool.settings.profileManager.getProfiles():
            self.addProfile(profile.get('id'), profile.get(
                'name'), profile.get('current'))

    def addProfile(self, ident, name, current):
        """Add profile to menu."""
        action = self._menu.addAction(name)
        action.triggered.connect(
            lambda x, ident=ident: self.selectProfile(ident))
        action.setCheckable(True)
        action.setChecked(current)
        self._profiles[ident] = action

    def removeProfile(self):
        """Remove profile"""
        profile = scctool.settings.profileManager.current()
        buttonReply = QMessageBox.question(
            self._parent, _("Remove Profile"),
            _("Are you sure you wish to remove profile '{}'?".format(
                profile['name'])),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No)
        if buttonReply == QMessageBox.No:
            return
        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            scctool.settings.profileManager.deleteProfile(profile['id'])
            self._parent.restart(False)
        except Exception as e:
            QMessageBox.information(self._parent, _("Remove Profile"), str(e))
        finally:
            QApplication.restoreOverrideCursor()

    def openFolder(self):
        """Open profile folder."""
        self._controller.open_file(
            scctool.settings.profileManager.profiledir())

    def newProfile(self):
        """Make a new profile."""
        name = ''
        while True:
            name, ok = QInputDialog.getText(
                self._parent, _('Add Profile'),
                _('Please enter the name of the profile') + ':',
                text=name)
            if not ok:
                return

            QApplication.setOverrideCursor(Qt.WaitCursor)
            try:
                ident = scctool.settings.profileManager.addProfile(name)
                self.addProfile(ident, name, False)
                self.selectProfile(ident)
            except Exception as e:
                QMessageBox.information(self._parent, _(
                    "Please enter a valid name"), str(e))
                module_logger.exception("message")
                continue
            finally:
                QApplication.restoreOverrideCursor()
            return

    def duplicateProfile(self):
        """Duplicate the current profile."""
        current = scctool.settings.profileManager.current()
        name = current['name'] + ' 2'
        while True:
            name, ok = QInputDialog.getText(
                self._parent, _('Duplicate Profile'),
                _('Please enter the name of the new profile') + ':',
                text=name)
            if not ok:
                return
            QApplication.setOverrideCursor(Qt.WaitCursor)
            try:
                self._controller.saveAll()
                ident = scctool.settings.profileManager.addProfile(
                    name, copy=current['id'])
                self.addProfile(ident, name, False)
                self.selectProfile(ident)
            except Exception as e:
                QMessageBox.information(self._parent, _(
                    "Please enter a valid name"), str(e))
                module_logger.exception("message")
                continue
            finally:
                QApplication.restoreOverrideCursor()
            return

    def exportProfile(self):
        """Export the current profile."""
        current = scctool.settings.profileManager.current()
        filename = os.path.join(
            scctool.settings.profileManager.basedir(),
            'scct-profile-{}-{}.zip'.format(current['name'],
                                            time.strftime("%Y%m%d"))
        )
        filename, ok = QFileDialog.getSaveFileName(
            self._parent, 'Export Profile',
            filename, _("ZIP archive") + " (*.zip)")
        if not ok:
            return

        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            self._controller.saveAll()
            scctool.settings.profileManager.exportProfile(
                current['id'], filename)
        except Exception as e:
            QMessageBox.critical(self._parent, _("Error"), str(e))
            module_logger.exception("message")
        finally:
            QApplication.restoreOverrideCursor()

    def importProfile(self):
        """Import a profile from zip archive and save it as new."""
        filename, ok = QFileDialog.getOpenFileName(
            self._parent,
            'Import Profile',
            scctool.settings.profileManager.basedir(),
            _("ZIP archive") + " (*.zip)")
        if not ok:
            return
        name = ""
        while True:
            name, ok = QInputDialog.getText(
                self._parent,
                _('Import Profile'),
                _('Please enter the name of the imported profile') + ':',
                text=name)
            if not ok:
                return
            QApplication.setOverrideCursor(Qt.WaitCursor)
            try:
                ident = scctool.settings.profileManager.importProfile(
                    filename, name)
                self.addProfile(ident, name, False)
                self.selectProfile(ident)
            except Exception as e:
                QMessageBox.information(self._parent, _(
                    "Please enter a valid name"), str(e))
                module_logger.exception("message")
                continue
            finally:
                QApplication.restoreOverrideCursor()
            return

    def importProfileOverwrite(self):
        """Import a profile from zip and overwrite the current profile."""
        filename, ok = QFileDialog.getOpenFileName(
            self._parent,
            'Import Profile',
            scctool.settings.profileManager.basedir(),
            _("ZIP archive") + " (*.zip)")
        if not ok:
            return
        profile = scctool.settings.profileManager.current()
        ident = profile['id']
        name = profile['name']
        buttonReply = QMessageBox.question(
            self._parent, _("Overwrite Profile"),
            _("Are you sure you wish to overwrite"
              " the current profile '{}'?".format(
                  name)),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No)
        if buttonReply == QMessageBox.No:
            return

        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            scctool.settings.profileManager.deleteProfile(ident, True)
            ident = scctool.settings.profileManager.importProfile(
                filename, name, ident)
            self.addProfile(ident, name, False)
            self.selectProfile(ident, False)
        except Exception as e:
            QMessageBox.information(self._parent, _(
                "Import & Overwrite Profile"), str(e))
            module_logger.exception('importProfileOverwrite')
        finally:
            QApplication.restoreOverrideCursor()

    def selectProfile(self, myid, save=True):
        """Select a profle."""
        for ident, action in self._profiles.items():
            if ident == myid:
                action.setChecked(True)
            else:
                action.setChecked(False)
        scctool.settings.profileManager.setDefault(myid)
        # scctool.settings.profileManager.setCurrent(myid)
        self._parent.restart(save)

    def renameProfile(self):
        """Rename a profile."""
        profile = scctool.settings.profileManager.current()
        name = profile.get('name', '')
        while True:
            name, ok = QInputDialog.getText(
                self._parent, _('Rename Profile'),
                _('Please enter the name of the profile') + ':',
                text=name)
            if not ok:
                return
            QApplication.setOverrideCursor(Qt.WaitCursor)
            try:
                scctool.settings.profileManager.renameProfile(
                    profile['id'], name)
                self._profiles[profile['id']].setText(name)
            except Exception as e:
                QMessageBox.information(self._parent, _(
                    "Please enter a valid name"), str(e))
                module_logger.exception("message")
                continue
            finally:
                QApplication.restoreOverrideCursor()
            return


class MatchComboBox(QComboBox):
    """Define QComboBox for the match url."""

    returnPressed = pyqtSignal()

    def __init__(self, parent=None):
        """Init the combobox."""
        super().__init__(parent)
        self.setEditable(True)
        self.lineEdit().setAlignment(Qt.AlignCenter)
        tooltip = _('Enter AlphaTL/RSL Match-URL or '
                    'search for an upcoming AlphaTL Match.')
        self.lineEdit().setPlaceholderText(tooltip)
        self.lineEdit().setToolTip(tooltip)
        self._alpha_icon = QIcon(scctool.settings.getResFile('alpha.png'))
        self._rstl_icon = QIcon(scctool.settings.getResFile('rstl.png'))
        self._rsl_icon = QIcon(scctool.settings.getResFile('rsl.png'))
        self._ctl_icon = QIcon(scctool.settings.getResFile('chobo.png'))
        self.addItem(self._alpha_icon, 'https://alpha.tl/match/3000')
        self.setItemData(0, Qt.AlignCenter, Qt.TextAlignmentRole)
        self.insertSeparator(1)
        self.lineEdit().returnPressed.connect(self.returnPressed.emit)
        self.activated.connect(self._handleActivated)

    def setText(self, text):
        """Set the text."""
        self.setURL(text)

    def _handleActivated(self, idx):
        data = self.itemData(idx)
        if not data:
            data = self.itemText(idx)
        self.setURL(data)

    def _handleCompleterActivated(self, text):
        if text in self._matches:
            data = self._matches[text]
        else:
            data = text
        self.setURL(data)

    def updateItems(self, matches):
        """Update the items."""
        # completer = QCompleter(
        #         ["https://alpha.tl/match/",
        #          "http://hdgame.net/en/tournaments/list/tournament/rstl-13/"],
        # self.le_url)
        self.removeItems()
        self._matches = matches
        completer = QCompleter(
            self._matches.keys(),
            self.lineEdit())
        completer.setFilterMode(Qt.MatchContains)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        completer.setCompletionMode(
            QCompleter.PopupCompletion)
        completer.setWrapAround(True)
        completer.activated.connect(self._handleCompleterActivated)
        self.setCompleter(completer)

        for text, url in self._matches.items():
            self.addItem(self._alpha_icon, text, url)

    def removeItems(self):
        """Remove all items."""
        for __ in range(2, self.count()):
            self.removeItem(2)

    def setURL(self, url):
        """Set a new URL."""
        lower_url = str(url).lower()
        if(lower_url.find('alpha') != -1):
            self.setItemIcon(0, self._alpha_icon)
        elif(lower_url.find('rfcs') != -1):
            self.setItemIcon(0, self._rsl_icon)
        elif(lower_url.find('hdgame') != -1):
            self.setItemIcon(0, self._rstl_icon)
        elif(lower_url.find('choboteamleague') != -1):
            self.setItemIcon(0, self._ctl_icon)
        else:
            self.setItemIcon(0, QIcon())
        self.setItemText(0, url)
        self.setCurrentIndex(0)

    def text(self):
        """Return it's text."""
        return self.lineEdit().text()

    def selectAll(self):
        self.lineEdit().selectAll()


class ScopeGroupBox(QGroupBox):
    """Define QGroupBox for icon scope."""

    dataModified = pyqtSignal()

    def __init__(self, name='', options=None, ident='', controller=None, parent=None):
        """Init lineedit."""
        super().__init__(name, parent)
        if options is None:
            options = list()
        layout = QFormLayout()
        self.controller = controller
        scope = scctool.settings.config.parser.get("MapIcons", f"scope_{ident}")
        self.bt_dynamic = QRadioButton(_("Dynamic:"))
        self.bt_dynamic.toggled.connect(lambda: self.btnstate('dynamic'))
        self.bt_dynamic.setMinimumWidth(120)
        self.scope_box = QComboBox()
        self.path = f"mapicons_{ident}"
        self.ident = ident
        found = False
        idx = 0
        for key, item in options.items():
            self.scope_box.addItem(item, key)
            if key == scope:
                self.scope_box.setCurrentIndex(idx)
                self.bt_dynamic.setChecked(True)
                found = True
            idx = idx + 1
        layout.addRow(self.bt_dynamic, self.scope_box)

        self.bt_static = QRadioButton(_("Static:"))
        self.bt_static.toggled.connect(lambda: self.btnstate('static'))
        self.bt_static.setMinimumWidth(120)

        container = QHBoxLayout()
        self.label1 = QLabel(_('From'))
        container.addWidget(self.label1)
        self.cb_lower = QComboBox()
        for set_idx in range(0, scctool.settings.max_no_sets):
            self.cb_lower.addItem(_('Map {}').format(set_idx + 1), set_idx)
        self.cb_lower.currentIndexChanged.connect(self.adjustRangeUpper)
        container.addWidget(self.cb_lower, 0)
        self.label2 = QLabel(_('to'))
        self.label2.setAlignment(Qt.AlignCenter)
        container.addWidget(self.label2, 0)
        self.cb_upper = QComboBox()
        for set_idx in range(0, scctool.settings.max_no_sets):
            self.cb_upper.addItem(_('Map {}').format(set_idx + 1), set_idx)
        container.addWidget(self.cb_upper, 0)
        layout.addRow(self.bt_static, container)

        if not found:
            m = re.match(r'^(\d+)-(\d+)$', scope)
            if m and int(m.group(1)) <= int(m.group(2)):
                self.bt_static.setChecked(True)
                self.cb_upper.setCurrentIndex(int(m.group(2)) - 1)
                self.cb_lower.setCurrentIndex(int(m.group(1)) - 1)

        self.cb_separate_style = QCheckBox(_('Activate Separate Style:'))
        primary = ident.split('_')[0]
        self.qb_boxStyle = StyleComboBox(
            f"{scctool.settings.casting_html_dir}/src/css/mapicons_{primary}",
            self.path)
        active = scctool.settings.config.parser.getboolean(
                "MapIcons", f"separate_style_{ident}")
        self.cb_separate_style.setChecked(active)
        self.qb_boxStyle.setEnabled(active)
        self.cb_separate_style.toggled.connect(self.toggleStyleComboBox)
        self.qb_boxStyle.connect2WS(self.controller, self.path)
        layout.addRow(self.cb_separate_style, self.qb_boxStyle)

        self.setLayout(layout)

        self.btnstate('dynamic')
        self.btnstate('static')

        self.bt_dynamic.toggled.connect(self.triggerSignal)
        self.bt_static.toggled.connect(self.triggerSignal)
        self.cb_upper.currentIndexChanged.connect(self.triggerSignal)
        self.cb_lower.currentIndexChanged.connect(self.triggerSignal)
        self.scope_box.currentIndexChanged.connect(self.triggerSignal)

    def btnstate(self, b):
        """Update button states."""
        if b == 'dynamic':
            self.scope_box.setEnabled(self.bt_dynamic.isChecked())
        elif b == 'static':
            self.cb_lower.setEnabled(self.bt_static.isChecked())
            self.cb_upper.setEnabled(self.bt_static.isChecked())
            self.label1.setEnabled(self.bt_static.isChecked())
            self.label2.setEnabled(self.bt_static.isChecked())

    def toggleStyleComboBox(self, state):
        """Toggle style box."""
        self.qb_boxStyle.setEnabled(state)
        scctool.settings.config.parser.set(
            "MapIcons", f"separate_style_{self.ident}",
            str(state))
        self.controller.websocketThread.changeStyle(self.path)

    def adjustRangeUpper(self, lower):
        """Adjust the range for the scopes."""
        current_idx = self.cb_upper.itemData(self.cb_upper.currentIndex())
        self.cb_upper.clear()
        rg = range(lower, scctool.settings.max_no_sets)
        if current_idx not in rg:
            current_idx = lower
        idx = 0
        for set_idx in rg:
            self.cb_upper.addItem(_('Map {}').format(set_idx + 1), set_idx)
            if set_idx == current_idx:
                self.cb_upper.setCurrentIndex(idx)
            idx = idx + 1

    def getScope(self):
        """Get the scope."""
        if self.bt_dynamic.isChecked():
            return self.scope_box.itemData(self.scope_box.currentIndex())
        else:
            lower = int(self.cb_lower.itemData(
                self.cb_lower.currentIndex())) + 1
            upper = int(self.cb_upper.itemData(
                self.cb_upper.currentIndex())) + 1
            return f'{lower}-{upper}'

    def triggerSignal(self):
        """Emit a signal."""
        self.dataModified.emit()
