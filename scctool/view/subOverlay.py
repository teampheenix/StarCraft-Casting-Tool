"""Shows an overlay for ingame."""
import logging
import os
import sys

from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QVBoxLayout, QWidget, QApplication

import scctool.settings

# create logger
module_logger = logging.getLogger('scctool.view.subOverlay')


class SubwindowOverlay(QWidget):
    """Show styles settings sub window."""

    def createWindow(self, mainWindow):
        """Shows an overlay for ingame."""
        try:
            parent = None
            super().__init__(parent)

            self.mainWindow = mainWindow
            self.controller = mainWindow.controller

            self.view = QWebEngineView(self)

            layout = QVBoxLayout(self)
            self.setLayout(layout)
            layout.addWidget(self.view)
            file_path = os.path.abspath(scctool.settings.getResFile('overlay/main.html'))
            local_url = QUrl.fromLocalFile(file_path)
            self.view.load(local_url)
            self.view.setAttribute(Qt.WA_TransparentForMouseEvents)
            self.view.page().setBackgroundColor(Qt.transparent)
            self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
            self.setAttribute(
                 Qt.WA_TranslucentBackground, True)
            self.setWindowFlags(
                 Qt.Tool | Qt.FramelessWindowHint)
            self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

            self.resize(QApplication.primaryScreen().size())


        except Exception as e:
            module_logger.exception("message")

    def closeWindow(self):
        """Close window."""
        self.passEvent = True
        self.close()

    def closeEvent(self, event):
        """Handle close event."""
        event.accept()
