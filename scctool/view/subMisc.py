#!/usr/bin/env python
import logging

# create logger
module_logger = logging.getLogger('scctool.view.subMisc')

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from scctool.view.widgets import *

import scctool.settings

class subwindowMisc(QWidget):
    def createWindow(self, mainWindow):

        try:
            parent = None
            super(subwindowMisc, self).__init__(parent)
            # self.setWindowFlags(Qt.WindowStaysOnTopHint)

            self.setWindowIcon(QIcon('src/settings.png'))
            self.mainWindow = mainWindow
            self.passEvent = False
            self.controller = mainWindow.controller
            self.__dataChanged = False

            self.createButtonGroup()
            self.createFavBox()
            self.createMapsBox()
            self.createOcrBox()

            mainLayout = QVBoxLayout()

            mainLayout.addWidget(self.mapsBox)
            mainLayout.addLayout(self.favBox)
            mainLayout.addWidget(self.ocrBox)
            mainLayout.addLayout(self.buttonGroup)

            self.setLayout(mainLayout)

            self.resize(QSize(mainWindow.size().width()
                              * .80, self.sizeHint().height()))
            self.move(mainWindow.pos() + QPoint(mainWindow.size().width() / 2, mainWindow.size().height() / 3)
                      - QPoint(self.size().width() / 2, self.size().height() / 3))

            self.setWindowTitle("Miscellaneous Settings")

        except Exception as e:
            module_logger.exception("message")

    def changed(self):
        self.__dataChanged = True

    def createFavBox(self):

        self.favBox = QVBoxLayout()

        box = QGroupBox("Favorites Players")
        layout = QHBoxLayout()

        self.list_favPlayers = ListTable(4, scctool.settings.config.getMyPlayers())
        self.list_favPlayers.dataModified.connect(self.changed)
        self.list_favPlayers.setFixedHeight(100)
        layout.addWidget(self.list_favPlayers)
        box.setLayout(layout)

        self.favBox.addWidget(box)

        box = QGroupBox("Favorites Teams")
        layout = QHBoxLayout()

        self.list_favTeams = ListTable(3, scctool.settings.config.getMyTeams())
        self.list_favTeams.dataModified.connect(self.changed)
        self.list_favTeams.setFixedHeight(50)

        layout.addWidget(self.list_favTeams)
        box.setLayout(layout)
        self.favBox.addWidget(box)

    def createOcrBox(self):

        self.ocrBox = QGroupBox(
            "Optical Character Recognition for Setting Ingame Score")

        layout = QGridLayout()

        self.cb_useocr = QCheckBox(
            " Activate Optical Character Recognition for Automatic Setting of Ingame Score")
        self.cb_useocr.setChecked(
            scctool.settings.config.parser.getboolean("SCT", "use_ocr"))
        self.cb_useocr.stateChanged.connect(self.changed)

        self.tesseract = MonitoredLineEdit()
        self.tesseract.setText(scctool.settings.config.parser.get("SCT", "tesseract"))
        self.tesseract.textModified.connect(self.changed)
        self.tesseract.setAlignment(Qt.AlignCenter)
        self.tesseract.setPlaceholderText(
            "C:\\Program Files (x86)\\Tesseract-OCR\\tesseract")
        self.tesseract.setReadOnly(True)
        self.tesseract.setToolTip('Tesseract-OCR Executeable')

        button = QPushButton("Select Folder")
        button.clicked.connect(self.selectTesseract)

        text = """Sometimes the order of players given by the SC2-Client-API differs from the order in the Observer-UI resulting in a swaped match score. To correct this via Optical Character Recognition you have to download and install <a href='https://github.com/UB-Mannheim/tesseract/wiki#tesseract-at-ub-mannheim'>Tesseract-OCR</a> and select the exectuable (tesseract.exe) here:"""

        label = QLabel(text)
        label.setOpenExternalLinks(True)
        label.setWordWrap(True)
        label.setMargin(5)
        layout.addWidget(label, 1, 0, 1, 3)

        layout.addWidget(self.cb_useocr, 0, 0, 1, 3)
        layout.addWidget(QLabel("Tesseract-OCR Folder:"), 2, 0)
        layout.addWidget(self.tesseract, 2, 1)
        layout.addWidget(button, 2, 2)

        self.ocrBox.setLayout(layout)

    def selectTesseract(self):
        old_exe = self.tesseract.text()
        default = scctool.settings.config.findTesserAct(old_exe)
        exe, ok = QFileDialog.getOpenFileName(self, "Select Tesseract-OCR Executeable", default,
            "Tesseract-OCR Executeable (tesseract.exe);; Exectuable (*.exe);; All files (*)")
        if(ok and exe != old_exe):
            self.tesseract.setText(exe)
            self.changed()

    def createMapsBox(self):

        self.mapsize = 150

        self.mapsBox = QGroupBox("Map Manager")

        layout = QGridLayout()

        self.maplist = QListWidget()
        self.maplist.setSortingEnabled(True)
        for map in scctool.settings.maps:
            self.maplist.addItem(QListWidgetItem(map))
        self.maplist.setCurrentItem(self.maplist.item(0))
        self.maplist.currentItemChanged.connect(self.changePreview)
        self.maplist.setFixedHeight(self.mapsize)
        self.maplist.setMinimumWidth(150)

        layout.addWidget(self.maplist, 0, 1, 7, 1)
        self.mapPreview = QLabel()
        self.mapPreview.setFixedWidth(self.mapsize)
        self.mapPreview.setFixedHeight(self.mapsize)
        self.mapPreview.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.mapPreview, 0, 0, 7, 1)

        self.pb_addMap = QPushButton("Add")
        self.pb_addMap.clicked.connect(self.addMap)
        self.pb_renameMap = QPushButton("Rename")
        self.pb_renameMap.clicked.connect(self.renameMap)
        self.pb_changeMap = QPushButton("Change Image")
        self.pb_changeMap.clicked.connect(self.changeMap)
        self.pb_removeMap = QPushButton("Remove")
        self.pb_removeMap.clicked.connect(self.deleteMap)

        layout.addWidget(QLabel(), 0, 2)
        layout.addWidget(self.pb_addMap, 1, 2)
        layout.addWidget(self.pb_removeMap, 2, 2)
        layout.addWidget(QLabel(), 3, 2)
        layout.addWidget(self.pb_renameMap, 4, 2)
        layout.addWidget(self.pb_changeMap, 5, 2)
        layout.addWidget(QLabel(), 6, 2)

        self.changePreview()
        self.mapsBox.setLayout(layout)

    def renameMap(self):
        item = self.maplist.currentItem()
        map = item.text()
        text, ok = QInputDialog.getText(
            self, 'Map Name', 'Map Name:', text=map)
        if not ok:
            return
        text = text.strip()
        if(text == map):
            return
        if(text in scctool.settings.maps):
            buttonReply = QMessageBox.warning(self, "Duplicate Entry", "Map is already in list! Overwrite?",
                                              QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if buttonReply == QMessageBox.No:
                return

        self.controller.addMap(self.controller.getMapImg(map, True), text)
        self.controller.deleteMap(map)
        item.setText(text)

    def changeMap(self):
        map = self.maplist.currentItem().text()
        fileName, ok = QFileDialog.getOpenFileName(
            self, "Select Map Image (> 500x500px recommended)", "", "Support Images (*.png *.jpg)")
        if ok:
            base = os.path.basename(fileName)
            name, ext = os.path.splitext(base)
            name = name.replace("_", " ")
            self.controller.addMap(fileName, map)
            self.changePreview()

    def addMap(self):
        fileName, ok = QFileDialog.getOpenFileName(
            self, "Select Map Image (> 500x500px recommended)", "", "Support Images (*.png *.jpg)")
        if ok:
            base = os.path.basename(fileName)
            name, ext = os.path.splitext(base)
            name = name.replace("_", " ")
            text, ok = QInputDialog.getText(
                self, 'Map Name', 'Map Name:', text=name)
            if ok:
                if(text.strip() in scctool.settings.maps):
                    buttonReply = QMessageBox.warning(self, "Duplicate Entry", "Map is already in list! Overwrite?",
                                                      QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                    if buttonReply == QMessageBox.No:
                        return

                self.controller.addMap(fileName, text)
                item = QListWidgetItem(text)
                self.maplist.addItem(item)
                self.maplist.setCurrentItem(item)

    def deleteMap(self):
        item = self.maplist.currentItem()
        map = item.text()
        buttonReply = QMessageBox.question(self, 'Delete map?', "Delete '{}' permanently?".format(
            map), QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if buttonReply == QMessageBox.Yes:
            self.controller.deleteMap(map)
            self.maplist.takeItem(self.maplist.currentRow())

    def changePreview(self):
        map = self.maplist.currentItem().text()
        if(map == "TBD"):
            self.pb_renameMap.setEnabled(False)
            self.pb_removeMap.setEnabled(False)
        else:
            self.pb_removeMap.setEnabled(True)
            self.pb_renameMap.setEnabled(True)

        self.mapPreview.setPixmap(QPixmap(self.controller.getMapImg(map, True)).scaled(
            self.mapsize, self.mapsize, Qt.KeepAspectRatio))

    def createButtonGroup(self):
        try:
            layout = QHBoxLayout()

            layout.addWidget(QLabel(""))

            buttonCancel = QPushButton('Cancel')
            buttonCancel.clicked.connect(self.closeWindow)
            layout.addWidget(buttonCancel)

            buttonSave = QPushButton('Save && Close')
            buttonSave.clicked.connect(self.saveCloseWindow)
            layout.addWidget(buttonSave)

            self.buttonGroup = layout
        except Exception as e:
            module_logger.exception("message")

    def saveData(self):
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
        self.saveData()
        self.passEvent = True
        self.close()

    def closeWindow(self):
        self.passEvent = True
        self.close()

    def closeEvent(self, event):
        try:
            self.mainWindow.updateMapCompleters()
            if(not self.__dataChanged):
                event.accept()
                return
            if(not self.passEvent):
                if(self.isMinimized()):
                    self.showNormal()
                buttonReply = QMessageBox.question(
                    self, 'Save data?', "Save data?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if buttonReply == QMessageBox.Yes:
                    self.saveData()
            event.accept()
        except Exception as e:
            module_logger.exception("message")
