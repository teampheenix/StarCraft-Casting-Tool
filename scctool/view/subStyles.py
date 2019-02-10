"""Subwindow for style settings."""
import logging

from PyQt5.QtCore import QPoint, QSize, Qt
from PyQt5.QtGui import QFontDatabase, QIcon, QKeySequence
from PyQt5.QtWidgets import (QCheckBox, QComboBox, QFormLayout, QGridLayout,
                             QGroupBox, QHBoxLayout, QLabel, QMessageBox,
                             QPushButton, QShortcut, QSizePolicy, QSpacerItem,
                             QTabWidget, QVBoxLayout, QWidget)

import scctool.settings
import scctool.settings.translation
from scctool.view.widgets import ColorLayout, StyleComboBox, TextPreviewer


# create logger
module_logger = logging.getLogger(__name__)
_ = scctool.settings.translation.gettext


class SubwindowStyles(QWidget):
    """Show styles settings sub window."""
    current_tab = -1

    def createWindow(self, mainWindow, tab=''):
        """Create styles settings sub window."""
        try:
            parent = None
            super().__init__(parent)

            self.setWindowIcon(
                QIcon(scctool.settings.getResFile('pantone.png')))
            self.setWindowModality(Qt.ApplicationModal)
            self.mainWindow = mainWindow
            self.passEvent = False
            self.controller = mainWindow.controller
            self.__dataChanged = False

            self.createButtonGroup()
            self.createColorBox()
            self.createStyleBox()
            self.createFontBox()

            self.tabs = QTabWidget()
            self.tabs.addTab(self.styleBox, _("Styles"))
            self.tabs.addTab(self.colorBox, _("Colors"))
            self.tabs.addTab(self.fontBox, _("Font"))

            table = dict()
            table['styles'] = 0
            table['colors'] = 1
            table['font'] = 2
            self.tabs.setCurrentIndex(
                table.get(tab, SubwindowStyles.current_tab))
            self.tabs.currentChanged.connect(self.tabChanged)

            mainLayout = QVBoxLayout()
            mainLayout.addWidget(self.tabs)
            mainLayout.addItem(QSpacerItem(
                0, 0, QSizePolicy.Minimum,
                QSizePolicy.Expanding))
            mainLayout.addLayout(self.buttonGroup)
            self.setLayout(mainLayout)

            self.resize(QSize(mainWindow.size().width() * .80,
                              self.sizeHint().height()))
            relativeChange = + QPoint(mainWindow.size().width() / 2,
                                      mainWindow.size().height() / 3)\
                - QPoint(self.size().width() / 2,
                         self.size().height() / 3)
            self.move(mainWindow.pos() + relativeChange)

            self.setWindowTitle(_("Style Settings"))

        except Exception:
            module_logger.exception("message")

    @classmethod
    def tabChanged(cls, idx):
        """Save the current tab."""
        SubwindowStyles.current_tab = idx

    def changed(self):
        """Handle data change."""
        self.__dataChanged = True

    def createButtonGroup(self):
        """Create buttons."""
        try:
            layout = QHBoxLayout()

            layout.addWidget(QLabel(""))

            buttonCancel = QPushButton(_('Cancel'))
            buttonCancel.clicked.connect(self.closeWindow)
            layout.addWidget(buttonCancel)

            buttonSave = QPushButton(_('&Save && Close'))
            buttonSave.setToolTip(_("Shortcut: {}").format("Ctrl+S"))
            self.shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
            self.shortcut.setAutoRepeat(False)
            self.shortcut.activated.connect(self.saveCloseWindow)
            buttonSave.clicked.connect(self.saveCloseWindow)
            layout.addWidget(buttonSave)

            self.buttonGroup = layout
        except Exception:
            module_logger.exception("message")

    def createStyleBox(self):
        """Create style box."""
        self.styleBox = QWidget()
        layout = QFormLayout()

        try:
            container = QHBoxLayout()
            self.qb_boxStyle = StyleComboBox(
                scctool.settings.casting_html_dir + "/src/css/mapicons_box",
                "mapicons_box")
            self.qb_boxStyle.connect2WS(self.controller, 'mapicons_box')
            label = QLabel(_("Box Map Icons:"))
            label.setMinimumWidth(110)
            button = QPushButton(_("Show in Browser"))
            button.clicked.connect(lambda: self.openHTML(
                scctool.settings.casting_html_dir + "/mapicons_box_1.html"))
            container.addWidget(self.qb_boxStyle)
            container.addWidget(button)
            layout.addRow(label, container)
        except Exception:
            module_logger.exception("message")

        try:
            container = QHBoxLayout()
            self.qb_landscapeStyle = StyleComboBox(
                scctool.settings.casting_html_dir +
                "/src/css/mapicons_landscape",
                "mapicons_landscape")
            self.qb_landscapeStyle.connect2WS(
                self.controller, 'mapicons_landscape')
            button = QPushButton(_("Show in Browser"))
            button.clicked.connect(lambda: self.openHTML(
                scctool.settings.casting_html_dir +
                "/mapicons_landscape_1.html"))
            container.addWidget(self.qb_landscapeStyle)
            container.addWidget(button)
            layout.addRow(QLabel(
                _("Landscape Map Icons:")), container)
        except Exception:
            module_logger.exception("message")

        try:
            container = QHBoxLayout()
            self.qb_scoreStyle = StyleComboBox(
                scctool.settings.casting_html_dir + "/src/css/score",
                "score")
            self.qb_scoreStyle.connect2WS(self.controller, 'score')
            button = QPushButton(_("Show in Browser"))
            button.clicked.connect(lambda: self.openHTML(
                scctool.settings.casting_html_dir + "/score.html"))
            container.addWidget(self.qb_scoreStyle)
            container.addWidget(button)
            layout.addRow(QLabel(_("Score:")), container)
        except Exception:
            module_logger.exception("message")

        try:
            container = QHBoxLayout()
            self.qb_introStyle = StyleComboBox(
                scctool.settings.casting_html_dir + "/src/css/intro",
                "intro")
            self.qb_introStyle.connect2WS(self.controller, 'intro')
            button = QPushButton(_("Show in Browser"))
            button.clicked.connect(lambda: self.openHTML(
                scctool.settings.casting_html_dir + "/intro.html"))
            container.addWidget(self.qb_introStyle)
            container.addWidget(button)
            layout.addRow(QLabel(_("Intros:")), container)
        except Exception:
            module_logger.exception("message")

        try:
            container = QHBoxLayout()
            self.qb_mapstatsStyle = StyleComboBox(
                scctool.settings.casting_html_dir + "/src/css/mapstats",
                "mapstats")
            self.qb_mapstatsStyle.connect2WS(self.controller, 'mapstats')
            button = QPushButton(_("Show in Browser"))
            button.clicked.connect(lambda: self.openHTML(
                scctool.settings.casting_html_dir + "/mapstats.html"))
            container.addWidget(self.qb_mapstatsStyle)
            container.addWidget(button)
            layout.addRow(QLabel(_("Map Stats:")), container)
        except Exception:
            module_logger.exception("message")

        try:
            container = QHBoxLayout()
            self.qb_aligulacStyle = StyleComboBox(
                scctool.settings.casting_html_dir + "/src/css/aligulac",
                "aligulac")
            self.qb_aligulacStyle.connect2WS(self.controller, 'aligulac')
            button = QPushButton(_("Show in Browser"))
            button.clicked.connect(lambda: self.openHTML(
                scctool.settings.casting_html_dir + "/aligulac.html"))
            container.addWidget(self.qb_aligulacStyle)
            container.addWidget(button)
            layout.addRow(QLabel(_("Aligulac:")), container)
        except Exception:
            module_logger.exception("message")

        try:
            container = QHBoxLayout()
            self.qb_countdownStyle = StyleComboBox(
                scctool.settings.casting_html_dir + "/src/css/countdown",
                "countdown")
            self.qb_countdownStyle.connect2WS(self.controller, 'countdown')
            button = QPushButton(_("Show in Browser"))
            button.clicked.connect(lambda: self.openHTML(
                scctool.settings.casting_html_dir + "/countdown.html"))
            container.addWidget(self.qb_countdownStyle)
            container.addWidget(button)
            layout.addRow(QLabel(_("Countdown:")), container)
        except Exception:
            module_logger.exception("message")

        try:
            container = QHBoxLayout()
            self.qb_countdownStyle = StyleComboBox(
                scctool.settings.casting_html_dir + "/src/css/vetos",
                "vetos")
            self.qb_countdownStyle.connect2WS(self.controller, 'vetos')
            button = QPushButton(_("Show in Browser"))
            button.clicked.connect(lambda: self.openHTML(
                scctool.settings.casting_html_dir + "/vetos.html"))
            container.addWidget(self.qb_countdownStyle)
            container.addWidget(button)
            layout.addRow(QLabel(_("Vetos") + ':'), container)
        except Exception:
            module_logger.exception("message")

        layout.addRow(QLabel(''))
        stylesDisc = _(
            'StarCraft Casting Tools allows you to make your own skins/styles'
            ' via CSS by placing an alternative CSS-files into '
            'casting_html/src/css/{browser-source}. If you do so, please'
            ' share these skins with this project. In case you need help'
            ' or just want to share your ideas for new skins'
            ' join our Discord Server.')
        label = QLabel(stylesDisc)
        label.setAlignment(Qt.AlignJustify)
        label.setWordWrap(True)
        layout.addRow(label)

        self.styleBox.setLayout(layout)

    def openHTML(self, file):
        """Open file in browser."""
        self.controller.openURL(scctool.settings.getAbsPath(file))

    def createColorBox(self):
        """Create box for color selection."""
        self.colorBox = QWidget()
        mainLayout = QVBoxLayout()

        box = QGroupBox(_("Map and Score Icons"))
        layout = QVBoxLayout()
        self.default_color = ColorLayout(
            self, _("Default Border:"),
            scctool.settings.config.parser.get(
                "MapIcons", "default_border_color"),
            "#f29b00")
        layout.addLayout(self.default_color)
        self.winner_color = ColorLayout(
            self, _("Winner Highlight:"),
            scctool.settings.config.parser.get(
                "MapIcons", "winner_highlight_color"),
            "#f29b00")
        layout.addLayout(self.winner_color)
        self.win_color = ColorLayout(
            self, _("Win:"),
            scctool.settings.config.parser.get("MapIcons", "win_color"),
            "#008000")
        layout.addLayout(self.win_color)
        self.lose_color = ColorLayout(
            self, _("Lose:"),
            scctool.settings.config.parser.get("MapIcons", "lose_color"),
            "#f22200")
        layout.addLayout(self.lose_color)
        self.undecided_color = ColorLayout(
            self, _("Undecided:"),
            scctool.settings.config.parser.get("MapIcons", "undecided_color"),
            "#aaaaaa")
        layout.addLayout(self.undecided_color)
        self.notplayed_color = ColorLayout(
            self, _("Not played:"),
            scctool.settings.config.parser.get("MapIcons", "notplayed_color"),
            "#aaaaaa")
        layout.addLayout(self.notplayed_color)
        box.setLayout(layout)
        mainLayout.addWidget(box)

        box = QGroupBox(_("Map Stats"))
        layout = QVBoxLayout()
        self.mapstats_color1 = ColorLayout(
            self, _("Color 1:"),
            scctool.settings.config.parser.get("Mapstats", "color1"),
            "#6495ed")
        layout.addLayout(self.mapstats_color1)
        self.mapstats_color2 = ColorLayout(
            self, _("Color 2:"),
            scctool.settings.config.parser.get("Mapstats", "color2"),
            "#000000")
        layout.addLayout(self.mapstats_color2)
        box.setLayout(layout)
        mainLayout.addWidget(box)

        self.colorBox.setLayout(mainLayout)

    def createFontBox(self):
        """Create box for font selection."""
        self.fontBox = QWidget()
        layout = QGridLayout()

        label = QLabel(
            _("Warning: Using a custom font instead of the regular font"
              " defined in the Icon Styles can lead to unitentional"
              " appereance.") +
            _("The proper way is to create a custom skin."))
        label.setWordWrap(True)
        label.setAlignment(Qt.AlignJustify)
        layout.addWidget(label, 1, 0, 1, 2)
        label = QLabel(_("Activate Custom Font") + ":")
        label.setMinimumWidth(110)
        self.cb_usefont = QCheckBox(" ")
        self.cb_usefont.setChecked(
            scctool.settings.config.parser.getboolean(
                "Style",
                "use_custom_font"))
        self.cb_usefont.stateChanged.connect(self.changed)
        layout.addWidget(label, 0, 0, alignment=Qt.AlignVCenter)
        layout.addWidget(self.cb_usefont, 0, 1,
                         alignment=Qt.AlignVCenter)
        label = QLabel(_("Custom Font") + ":")
        label.setMinimumWidth(110)
        layout.addWidget(label, 2, 0)
        self.cb_font = QComboBox()
        my_font = scctool.settings.config.parser.get(
            "Style", "custom_font")
        fonts = QFontDatabase().families()
        for idx, font in enumerate(fonts):
            self.cb_font.addItem(str(font))
            if str(font).lower().strip() == my_font.lower():
                self.cb_font.setCurrentIndex(idx)
        self.cb_font.setStyleSheet("QComboBox { combobox-popup: 0; }")
        self.cb_font.currentIndexChanged.connect(self.changed)
        self.cb_font.currentIndexChanged.connect(self.updateFontPreview)
        layout.addWidget(self.cb_font, 2, 1)
        layout.setColumnStretch(1, 1)
        self.previewer = TextPreviewer()
        layout.addWidget(self.previewer, 3, 0, 1, 2)
        layout.addItem(QSpacerItem(
            0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding),
            4, 0)
        self.fontBox.setLayout(layout)
        self.updateFontPreview()

    def updateFontPreview(self):
        """Update the font preview."""
        font = self.cb_font.currentText().strip()
        self.previewer.setFont(font)

    def saveData(self):
        """Save data."""
        if(self.__dataChanged):
            scctool.settings.config.parser.set(
                "MapIcons", "default_border_color",
                self.default_color.getColor())
            scctool.settings.config.parser.set(
                "MapIcons", "undecided_color",
                self.undecided_color.getColor())
            scctool.settings.config.parser.set(
                "MapIcons", "winner_highlight_color",
                self.winner_color.getColor())
            scctool.settings.config.parser.set(
                "MapIcons", "win_color",
                self.win_color.getColor())
            scctool.settings.config.parser.set(
                "MapIcons", "lose_color",
                self.lose_color.getColor())
            scctool.settings.config.parser.set(
                "MapIcons", "notplayed_color",
                self.notplayed_color.getColor())

            scctool.settings.config.parser.set(
                "Mapstats", "color1",
                self.mapstats_color1.getColor())
            scctool.settings.config.parser.set(
                "Mapstats", "color2",
                self.mapstats_color2.getColor())

            scctool.settings.config.parser.set(
                "Style", "use_custom_font",
                str(self.cb_usefont.isChecked()))

            scctool.settings.config.parser.set(
                "Style", "custom_font",
                self.cb_font.currentText().strip())

            colors = {'color1': self.mapstats_color1.getColor(),
                      'color2': self.mapstats_color2.getColor()}
            self.controller.websocketThread.changeColors('mapstats', colors)
            self.controller.websocketThread.changeFont()
            self.controller.matchMetaDataChanged()
            self.__dataChanged = False

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
                buttonReply = QMessageBox.question(
                    self, _('Save data?'), _("Save data?"),
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No)
                if buttonReply == QMessageBox.Yes:
                    self.saveData()
            event.accept()
        except Exception:
            module_logger.exception("message")
