"""Grab match data from websites."""

import logging

import requests

# create logger
module_logger = logging.getLogger(__name__)


class MatchGrabber(object):
    """Parent definition,i.e., for custom matchs."""

    _provider = "Custom"

    def __init__(self, matchData, controller, id=False):
        """Init match grabber."""
        self._id = 0
        self.setID(id)
        self._controller = controller
        self._matchData = matchData
        self._urlprefix = ""
        self._apiprefix = ""
        self._rawData = None

    def setID(self, id=False):
        """Set ID."""
        if id:
            self._id = int(id)

    def getID(self):
        """Get ID as int."""
        return int(self._id)

    def _getAPI(self, id=False):
        if id:
            self.setID(id)
        return self._apiprefix + str(self.getID())

    def getURL(self, id=False):
        """Get URL."""
        if id:
            self.setID(id)
        return self._urlprefix + str(self.getID())

    def getProvider(self):
        """Get name of the provider."""
        return self._provider

    def grabData(self, metaChange=False, logoManager=None):
        """Grab match data."""
        raise ValueError(
            "Error: Cannot grab data from this provider.")

    def _getJson(self):
        data = requests.get(url=self._getAPI()).json()
        return data

    def _aliasPlayer(self, player):
        return self._controller.aliasManager.translatePlayer(player)

    def _aliasTeam(self, player):
        return self._controller.aliasManager.translateTeam(player)

    def downloadLogos(self, logoManager):
        """Download logos."""
        raise UserWarning(
            "Error: Cannot download logos from this provider.")

    def downloadBanner(self):
        """Download Banner."""
        raise UserWarning(
            "Error: Cannot download a match banner from this provider.")
