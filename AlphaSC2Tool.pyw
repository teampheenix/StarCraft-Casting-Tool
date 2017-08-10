#!/usr/bin/python
import sys

from alphasc2tool.controller import *
from alphasc2tool.view import *

from PyQt5.QtWidgets import QApplication, QStyleFactory
from PyQt5.QtGui import QIcon

def main():
    
    app = QApplication(sys.argv)
    QApplication.setStyle(QStyleFactory.create('Fusion'))
    app.setWindowIcon(QIcon('src/alpha.ico'))
    controller = AlphaController()
    view = mainWindow(controller)
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()