"""Match Controller."""
import json
import logging
from collections import OrderedDict

from PyQt5.QtCore import QObject, pyqtSignal

import scctool.settings
from scctool.matchdata import matchData
from scctool.matchformat import *
from scctool.matchgrabber import *

# create logger
module_logger = logging.getLogger('scctool.matchcontrol')


class MatchControl(QObject):
    """Controler for match data."""
    dataChanged = pyqtSignal(str, object)
    metaChanged = pyqtSignal()
    scopes = {}

    def __init__(self, controller):
        """Init and define custom providers."""
        super().__init__()
        self.__matches = list()
        self.__controller = controller
        self.__initProviderList()
        self.__initScopes()
        self.__initCustomFormats()
        self.__activeMatch = 0

    def readJsonFile(self):
        """Read json data from file."""
        try:
            with open(scctool.settings.getJsonFile('matchdata'),
                      'r', encoding='utf-8-sig') as json_file:
                data = json.load(json_file)
                if isinstance(data, dict):
                    if 'matches' not in data or 'active' not in data:
                        data = {'matches': [data], 'active': 0}
                else:
                    data = {'matches': [dict()], 'active': 0}
        except Exception as e:
            data = {'matches': [dict()], 'active': 0}

        for match in data.get('matches', []):
            self.newMatchData(match)

        self.__activeMatch = data.get('active', 0)

    def writeJsonFile(self):
        """Write json data to file."""
        try:
            matches = []
            for match in self.__matches:
                matches.append(match.getData())
            data = {'matches': matches, 'active': self.__activeMatch}
            with open(scctool.settings.getJsonFile('matchdata'),
                      'w', encoding='utf-8-sig') as outfile:
                json.dump(data, outfile)
        except Exception as e:
            module_logger.exception("message")

    def __initScopes(self):
        self.scopes = {'all': _('All Maps'),
                       'not-ace': _('None Ace Maps'),
                       'ace': _('Ace Maps'),
                       'decided': _('Decided Maps'),
                       'decided+1': _('Decided Maps + 1'),
                       'current': _('Current Map'),
                       'current+1': _('Current and Previous Map'),
                       'undecided': _('Undecided Maps')}

    def __initProviderList(self):
        self.VALID_PROVIDERS = dict()
        self.VALID_PROVIDERS[MatchGrabber._provider] = MatchGrabber
        for cls in MatchGrabber.__subclasses__():
            self.VALID_PROVIDERS[cls._provider] = cls

    def __initCustomFormats(self):
        formats = dict()
        for cls in MatchFormat.__subclasses__():
            formats[cls._name] = cls
        self.__CUSTOM_FORMATS = OrderedDict(sorted(formats.items()))

    def getCustomFormats(self):
        for custom_format in self.__CUSTOM_FORMATS.keys():
            yield custom_format, self.__CUSTOM_FORMATS[custom_format]._icon

    def applyCustomFormat(self, name):
        if name in self.__CUSTOM_FORMATS:
            customFormat = self.__CUSTOM_FORMATS[name](self)
            with self.emitLock(True, self.metaChangedSignal):
                customFormat.applyFormat()
        else:
            raise ValueError("Unknown Custom Match Format.")

    def newMatchData(self, data=dict()):
        self.__matches.append(matchData(self, self.__controller, data))

    def activeMatch(self):
        return self.__matches[self.__activeMatch]
