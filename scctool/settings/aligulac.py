"""Provide aligulac id manager for SCCTool."""
import json
import logging

from PyQt5.QtCore import QObject, pyqtSignal

import scctool.settings.translation
from scctool.settings import getJsonFile

module_logger = logging.getLogger(__name__)
_ = scctool.settings.translation.gettext


class AligulacManager(QObject):
    """Provide aligulac id manager for SCCTool."""

    dataChanged = pyqtSignal()

    def __init__(self):
        """Init the manager."""
        super().__init__()
        self.loadJson()

    def loadJson(self):
        """Read json data from file."""
        try:
            with open(getJsonFile('aligulac'), 'r',
                      encoding='utf-8-sig') as json_file:
                data = json.load(json_file)
        except Exception:
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
        except Exception:
            module_logger.exception("message")

    def addID(self, name, aligulac_id):
        """Connect a name to an aligulac id."""
        name = str(name).strip()

        if not isinstance(aligulac_id, int):
            aligulac_id = int(aligulac_id)

        if aligulac_id <= 0:
            raise ValueError('aligulac_id <= 0')

        if self.__player2id.get(name, 0) != aligulac_id:
            self.__player2id[name] = aligulac_id
            self.dataChanged.emit()

    def getID(self, name):
        """Return a player's aligulac id."""
        name = str(name).strip()
        if name not in self.__player2id:
            raise ValueError('Name not found.')
        return self.__player2id[name]

    def removeID(self, name):
        """Remove an player id."""
        name = str(name).strip()
        if name in self.__player2id:
            del self.__player2id[name]
            self.dataChanged.emit()

    def getList(self):
        """Return saved aligulac list."""
        return dict(self.__player2id)

    def available(self, name):
        """Check if a name is in the list."""
        return str(name).strip() in self.__player2id

    def translate(self, name):
        """Translate a player to an id if in list."""
        if self.available(name):
            return self.getID(name)
        else:
            return name
