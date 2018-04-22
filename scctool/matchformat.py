"""Provide match formats."""

import logging

# create logger
module_logger = logging.getLogger('scctool.matchformat')


class MatchFormat(object):
    """Interface definition"""

    _name = ""

    def __init__(self, matchData):
        """Init match grabber."""
        self._matchData = matchData

    def applyFormat(self):
        raise UserWarning("Not implemented.")

    def getName(self):
        return self._name


class MatchFormatKoprulu(MatchFormat):
    """Interface definition"""

    _name = "Koprulu Team League"

    def __init__(self, *args):
        """Init match grabber."""
        super().__init__(*args)
        self._url = "http://koprululeague.forumactif.org"

    def applyFormat(self):
        self._matchData.setCustom(7, True, False)
        self._matchData.setMinSets(4)
        self._matchData.setURL(self._url)
        self._matchData.setLeague(self._name)
        self._matchData.writeJsonFile()


class MatchFormatWardi(MatchFormat):
    """Interface definition"""

    _name = "WardiTV Team League Season 8"

    def __init__(self, *args):
        """Init match grabber."""
        super().__init__(*args)
        self._url = "http://liquipedia.net/starcraft2/WardiTV_Team_League_S8"

    def applyFormat(self):
        self._matchData.setCustom(7, True, False)
        self._matchData.setMinSets(4)
        self._matchData.setURL(self._url)
        self._matchData.setLeague(self._name)
        self._matchData.writeJsonFile()


class MatchFormatAllInTheNydus(MatchFormat):
    """Interface definition"""

    _name = "All-In TheNydus"

    def __init__(self, *args):
        """Init match grabber."""
        super().__init__(*args)
        self._url = "https://sites.google.com/site/allinthenydus"

    def applyFormat(self):
        self._matchData.setCustom(7, True, False)
        self._matchData.setMinSets(4)
        self._matchData.setURL(self._url)
        self._matchData.setLeague(self._name)
        self._matchData.writeJsonFile()


class MatchFormatVSL(MatchFormat):
    """Interface definition"""

    _name = "Validity Star League"

    def __init__(self, *args):
        """Init match grabber."""
        super().__init__(*args)
        self._url = "http://liquipedia.net/starcraft2/Validity_Star_League"

    def applyFormat(self):
        self._matchData.setCustom(7, True, False)
        self._matchData.setMinSets(4)
        self._matchData.setURL(self._url)
        self._matchData.setLeague(self._name)
        self._matchData.writeJsonFile()


class MatchFormatChobo(MatchFormat):
    """Interface definition"""

    _name = "Chobo Team League"

    def __init__(self, *args):
        """Init match grabber."""
        super().__init__(*args)
        self._url = "http://www.choboteamleague.com"

    def applyFormat(self):
        self._matchData.setCustom(8, False, False)
        self._matchData.setMinSets(8)
        self._matchData.setURL(self._url)
        self._matchData.setLeague(self._name)
        self._matchData.writeJsonFile()
