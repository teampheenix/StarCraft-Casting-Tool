"""Show styles settings sub window."""
import logging

import PyQt5

from scctool.view.widgets import StyleComboBox, ColorLayout
import scctool.settings

import os.path

# create logger
module_logger = logging.getLogger('scctool.view.subStyles')


class SubwindowStyles(PyQt5.QtWidgets.QWidget):
    """Show styles settings sub window."""

    def createWindow(self, mainWindow):
        """Create styles settings sub window."""
        try:
            parent = None
            super(SubwindowStyles, self).__init__(parent)

            self.setWindowIcon(
                PyQt5.QtGui.QIcon(scctool.settings.getAbsPath('src/pantone.png')))
            self.setWindowModality(PyQt5.QtCore.Qt.ApplicationModal)
            self.mainWindow = mainWindow
            self.passEvent = False
            self.controller = mainWindow.controller
            self.__dataChanged = False

            self.createButtonGroup()
            self.createColorBox()
            self.createStyleBox()

            mainLayout = PyQt5.QtWidgets.QVBoxLayout()
            mainLayout.addWidget(self.styleBox)
            mainLayout.addWidget(self.colorBox)
            mainLayout.addItem(PyQt5.QtWidgets.QSpacerItem(
                0, 0, PyQt5.QtWidgets.QSizePolicy.Minimum,
                PyQt5.QtWidgets.QSizePolicy.Expanding))
            mainLayout.addLayout(self.buttonGroup)
            self.setLayout(mainLayout)

            self.resize(PyQt5.QtCore.QSize(mainWindow.size().width()
                                           * .80, self.sizeHint().height()))
            relativeChange = + PyQt5.QtCore.QPoint(mainWindow.size().width() / 2,
                                                   mainWindow.size().height() / 3)\
                - PyQt5.QtCore.QPoint(self.size().width() / 2,
                                      self.size().height() / 3)
            self.move(mainWindow.pos() + relativeChange)

            self.setWindowTitle(_("Style Settings"))

        except Exception as e:
            module_logger.exception("message")

    def changed(self):
        """Handle data change."""
        self.__dataChanged = True

    def createButtonGroup(self):
        """Create buttons."""
        try:
            layout = PyQt5.QtWidgets.QHBoxLayout()

            layout.addWidget(PyQt5.QtWidgets.QLabel(""))

            buttonCancel = PyQt5.QtWidgets.QPushButton(_('Cancel'))
            buttonCancel.clicked.connect(self.closeWindow)
            layout.addWidget(buttonCancel)

            buttonSave = PyQt5.QtWidgets.QPushButton(_('Save && Close'))
            buttonSave.clicked.connect(self.saveCloseWindow)
            layout.addWidget(buttonSave)

            self.buttonGroup = layout
        except Exception as e:
            module_logger.exception("message")

    def createStyleBox(self):
        """Create style box."""
        self.styleBox = PyQt5.QtWidgets.QGroupBox(_("Styles"))
        layout = PyQt5.QtWidgets.QFormLayout()

        container = PyQt5.QtWidgets.QHBoxLayout()
        self.qb_boxStyle = StyleComboBox(
            scctool.settings.OBSmapDir + "/src/css/box_styles",
            scctool.settings.config.parser.get("Style", "mapicon_box"))
        self.qb_boxStyle.currentIndexChanged.connect(self.changed)
        label = PyQt5.QtWidgets.QLabel(_("Box Map Icons:"))
        label.setMinimumWidth(110)
        button = PyQt5.QtWidgets.QPushButton(_("Show in Browser"))
        button.clicked.connect(lambda: self.openHTML(
            scctool.settings.OBSmapDir + "/icons_box/all_maps.html"))
        container.addWidget(self.qb_boxStyle)
        container.addWidget(button)
        layout.addRow(label, container)

        container = PyQt5.QtWidgets.QHBoxLayout()
        self.qb_landscapeStyle = StyleComboBox(
            scctool.settings.OBSmapDir + "/src/css/landscape_styles",
            scctool.settings.config.parser.get("Style", "mapicon_landscape"))
        self.qb_landscapeStyle.currentIndexChanged.connect(self.changed)
        button = PyQt5.QtWidgets.QPushButton(_("Show in Browser"))
        button.clicked.connect(lambda: self.openHTML(
            scctool.settings.OBSmapDir + "/icons_landscape/all_maps.html"))
        container.addWidget(self.qb_landscapeStyle)
        container.addWidget(button)
        layout.addRow(PyQt5.QtWidgets.QLabel(
            _("Landscape Map Icons:")), container)

        container = PyQt5.QtWidgets.QHBoxLayout()
        self.qb_scoreStyle = StyleComboBox(
            scctool.settings.OBShtmlDir + "/src/css/score_styles",
            scctool.settings.config.parser.get("Style", "score"))
        self.qb_scoreStyle.currentIndexChanged.connect(self.changed)
        button = PyQt5.QtWidgets.QPushButton(_("Show in Browser"))
        button.clicked.connect(lambda: self.openHTML(
            scctool.settings.OBShtmlDir + "/score.html"))
        container.addWidget(self.qb_scoreStyle)
        container.addWidget(button)
        layout.addRow(PyQt5.QtWidgets.QLabel(_("Score:")), container)

        container = PyQt5.QtWidgets.QHBoxLayout()
        self.qb_introStyle = StyleComboBox(
            scctool.settings.OBShtmlDir + "/src/css/intro_styles",
            scctool.settings.config.parser.get("Style", "intro"))
        self.qb_introStyle.currentIndexChanged.connect(self.changed)
        button = PyQt5.QtWidgets.QPushButton(_("Show in Browser"))
        button.clicked.connect(lambda: self.openHTML(
            scctool.settings.OBShtmlDir + "/intro1.html"))
        container.addWidget(self.qb_introStyle)
        container.addWidget(button)
        layout.addRow(PyQt5.QtWidgets.QLabel(_("Intros:")), container)

        self.pb_applyStyles = PyQt5.QtWidgets.QPushButton(_("Apply"))
        self.pb_applyStyles.clicked.connect(self.applyStyles)
        layout.addRow(PyQt5.QtWidgets.QLabel(), self.pb_applyStyles)

        txt = _("Note that to make these changes visible in OBS" +
                " you have to refresh the cache of your browser sources.")
        label = PyQt5.QtWidgets.QLabel(txt)
        label.setWordWrap(True)
        layout.addRow(PyQt5.QtWidgets.QLabel(), label)

        self.styleBox.setLayout(layout)

    def openHTML(self, file):
        """Open file in browser."""
        self.controller.openURL(os.path.abspath(file))

    def applyStyles(self):
        """Apply styles."""
        self.qb_boxStyle.apply(
            self.controller, scctool.settings.OBSmapDir + "/src/css/box.css")
        self.qb_landscapeStyle.apply(
            self.controller, scctool.settings.OBSmapDir + "/src/css/landscape.css")
        self.qb_scoreStyle.apply(
            self.controller, scctool.settings.OBShtmlDir + "/src/css/score.css")
        self.qb_introStyle.apply(
            self.controller, scctool.settings.OBShtmlDir + "/src/css/intro.css")

    def createColorBox(self):
        """Create box for color selection."""
        self.colorBox = PyQt5.QtWidgets.QGroupBox(_("Colors"))
        layout = PyQt5.QtWidgets.QVBoxLayout()

        self.default_color = ColorLayout(
            self, _("Default Border:"),
            scctool.settings.config.parser.get("MapIcons", "default_border_color"), "#f29b00")
        layout.addLayout(self.default_color)
        self. win_color = ColorLayout(
            self, _("Win:"),
            scctool.settings.config.parser.get("MapIcons", "win_color"), "#008000")
        layout.addLayout(self.win_color)
        self.lose_color = ColorLayout(
            self, _("Lose:"),
            scctool.settings.config.parser.get("MapIcons", "lose_color"), "#f22200")
        layout.addLayout(self.lose_color)
        self.undecided_color = ColorLayout(
            self, _("Undecided:"),
            scctool.settings.config.parser.get("MapIcons", "undecided_color"), "#f29b00")
        layout.addLayout(self.undecided_color)
        self.notplayed_color = ColorLayout(
            self, _("Not played:"),
            scctool.settings.config.parser.get("MapIcons", "notplayed_color"), "#c0c0c0")
        layout.addLayout(self.notplayed_color)

        self.colorBox.setLayout(layout)

    def saveData(self):
        """Save data."""
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
            if(not self.__dataChanged):
                event.accept()
                return
            if(not self.passEvent):
                if(self.isMinimized()):
                    self.showNormal()
                buttonReply = PyQt5.QtWidgets.QMessageBox.question(
                    self, _('Save data?'), _("Save data?"),
                    PyQt5.QtWidgets.QMessageBox.Yes | PyQt5.QtWidgets.QMessageBox.No,
                    PyQt5.QtWidgets.QMessageBox.No)
                if buttonReply == PyQt5.QtWidgets.QMessageBox.Yes:
                    self.saveData()
            event.accept()
        except Exception as e:
            module_logger.exception("message")
