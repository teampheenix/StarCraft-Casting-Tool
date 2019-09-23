"""Provide match formats."""
import logging

import scctool.settings.translation

# create logger
module_logger = logging.getLogger(__name__)

_ = scctool.settings.translation.gettext


class MatchFormat(object):
    """Interface definition."""

    _name = ""
    _icon = ""

    def __init__(self, matchData):
        """Init match grabber."""
        self._matchData = matchData

    def applyFormat(self):
        """Apply format."""
        raise UserWarning("Not implemented.")

    def getName(self):
        """Return the name."""
        return self._name


class MatchFormatKoprulu(MatchFormat):
    """Interface definition."""

    _name = "Koprulu Team League"
    _icon = "koprulu_league.png"

    def __init__(self, *args):
        """Init match grabber."""
        super().__init__(*args)
        self._url = "http://koprulu-league.fr.nf"

    def applyFormat(self):
        """Apply format."""
        # Very old format:
        # self._matchData.setCustom(5, False, False)
        # self._matchData.setLabel(4, "Ace Map")
        # self._matchData.setAce(4, True)
        # self._matchData.setMinSets(3)
        # Old format:
        #self._matchData.setCustom(7, True, False)
        #self._matchData.setMinSets(4)
        self._matchData.setCustom(7, False, False, ace_sets=1)
        self._matchData.setMinSets(6)
        self._matchData.setURL(self._url)
        self._matchData.setLeague(self._name)
        self._matchData.writeJsonFile()


class MatchFormatWardi(MatchFormat):
    """Interface definition."""

    _name = "WardiTV Team League Season 8"
    _icon = "wardi.ico"

    def __init__(self, *args):
        """Init match grabber."""
        super().__init__(*args)
        self._url = "http://liquipedia.net/starcraft2/WardiTV_Team_League_S8"

    def applyFormat(self):
        """Apply format."""
        self._matchData.setCustom(7, True, False)
        self._matchData.setMinSets(4)
        self._matchData.setURL(self._url)
        self._matchData.setLeague(self._name)
        self._matchData.writeJsonFile()


class MatchFormatPsi(MatchFormat):
    """Interface definition."""

    _name = "PSISTORM Gaming Team League"
    _icon = "psistorm.jpg"

    def __init__(self, *args):
        """Init match grabber."""
        super().__init__(*args)
        self._url = "http://liquipedia.net/starcraft2" + \
            "PSISTORM_Gaming_Team_League"

    def applyFormat(self):
        """Apply format."""
        self._matchData.setCustom(5, False, False)
        self._matchData.setMinSets(5)
        self._matchData.setURL(self._url)
        self._matchData.setLeague(self._name)
        self._matchData.writeJsonFile()


class MatchFormatAllInTheNydus(MatchFormat):
    """Interface definition."""

    _name = "All-In TheNydus"
    _icon = "nydus.ico"

    def __init__(self, *args):
        """Init match grabber."""
        super().__init__(*args)
        self._url = "https://sites.google.com/site/allinthenydus"

    def applyFormat(self):
        """Apply format."""
        self._matchData.setCustom(7, True, False)
        self._matchData.setMinSets(4)
        self._matchData.setURL(self._url)
        self._matchData.setLeague(self._name)
        self._matchData.writeJsonFile()


class MatchFormatVTL(MatchFormat):
    """Interface definition."""

    _name = "Validity Team League"
    _icon = "VTL.png"

    def __init__(self, *args):
        """Init match grabber."""
        super().__init__(*args)
        self._url = "https://liquipedia.net/starcraft2/Validity_Team_League"

    def applyFormat(self):
        """Apply format."""
        self._matchData.setCustom(7, True, False)
        self._matchData.setMinSets(4)
        self._matchData.setURL(self._url)
        self._matchData.setLeague(self._name)
        self._matchData.writeJsonFile()


class MatchFormatChobo(MatchFormat):
    """Interface definition."""

    _name = "Chobo Team League"
    _icon = "chobo.png"

    def __init__(self, *args):
        """Init match grabber."""
        super().__init__(*args)
        self._url = "http://www.choboteamleague.com"

    def applyFormat(self):
        """Apply format."""
        self._matchData.setCustom(7, False, False, 3)
        self._matchData.setMinSets(9)
        self._matchData.setURL(self._url)
        self._matchData.setLeague(self._name)
        self._matchData.writeJsonFile()


class ProleagueFormat(MatchFormat):
    """Interface definition."""

    _name = "Proleague Format"
    _icon = "scct.ico"

    def __init__(self, *args):
        """Init match grabber."""
        super().__init__(*args)
        self._url = "https://github.com/teampheenix/StarCraft-Casting-Tool"

    def applyFormat(self):
        """Apply format."""
        self._matchData.setCustom(5, False, False, ace_sets=1)
        self._matchData.setMinSets(3)
        self._matchData.setURL(self._url)
        self._matchData.setLeague(self._name)
        self._matchData.writeJsonFile()


class ChineseFormat(MatchFormat):
    """Interface definition."""

    _name = "Chinese Team Championship"
    _icon = "scct.ico"

    def __init__(self, *args):
        """Init match grabber."""
        super().__init__(*args)
        self._url = "https://github.com/teampheenix/StarCraft-Casting-Tool"

    def applyFormat(self):
        """Apply format."""
        self._matchData.setCustom(7, False, False, ace_sets=1)
        self._matchData.setMinSets(6)
        self._matchData.setURL(self._url)
        self._matchData.setLeague(self._name)
        self._matchData.writeJsonFile()


class MatchFormatESL(MatchFormat):
    """Interface definition."""

    _name = "ESL SC2 Open Team Tournament Spring 2019"
    _icon = "esl.png"

    def __init__(self, *args):
        """Init match grabber."""
        super().__init__(*args)
        self._url = ("https://play.eslgaming.com/starcraft/global/sc2/"
                     "open/all-kill-spring-2019/")

    def applyFormat(self):
        """Apply format."""
        self._matchData.setCustom(7, True, False)
        self._matchData.setMinSets(4)
        self._matchData.setURL(self._url)
        self._matchData.setLeague(self._name)
        self._matchData.writeJsonFile()
