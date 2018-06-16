"""Provide match formats."""

import logging

# create logger
module_logger = logging.getLogger('scctool.matchformat')


class MatchFormat(object):
    """Interface definition"""

    _name = ""
    _icon = ""

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
    _icon = "koprulu_league.png"

    def __init__(self, *args):
        """Init match grabber."""
        super().__init__(*args)
        self._url = "http://koprulu-league.fr.nf"

    def applyFormat(self):
        self._matchData.setCustom(7, True, False)
        self._matchData.setMinSets(4)
        self._matchData.setURL(self._url)
        self._matchData.setLeague(self._name)
        self._matchData.writeJsonFile()


class MatchFormatWardi(MatchFormat):
    """Interface definition"""

    _name = "WardiTV Team League Season 8"
    _icon = "wardi.ico"

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


class MatchFormatPsi(MatchFormat):
    """Interface definition"""

    _name = "PSISTORM Gaming Team League"
    _icon = "psistorm.jpg"

    def __init__(self, *args):
        """Init match grabber."""
        super().__init__(*args)
        self._url = "http://liquipedia.net/starcraft2" + \
            "PSISTORM_Gaming_Team_League"

    def applyFormat(self):
        self._matchData.setCustom(5, False, False)
        self._matchData.setMinSets(5)
        self._matchData.setURL(self._url)
        self._matchData.setLeague(self._name)
        self._matchData.writeJsonFile()


class MatchFormatAllInTheNydus(MatchFormat):
    """Interface definition"""

    _name = "All-In TheNydus"
    _icon = "nydus.ico"

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


class MatchFormatVTL(MatchFormat):
    """Interface definition"""

    _name = "Validity Team League"
    _icon = "VTL.png"

    def __init__(self, *args):
        """Init match grabber."""
        super().__init__(*args)
        self._url = "https://liquipedia.net/starcraft2/Validity_Team_League"

    def applyFormat(self):
        self._matchData.setCustom(7, True, False)
        self._matchData.setMinSets(4)
        self._matchData.setURL(self._url)
        self._matchData.setLeague(self._name)
        self._matchData.writeJsonFile()


class MatchFormatChobo(MatchFormat):
    """Interface definition"""

    _name = "Chobo Team League"
    _icon = "chobo.png"

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
