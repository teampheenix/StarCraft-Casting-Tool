"""Match Controller."""
import json
import logging
from collections import OrderedDict
from time import time

from PyQt5.QtCore import QObject, pyqtSignal

import scctool.settings
from scctool.matchdata import MatchData
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
        self.__matches = dict()
        self.__controller = controller
        self.__initProviderList()
        self.__initScopes()
        self.__initCustomFormats()
        self.__activeMatch = None
        self.__selectedMatch = None
        self.__order = list()

    def readJsonFile(self):
        """Read json data from file."""
        new_id = self._uniqid()
        try:
            with open(scctool.settings.getJsonFile('matchdata'),
                      'r', encoding='utf-8-sig') as json_file:
                data = json.load(json_file)
                if isinstance(data, dict):
                    if ('matches' not in data or
                            'active' not in data or
                            'selected' not in data or
                            'order' not in data):
                        data = {'matches': {new_id: data},
                                'active': new_id,
                                'selected': new_id,
                                'order': [new_id]}
                else:
                    data = {'matches': {new_id: dict()},
                            'active': new_id,
                            'selected': new_id,
                            'order': [new_id]}
        except Exception as e:
            data = {'matches': {new_id: dict()},
                    'active': new_id,
                    'selected': new_id,
                    'order': [new_id]}

        for id, match in data.get('matches', {new_id: dict()}).items():
            self.newMatchData(match, id)

        self.__order = data.get('order', self.__matches.keys())
        self.activateMatch(data.get('active', id))
        self.selectMatch(data.get('selected', id))

    def writeJsonFile(self):
        """Write json data to file."""
        try:
            matches = {}
            for id, match in self.__matches.items():
                matches[id] = match.getData()
            data = {'matches': matches}
            data['active'] = self.__activeMatch
            data['selected'] = self.__selectedMatch
            data['order'] = self.__order
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
        self.CUSTOM_FORMATS = OrderedDict(sorted(formats.items()))

    def getCustomFormats(self):
        for custom_format in self.CUSTOM_FORMATS.keys():
            yield custom_format, self.CUSTOM_FORMATS[custom_format]._icon

    def newMatchData(self, data=dict(), id=''):
        if not id:
            while True:
                id = self._uniqid()
                if id not in self.__matches.keys():
                    break
        match = MatchData(self, self.__controller, id, data)
        self.__matches[id] = match
        self.__order.append(id)
        return match

    def activeMatch(self):
        return self.__matches[self.__activeMatch]

    def selectedMatch(self):
        return self.__matches[self.__selectedMatch]

    def selectMatch(self, id):
        if id in self.__matches.keys() and self.__selectedMatch != id:
            self.__selectedMatch = id
            module_logger.info('Selected match {}'.format(id))

    def activateMatch(self, id):
        if id in self.__matches.keys() and self.__activeMatch != id:
            old_id = self.__activeMatch
            self.__activeMatch = id
            print(id, old_id)
            if old_id is not None and old_id in self.__matches.keys():
                try:
                    self.__matches[old_id].metaChanged.disconnect()
                except TypeError as e:
                    module_logger.exception("message")
                try:
                    self.__matches[old_id].dataChanged.disconnect()
                except TypeError as e:
                    module_logger.exception("message")
            self.__matches[id].metaChanged.connect(self.__handleMetaSignal)
            self.__matches[id].dataChanged.connect(self.__handleDataSignal)
            self.metaChanged.emit()
            module_logger.info('Activated match {}'.format(id))

    def __handleDataSignal(self, *args):
        self.dataChanged.emit(*args)

    def __handleMetaSignal(self):
        self.metaChanged.emit()

    def getMatch(self, id):
        return self.__matches[id]

    def activeMatchId(self):
        return self.__activeMatch

    def selectedMatchId(self):
        return self.__selectedMatch

    def selectedMatchIdx(self):
        return self.__order.index(self.__selectedMatch)

    def getMatches(self):
        for id in self.__order:
            yield self.__matches[id]

    def _uniqid(self):
        return hex(int(time() * 10000000))[10:]

    def updateOrder(self, toIdx, fromIdx):
        self.__order[toIdx], self.__order[fromIdx] =\
            self.__order[fromIdx], self.__order[toIdx]

    def removeMatch(self, ident):
        index = self.__order.index(ident)
        self.__order.pop(index)
        try:
            self.__matches[ident].metaChanged.disconnect()
        except TypeError as e:
            pass
        try:
            self.__matches[ident].dataChanged.disconnect()
        except TypeError as e:
            pass
        del self.__matches[ident]
        if ident == self.activeMatchId():
            new_index = index - 1 if index > 0 else 0
            # new_ident = self.__order[new_index]
            # self.activateMatch(new_ident)
            return new_index
