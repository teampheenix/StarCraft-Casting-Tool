"""Provide match grabber for Spire.gg."""
import json
import logging
from datetime import datetime, timedelta, timezone
from urllib.request import urlopen, urlretrieve

import scctool.settings
import scctool.settings.translation
from scctool.matchgrabber.custom import MatchGrabber as MatchGrabberParent

# create logger
module_logger = logging.getLogger(__name__)
_ = scctool.settings.translation.gettext


class MatchGrabber(MatchGrabberParent):
    """Grabs match data from spire.gg."""

    _provider = "spiregg"

    def __init__(self, *args):
        """Init match grabber."""
        super().__init__(*args)
        self._urlprefix = "https://spire.gg/match/"
        self._apiprefix = "https://api.spire.gg/matches/"

    def updateCountdown(self, datetime_str):
        if not datetime_str or not scctool.settings.config.parser.getboolean(
                "Countdown", "matchgrabber_update"):
            return
        dt_obj = datetime.fromisoformat(datetime_str)
        self._controller.view.countdownTab.setFromTimestamp(dt_obj.timestamp())

    def grabData(self, metaChange=False, logoManager=None):
        """Grab match data."""
        data = self._getJson()

        if(data['code'] != "ok"):
            msg = 'API-Error: ' + data['code']
            raise ValueError(msg)
        else:
            self._rawData = data.get('result', {})
            try:
                matchFormat = json.loads(self._rawData.get(
                    'tournamentStage', {}).get('setsLimitsJson', ''))
            except AttributeError:
                matchFormat = {}
            overwrite = (metaChange
                         or self._matchData.getURL().strip()
                         != self.getURL().strip())
            with self._matchData.emitLock(overwrite,
                                          self._matchData.metaChanged):
                self._setMatchFormat(matchFormat, overwrite)
                self._matchData.resetLabels()
                if overwrite:
                    self._matchData.resetSwap()
                self.updateCountdown(self._rawData.get('datetime', ''))
                tournament = self._rawData['tournament']
                if tournament:
                    league = tournament.get('name', '')
                else:
                    league = f'Spire.gg {self._rawData.get("type", "")}'
                if not isinstance(league, str):
                    league = "TBD"
                self._matchData.setLeague(league)

                # TODO: Set maps

                for team_idx, team_label in {0: 'A', 1: 'B'}.items():
                    name = self._rawData['lineups'][team_label]['name']
                    tag = ''
                    if not isinstance(name, str):
                        name = "TBD"
                    if not isinstance(tag, str):
                        tag = ""
                    self._matchData.setTeam(
                        self._matchData.getSwappedIdx(team_idx),
                        self._aliasTeam(name), tag)

                # TODO: Set map scores, maps and lineup

                self._matchData.autoSetMyTeam(
                    swap=scctool.settings.config.parser.getboolean(
                        "SCT", "swap_myteam"))
                if logoManager is not None:
                    self.downloadLogos(logoManager)

    def downloadLogos(self, logoManager):
        """Download team logos."""
        if self._rawData is None:
            raise ValueError(
                "Error: No raw data.")

        for idx, team_label in {0: 'A', 1: 'B'}.items():
            try:
                logo_idx = self._matchData.getSwappedIdx(idx) + 1
                oldLogo = logoManager.getTeam(logo_idx)
                logo = logoManager.newLogo()
                url = self._rawData['lineups'][team_label]['avatar']
                if url:
                    new_logo = logo.fromURL(url,
                                            localFile=oldLogo.getAbsFile())
                    if new_logo:
                        logoManager.setTeamLogo(logo_idx, logo)
                    else:
                        module_logger.info("Logo download is not needed.")

            except Exception:
                module_logger.exception("message")

    def _setMatchFormat(self, format_data, overwrite):
        if format_data.get('format', '') == 'CHINESE_6':
            self._matchData.setNoSets(7, 1, resetPlayers=overwrite)
            self._matchData.setMinSets(format_data.get('maxWins', 6))
            self._matchData.setAllKill(False)
            self._matchData.setSolo(False)
            self._matchData.setNoVetoes(0)
        else:
            raise ValueError('Unknown Format')
