import json
import logging

from PyQt5.QtCore import QObject, pyqtSignal

import scctool.settings.translation
from scctool.settings import getJsonFile

"""Provide aligulac id manager for SCCTool."""



module_logger = logging.getLogger(__name__)
_ = scctool.settings.translation.gettext


class AligulacManager(QObject):

    dataChanged = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.loadJson()

    def loadJson(self):
        """Read json data from file."""
        try:
            with open(getJsonFile('aligulac'), 'r',
                      encoding='utf-8-sig') as json_file:
                data = json.load(json_file)
        except Exception as e:
            data = dict()

        self.__player2id = data

        if not isinstance(self.__player2id, dict):
            self.__player2id = dict()

    def dumpJson(self):
        """Write json data to file."""
        try:
            with open(getJsonFile('aligulac'), 'w',
                      encoding='utf-8-sig') as outfile:
                json.dump(self.__player2id, outfile)
        except Exception as e:
            module_logger.exception("message")

    def addID(self, name, id):
        name = str(name).strip()

        if not isinstance(id, int):
            id = int(id)

        if id <= 0:
            raise ValueError('ID <= 0')

        if self.__player2id.get(name, 0) != id:
            self.__player2id[name] = id
            self.dataChanged.emit()

    def getID(self, name):
        name = str(name).strip()
        if name not in self.__player2id:
            raise ValueError('Name not found.')
        return self.__player2id[name]

    def removeID(self, name):
        name = str(name).strip()
        if name in self.__player2id:
            del self.__player2id[name]
            self.dataChanged.emit()

    def getList(self):
        return dict(self.__player2id)

    def available(self, name):
        return str(name).strip() in self.__player2id

    def translate(self, name):
        if self.available(name):
            return self.getID(name)
        else:
            return name
