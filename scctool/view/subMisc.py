"""Show subwindow with miscellaneous settings."""
import logging
import PyQt5

import os.path
import humanize  # pip install humanize

from scctool.view.widgets import MonitoredLineEdit, ListTable
import scctool.settings


# create logger
module_logger = logging.getLogger('scctool.view.subMisc')


class SubwindowMisc(PyQt5.QtWidgets.QWidget):
    """Show subwindow with miscellaneous settings."""

    def createWindow(self, mainWindow):
        """Create subwindow with miscellaneous settings."""
        try:
            parent = None
            super(SubwindowMisc, self).__init__(parent)
            # self.setWindowFlags(PyQt5.QtCore.Qt.WindowStaysOnTopHint)

            self.setWindowIcon(
                PyQt5.QtGui.QIcon(scctool.settings.getAbsPath('src/settings.png')))
            self.setWindowModality(PyQt5.QtCore.Qt.ApplicationModal)
            self.mainWindow = mainWindow
            self.passEvent = False
            self.controller = mainWindow.controller
            self.__dataChanged = False

            self.createButtonGroup()
            self.createTabs()

            mainLayout = PyQt5.QtWidgets.QVBoxLayout()

            mainLayout.addWidget(self.tabs)
            mainLayout.addLayout(self.buttonGroup)

            self.setLayout(mainLayout)

            self.resize(PyQt5.QtCore.QSize(mainWindow.size().width()
                                           * .80, self.sizeHint().height()))
            relativeChange = PyQt5.QtCore.QPoint(mainWindow.size().width() / 2,
                                                 mainWindow.size().height() / 3)\
                - PyQt5.QtCore.QPoint(self.size().width() / 2,
                                      self.size().height() / 3)
            self.move(mainWindow.pos() + relativeChange)

            self.setWindowTitle("Miscellaneous Settings")

        except Exception as e:
            module_logger.exception("message")

    def createTabs(self):
        """Create tabs."""
        self.tabs = PyQt5.QtWidgets.QTabWidget()

        self.createFavBox()
        self.createMapsBox()
        self.createOcrBox()

        # Add tabs
        self.tabs.addTab(self.mapsBox, "Map Manager")
        self.tabs.addTab(self.favBox, "Favorites")
        self.tabs.addTab(self.ocrBox, "OCR")

    def changed(self):
        """Handle changes."""
        self.__dataChanged = True

    def createFavBox(self):
        """Create favorites box."""
        self.favBox = PyQt5.QtWidgets.QWidget()
        mainLayout = PyQt5.QtWidgets.QVBoxLayout()

        box = PyQt5.QtWidgets.QGroupBox("Players")
        layout = PyQt5.QtWidgets.QHBoxLayout()

        self.list_favPlayers = ListTable(
            4, scctool.settings.config.getMyPlayers())
        self.list_favPlayers.dataModified.connect(self.changed)
        self.list_favPlayers.setFixedHeight(150)
        layout.addWidget(self.list_favPlayers)
        box.setLayout(layout)

        mainLayout.addWidget(box)

        box = PyQt5.QtWidgets.QGroupBox("Teams")
        layout = PyQt5.QtWidgets.QHBoxLayout()

        self.list_favTeams = ListTable(3, scctool.settings.config.getMyTeams())
        self.list_favTeams.dataModified.connect(self.changed)
        self.list_favTeams.setFixedHeight(100)
        layout.addWidget(self.list_favTeams)

        box.setLayout(layout)
        mainLayout.addWidget(box)

        mainLayout.addItem(PyQt5.QtWidgets.QSpacerItem(
            0, 0, PyQt5.QtWidgets.QSizePolicy.Minimum, PyQt5.QtWidgets.QSizePolicy.Expanding))

        self.favBox.setLayout(mainLayout)

    def createOcrBox(self):
        """Create forms for OCR."""
        self.ocrBox = PyQt5.QtWidgets.QWidget()

        mainLayout = PyQt5.QtWidgets.QVBoxLayout()

        box = PyQt5.QtWidgets.QGroupBox(
            "Optical Character Recognition for Automatic Setting of Ingame Score")

        layout = PyQt5.QtWidgets.QGridLayout()

        self.cb_useocr = PyQt5.QtWidgets.QCheckBox(
            " Activate Optical Character Recognition")
        self.cb_useocr.setChecked(
            scctool.settings.config.parser.getboolean("SCT", "use_ocr"))
        self.cb_useocr.stateChanged.connect(self.changed)

        self.tesseract = MonitoredLineEdit()
        self.tesseract.setText(
            scctool.settings.config.parser.get("SCT", "tesseract"))
        self.tesseract.textModified.connect(self.changed)
        # self.tesseract.setAlignment(PyQt5.QtCore.Qt.AlignCenter)
        self.tesseract.setPlaceholderText(
            "C:\\Program Files (x86)\\Tesseract-OCR\\tesseract")
        self.tesseract.setReadOnly(True)
        self.tesseract.setToolTip('Tesseract-OCR Executeable')

        self.browse = PyQt5.QtWidgets.QPushButton("Browse...")
        self.browse.clicked.connect(self.selectTesseract)

        text = "Sometimes the order of players given by the SC2-Client-API differs" +\
            " from the order in the Observer-UI resulting in a swaped match score." +\
            " To correct this via Optical Character Recognition you have to download" +\
            " {} and install and select the exectuable below, if it is not detected" +\
            " automatically."""
        url = 'https://github.com/UB-Mannheim/tesseract/wiki#tesseract-at-ub-mannheim'
        url = "<a href='{}'>Tesseract-OCR</a>".format(url)

        label = PyQt5.QtWidgets.QLabel(text.format(url))
        label.setAlignment(PyQt5.QtCore.Qt.AlignJustify)
        label.setOpenExternalLinks(True)
        label.setWordWrap(True)
        label.setMargin(5)
        layout.addWidget(label, 1, 0, 1, 2)

        layout.addWidget(self.cb_useocr, 0, 0, 1, 2)
        layout.addWidget(PyQt5.QtWidgets.QLabel(
            "Tesseract-OCR Executeable:"), 2, 0)
        layout.addWidget(self.tesseract, 3, 0)
        layout.addWidget(self.browse, 3, 1)

        box.setLayout(layout)
        mainLayout.addWidget(box)
        mainLayout.addItem(PyQt5.QtWidgets.QSpacerItem(
            0, 0, PyQt5.QtWidgets.QSizePolicy.Minimum, PyQt5.QtWidgets.QSizePolicy.Expanding))
        self.ocrBox.setLayout(mainLayout)

        if(not scctool.settings.windows):
            self.cb_useocr.setEnabled(False)
            self.cb_useocr.setAttribute(PyQt5.QtCore.Qt.WA_AlwaysShowToolTips)
            self.cb_useocr.setToolTip(
                "This feature is only available in Windows.")
            self.tesseract.setEnabled(False)
            self.tesseract.setAttribute(PyQt5.QtCore.Qt.WA_AlwaysShowToolTips)
            self.tesseract.setToolTip(
                "This feature is only available in Windows.")
            self.browse.setEnabled(False)
            self.browse.setAttribute(PyQt5.QtCore.Qt.WA_AlwaysShowToolTips)
            self.browse.setToolTip(
                "This feature is only available in Windows.")

    def selectTesseract(self):
        """Create forms for tesseract."""
        old_exe = self.tesseract.text()
        default = scctool.settings.config.findTesserAct(old_exe)
        exe, ok = PyQt5.QtWidgets.QFileDialog.getOpenFileName(
            self, "Select Tesseract-OCR Executeable", default,
            "Tesseract-OCR Executeable (tesseract.exe);; Exectuable (*.exe);; All files (*)")
        if(ok and exe != old_exe):
            self.tesseract.setText(exe)
            self.changed()

    def createMapsBox(self):
        """Create box for map manager."""
        self.mapsize = 300

        self.mapsBox = PyQt5.QtWidgets.QWidget()

        layout = PyQt5.QtWidgets.QGridLayout()

        self.maplist = PyQt5.QtWidgets.QListWidget()
        self.maplist.setSortingEnabled(True)
        for map in scctool.settings.maps:
            self.maplist.addItem(PyQt5.QtWidgets.QListWidgetItem(map))
        self.maplist.setCurrentItem(self.maplist.item(0))
        self.maplist.currentItemChanged.connect(self.changePreview)
        # self.maplist.setFixedHeight(self.mapsize)
        self.maplist.setMinimumWidth(150)

        layout.addWidget(self.maplist, 0, 1, 2, 1)
        self.mapPreview = PyQt5.QtWidgets.QLabel()
        self.mapPreview.setFixedWidth(self.mapsize)
        self.mapPreview.setFixedHeight(self.mapsize)
        self.mapPreview.setAlignment(PyQt5.QtCore.Qt.AlignCenter)
        layout.addWidget(self.mapPreview, 0, 0)
        self.mapInfo = PyQt5.QtWidgets.QLabel()
        layout.addWidget(self.mapInfo, 1, 0)

        self.pb_addMap = PyQt5.QtWidgets.QPushButton("Add")
        self.pb_addMap.clicked.connect(self.addMap)
        self.pb_renameMap = PyQt5.QtWidgets.QPushButton("Rename")
        self.pb_renameMap.clicked.connect(self.renameMap)
        self.pb_changeMap = PyQt5.QtWidgets.QPushButton("Change Image")
        self.pb_changeMap.clicked.connect(self.changeMap)
        self.pb_removeMap = PyQt5.QtWidgets.QPushButton("Remove")
        self.pb_removeMap.clicked.connect(self.deleteMap)

        box = PyQt5.QtWidgets.QWidget()
        container = PyQt5.QtWidgets.QHBoxLayout()
        container.addWidget(PyQt5.QtWidgets.QLabel(), 4)
        container.addWidget(self.pb_renameMap, 0)
        container.addWidget(self.pb_changeMap, 0)
        label = PyQt5.QtWidgets.QLabel()
        label.setFixedWidth(10)
        container.addWidget(PyQt5.QtWidgets.QLabel(), 0)
        container.addWidget(self.pb_addMap, 0)
        container.addWidget(self.pb_removeMap, 0)
        box.setLayout(container)

        layout.addWidget(box, 2, 0, 1, 2)

        layout.addItem(PyQt5.QtWidgets.QSpacerItem(0, 0, PyQt5.QtWidgets.QSizePolicy.Minimum,
                                                   PyQt5.QtWidgets.QSizePolicy.Expanding),
                       3, 0, 1, 2)

        self.changePreview()
        self.mapsBox.setLayout(layout)

    def renameMap(self):
        """Rename maps."""
        item = self.maplist.currentItem()
        map = item.text()
        text, ok = PyQt5.QtWidgets.QInputDialog.getText(
            self, 'Map Name', 'Map Name:', text=map)
        if not ok:
            return
        text = text.strip()
        if(text == map):
            return
        if(text in scctool.settings.maps):
            buttonReply = PyQt5.QtWidgets.QMessageBox.warning(
                self, "Duplicate Entry", "Map is already in list! Overwrite?",
                PyQt5.QtWidgets.QMessageBox.Yes | PyQt5.QtWidgets.QMessageBox.No,
                PyQt5.QtWidgets.QMessageBox.No)
            if buttonReply == PyQt5.QtWidgets.QMessageBox.No:
                return

        self.controller.addMap(self.controller.getMapImg(map, True), text)
        self.controller.deleteMap(map)
        item.setText(text)

    def changeMap(self):
        """Change a map."""
        map = self.maplist.currentItem().text()
        fileName, ok = PyQt5.QtWidgets.QFileDialog.getOpenFileName(
            self, "Select Map Image (> 500x500px recommended)",
            "", "Support Images (*.png *.jpg)")
        if ok:
            base = os.path.basename(fileName)
            name, ext = os.path.splitext(base)
            name = name.replace("_", " ")
            self.controller.addMap(fileName, map)
            self.changePreview()

    def addMap(self):
        """Add a map."""
        fileName, ok = PyQt5.QtWidgets.QFileDialog.getOpenFileName(
            self, "Select Map Image (> 500x500px recommended)",
            "", "Support Images (*.png *.jpg)")
        if ok:
            base = os.path.basename(fileName)
            name, ext = os.path.splitext(base)
            name = name.replace("_", " ")
            text, ok = PyQt5.QtWidgets.QInputDialog.getText(
                self, 'Map Name', 'Map Name:', text=name)
            if ok:
                if(text.strip() in scctool.settings.maps):
                    buttonReply = PyQt5.QtWidgets.QMessageBox.warning(
                        self, "Duplicate Entry", "Map is already in list! Overwrite?",
                        PyQt5.QtWidgets.QMessageBox.Yes | PyQt5.QtWidgets.QMessageBox.No,
                        PyQt5.QtWidgets.QMessageBox.No)
                    if buttonReply == PyQt5.QtWidgets.QMessageBox.No:
                        return

                self.controller.addMap(fileName, text)
                item = PyQt5.QtWidgets.QListWidgetItem(text)
                self.maplist.addItem(item)
                self.maplist.setCurrentItem(item)

    def deleteMap(self):
        """Delete a map."""
        item = self.maplist.currentItem()
        map = item.text()
        buttonReply = PyQt5.QtWidgets.QMessageBox.question(
            self, 'Delete map?',
            "Delete '{}' permanently?".format(map),
            PyQt5.QtWidgets.QMessageBox.Yes | PyQt5.QtWidgets.QMessageBox.No,
            PyQt5.QtWidgets.QMessageBox.No)
        if buttonReply == PyQt5.QtWidgets.QMessageBox.Yes:
            self.controller.deleteMap(map)
            self.maplist.takeItem(self.maplist.currentRow())

    def changePreview(self):
        """Change the map preview."""
        map = self.maplist.currentItem().text()
        if(map == "TBD"):
            self.pb_renameMap.setEnabled(False)
            self.pb_removeMap.setEnabled(False)
        else:
            self.pb_removeMap.setEnabled(True)
            self.pb_renameMap.setEnabled(True)

        file = self.controller.getMapImg(map, True)
        map = PyQt5.QtGui.QPixmap(file)
        width = map.height()
        height = map.width()
        ext = os.path.splitext(file)[1].replace(".", "").upper()
        size = humanize.naturalsize(os.path.getsize(file))
        map = PyQt5.QtGui.QPixmap(file).scaled(
            self.mapsize, self.mapsize, PyQt5.QtCore.Qt.KeepAspectRatio)
        self.mapPreview.setPixmap(map)
        text = "{}x{}px, {}, {}".format(width, height, str(size), ext)
        self.mapInfo.setText(text)

    def createButtonGroup(self):
        """Create buttons."""
        try:
            layout = PyQt5.QtWidgets.QHBoxLayout()

            layout.addWidget(PyQt5.QtWidgets.QLabel(""))

            buttonCancel = PyQt5.QtWidgets.QPushButton('Cancel')
            buttonCancel.clicked.connect(self.closeWindow)
            layout.addWidget(buttonCancel)

            buttonSave = PyQt5.QtWidgets.QPushButton('Save && Close')
            buttonSave.clicked.connect(self.saveCloseWindow)
            layout.addWidget(buttonSave)

            self.buttonGroup = layout
        except Exception as e:
            module_logger.exception("message")

    def saveData(self):
        """Save the data."""
        if(self.__dataChanged):
            scctool.settings.config.parser.set(
                "SCT", "myteams", ", ".join(self.list_favTeams.getData()))
            scctool.settings.config.parser.set(
                "SCT", "commonplayers", ", ".join(self.list_favPlayers.getData()))
            scctool.settings.config.parser.set(
                "SCT", "tesseract", self.tesseract.text().strip())
            scctool.settings.config.parser.set(
                "SCT", "use_ocr", str(self.cb_useocr.isChecked()))

    def saveCloseWindow(self):
        """Save and close window."""
        self.saveData()
        self.passEvent = True
        self.close()

    def closeWindow(self):
        """Close window."""
        self.passEvent = True
        self.close()

    def closeEvent(self, event):
        """Handle close event."""
        try:
            self.mainWindow.updateMapCompleters()
            if(not self.__dataChanged):
                event.accept()
                return
            if(not self.passEvent):
                if(self.isMinimized()):
                    self.showNormal()
                buttonReply = PyQt5.QtWidgets.QMessageBox.question(
                    self, 'Save data?', "Save data?",
                    PyQt5.QtWidgets.QMessageBox.Yes | PyQt5.QtWidgets.QMessageBox.No,
                    PyQt5.QtWidgets.QMessageBox.No)
                if buttonReply == PyQt5.QtWidgets.QMessageBox.Yes:
                    self.saveData()
            event.accept()
        except Exception as e:
            module_logger.exception("message")
