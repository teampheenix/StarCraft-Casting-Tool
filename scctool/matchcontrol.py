"""Match Controller."""
import json
import logging
from collections import OrderedDict
from time import time

from PyQt5.QtCore import QObject, pyqtSignal

import scctool.settings
import scctool.settings.translation
from scctool.matchdata import MatchData
from scctool.matchformat import MatchFormat
from scctool.matchgrabber import MatchGrabber

_ = scctool.settings.translation.gettext

# create logger
module_logger = logging.getLogger(__name__)


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
                    if ('matches' not in data
                            or 'active' not in data
                            or 'selected' not in data
                            or 'order' not in data):
                        data = {'matches': {new_id: data},
                                'active': new_id,
                                'selected': new_id,
                                'order': [new_id]}
                else:
                    data = {'matches': {new_id: dict()},
                            'active': new_id,
                            'selected': new_id,
                            'order': [new_id]}
        except Exception:
            data = {'matches': {new_id: dict()},
                    'active': new_id,
                    'selected': new_id,
                    'order': [new_id]}

        for ident, match in data.get('matches', {new_id: dict()}).items():
            self.newMatchData(match, ident)

        self.__order = data.get('order', self.__matches.keys())
        self.activateMatch(data.get('active', id))
        self.selectMatch(data.get('selected', id))

    def writeJsonFile(self):
        """Write json data to file."""
        try:
            matches = {}
            for ident, match in self.__matches.items():
                matches[ident] = match.getData()
            data = {'matches': matches}
            data['active'] = self.__activeMatch
            data['selected'] = self.__selectedMatch
            data['order'] = self.__order
            with open(scctool.settings.getJsonFile('matchdata'),
                      'w', encoding='utf-8-sig') as outfile:
                json.dump(data, outfile)
        except Exception:
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
        """Get all available custom formats."""
        for custom_format in self.CUSTOM_FORMATS.keys():
            yield custom_format, self.CUSTOM_FORMATS[custom_format]._icon

    def newMatchData(self, data=None, ident=''):
        """Insert new match data."""
        if not data:
            data = dict()
        if not ident:
            while True:
                ident = self._uniqid()
                if id not in self.__matches.keys():
                    break
        match = MatchData(self, self.__controller, ident, data)
        self.__matches[ident] = match
        self.__order.append(ident)
        return match

    def activeMatch(self):
        """Return the active match."""
        return self.__matches[self.__activeMatch]

    def selectedMatch(self):
        """Return the selected match."""
        return self.__matches[self.__selectedMatch]

    def selectMatch(self, ident):
        """Select a match."""
        if ident in self.__matches.keys() and self.__selectedMatch != ident:
            self.__selectedMatch = ident
            module_logger.info('Selected match {}'.format(ident))
            return True
        else:
            return False

    def activateMatch(self, ident):
        """Activate a match."""
        if ident in self.__matches.keys() and self.__activeMatch != ident:
            old_ident = self.__activeMatch
            self.__activeMatch = ident
            if old_ident is not None and old_ident in self.__matches.keys():
                try:
                    self.__matches[old_ident].metaChanged.disconnect()
                except TypeError:
                    module_logger.exception("message")
                try:
                    self.__matches[old_ident].dataChanged.disconnect()
                except TypeError:
                    module_logger.exception("message")
            self.__controller.placeholderSetup()
            self.__matches[ident].metaChanged.connect(self.__handleMetaSignal)
            self.__matches[ident].dataChanged.connect(self.__handleDataSignal)
            self.metaChanged.emit()
            module_logger.info(f'Activated match {ident}')

    def __handleDataSignal(self, *args):
        self.dataChanged.emit(*args)

    def __handleMetaSignal(self):
        self.metaChanged.emit()

    def getMatch(self, ident):
        """Get a match by id."""
        return self.__matches[ident]

    def activeMatchId(self):
        """Get id of the active match."""
        return self.__activeMatch

    def activeMatchIdx(self):
        """Get index of the active match."""
        return self.__order.index(self.__activeMatch)

    def selectedMatchId(self):
        """Get id of selected match."""
        return self.__selectedMatch

    def selectedMatchIdx(self):
        """Get index of selected match."""
        return self.__order.index(self.__selectedMatch)

    def getMatches(self):
        """Yield all matches."""
        for ident in self.__order:
            yield self.__matches[ident]

    def getMatchIDs(self):
        """Get match IDs."""
        return self.__order

    @classmethod
    def _uniqid(cls):
        return hex(int(time() * 10000000))[10:]

    def countMatches(self):
        """Return the number of matches."""
        return len(self.__matches)

    def updateOrder(self, toIdx, fromIdx):
        """Update the order of the matches."""
        self.__order[toIdx], self.__order[fromIdx] =\
            self.__order[fromIdx], self.__order[toIdx]

    def removeMatch(self, ident):
        """Remove a match."""
        index = self.__order.index(ident)
        self.__order.pop(index)
        try:
            self.__matches[ident].metaChanged.disconnect()
        except TypeError:
            pass
        try:
            self.__matches[ident].dataChanged.disconnect()
        except TypeError:
            pass
        self.__controller.logoManager.deleteMatch(ident)
        del self.__matches[ident]
        if ident == self.activeMatchId():
            new_index = index - 1 if index > 0 else 0
            # new_ident = self.__order[new_index]
            # self.activateMatch(new_ident)
            return new_index
