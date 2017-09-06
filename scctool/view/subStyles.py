"""Show styles settings sub window."""
import logging

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from scctool.view.widgets import *
import scctool.settings

# create logger
module_logger = logging.getLogger('scctool.view.subStyles')


class SubwindowStyles(QWidget):
    """Show styles settings sub window."""

    def createWindow(self, mainWindow):
        """Create styles settings sub window."""
        try:
            parent = None
            super(SubwindowStyles, self).__init__(parent)

            self.setWindowIcon(
                QIcon(scctool.settings.getAbsPath('src/pantone.png')))
            self.setWindowModality(Qt.ApplicationModal)
            self.mainWindow = mainWindow
            self.passEvent = False
            self.controller = mainWindow.controller
            self.__dataChanged = False

            self.createButtonGroup()
            self.createColorBox()
            self.createStyleBox()

            mainLayout = QVBoxLayout()
            mainLayout.addWidget(self.styleBox)
            mainLayout.addWidget(self.colorBox)
            mainLayout.addItem(QSpacerItem(
                0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))
            mainLayout.addLayout(self.buttonGroup)
            self.setLayout(mainLayout)

            self.resize(QSize(mainWindow.size().width()
                              * .80, self.sizeHint().height()))
            relativeChange = + QPoint(mainWindow.size().width() / 2,
                                      mainWindow.size().height() / 3)\
                - QPoint(self.size().width() / 2, self.size().height() / 3)
            self.move(mainWindow.pos() + relativeChange)

            self.setWindowTitle("Style Settings")

        except Exception as e:
            module_logger.exception("message")

    def changed(self):
        self.__dataChanged = True

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

    def createStyleBox(self):
        self.styleBox = QGroupBox("Styles")
        layout = QFormLayout()

        container = QHBoxLayout()
        self.qb_boxStyle = StyleComboBox(
            scctool.settings.OBSmapDir + "/src/css/box_styles",
            scctool.settings.config.parser.get("Style", "mapicon_box"))
        self.qb_boxStyle.currentIndexChanged.connect(self.changed)
        label = QLabel("Box Map Icons:")
        label.setMinimumWidth(110)
        button = QPushButton("Show in Browser")
        button.clicked.connect(lambda: self.openHTML(
            scctool.settings.OBSmapDir + "/icons_box/all_maps.html"))
        container.addWidget(self.qb_boxStyle)
        container.addWidget(button)
        layout.addRow(label, container)

        container = QHBoxLayout()
        self.qb_landscapeStyle = StyleComboBox(
            scctool.settings.OBSmapDir + "/src/css/landscape_styles",
            scctool.settings.config.parser.get("Style", "mapicon_landscape"))
        self.qb_landscapeStyle.currentIndexChanged.connect(self.changed)
        button = QPushButton("Show in Browser")
        button.clicked.connect(lambda: self.openHTML(
            scctool.settings.OBSmapDir + "/icons_landscape/all_maps.html"))
        container.addWidget(self.qb_landscapeStyle)
        container.addWidget(button)
        layout.addRow(QLabel("Landscape Map Icons:"), container)

        container = QHBoxLayout()
        self.qb_scoreStyle = StyleComboBox(
            scctool.settings.OBShtmlDir + "/src/css/score_styles",
            scctool.settings.config.parser.get("Style", "score"))
        self.qb_scoreStyle.currentIndexChanged.connect(self.changed)
        button = QPushButton("Show in Browser")
        button.clicked.connect(lambda: self.openHTML(
            scctool.settings.OBShtmlDir + "/score.html"))
        container.addWidget(self.qb_scoreStyle)
        container.addWidget(button)
        layout.addRow(QLabel("Score:"), container)

        container = QHBoxLayout()
        self.qb_introStyle = StyleComboBox(
            scctool.settings.OBShtmlDir + "/src/css/intro_styles",
            scctool.settings.config.parser.get("Style", "intro"))
        self.qb_introStyle.currentIndexChanged.connect(self.changed)
        button = QPushButton("Show in Browser")
        button.clicked.connect(lambda: self.openHTML(
            scctool.settings.OBShtmlDir + "/intro1.html"))
        container.addWidget(self.qb_introStyle)
        container.addWidget(button)
        layout.addRow(QLabel("Intros:"), container)

        self.pb_applyStyles = QPushButton("Apply")
        self.pb_applyStyles.clicked.connect(self.applyStyles)
        layout.addRow(QLabel(), self.pb_applyStyles)

        self.styleBox.setLayout(layout)

    def openHTML(self, file):
        self.controller.openURL(os.path.abspath(file))

    def applyStyles(self):
        self.qb_boxStyle.apply(
            self.controller, scctool.settings.OBSmapDir + "/src/css/box.css")
        self.qb_landscapeStyle.apply(
            self.controller, scctool.settings.OBSmapDir + "/src/css/landscape.css")
        self.qb_scoreStyle.apply(
            self.controller, scctool.settings.OBShtmlDir + "/src/css/score.css")
        self.qb_introStyle.apply(
            self.controller, scctool.settings.OBShtmlDir + "/src/css/intro.css")

    def createColorBox(self):
        self.colorBox = QGroupBox("Colors")
        layout = QVBoxLayout()

        self.default_color = ColorLayout(
            self, "Default Border:",
            scctool.settings.config.parser.get("MapIcons", "default_border_color"), "#f29b00")
        layout.addLayout(self.default_color)
        self. win_color = ColorLayout(
            self, "Win:",
            scctool.settings.config.parser.get("MapIcons", "win_color"), "#008000")
        layout.addLayout(self.win_color)
        self.lose_color = ColorLayout(
            self, "Lose:",
            scctool.settings.config.parser.get("MapIcons", "lose_color"), "#f22200")
        layout.addLayout(self.lose_color)
        self.undecided_color = ColorLayout(
            self, "Undecided:",
            scctool.settings.config.parser.get("MapIcons", "undecided_color"), "#f29b00")
        layout.addLayout(self.undecided_color)
        self.notplayed_color = ColorLayout(
            self, "Not played:",
            scctool.settings.config.parser.get("MapIcons", "notplayed_color"), "#c0c0c0")
        layout.addLayout(self.notplayed_color)

        self.colorBox.setLayout(layout)

    def saveData(self):
        if(self.__dataChanged):
            scctool.settings.config.parser.set(
                "MapIcons", "default_border_color", self.default_color.getColor())
            scctool.settings.config.parser.set(
                "MapIcons", "undecided_color", self.undecided_color.getColor())
            scctool.settings.config.parser.set(
                "MapIcons", "win_color", self.win_color.getColor())
            scctool.settings.config.parser.set(
                "MapIcons", "lose_color", self.lose_color.getColor())
            scctool.settings.config.parser.set(
                "MapIcons", "notplayed_color", self.notplayed_color.getColor())

            scctool.settings.config.parser.set(
                "Style", "mapicon_landscape", self.qb_landscapeStyle.currentText())
            scctool.settings.config.parser.set(
                "Style", "mapicon_box", self.qb_boxStyle.currentText())
            scctool.settings.config.parser.set(
                "Style", "score", self.qb_scoreStyle.currentText())
            scctool.settings.config.parser.set(
                "Style", "intro", self.qb_introStyle.currentText())

            self.controller.matchData.allChanged()

    def saveCloseWindow(self):
        self.saveData()
        self.passEvent = True
        self.close()

    def closeWindow(self):
        self.passEvent = True
        self.close()

    def closeEvent(self, event):
        try:
            if(not self.__dataChanged):
                event.accept()
                return
            if(not self.passEvent):
                if(self.isMinimized()):
                    self.showNormal()
                buttonReply = QMessageBox.question(
                    self, 'Save data?', "Save data?",
                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if buttonReply == QMessageBox.Yes:
                    self.saveData()
            event.accept()
        except Exception as e:
            module_logger.exception("message")
