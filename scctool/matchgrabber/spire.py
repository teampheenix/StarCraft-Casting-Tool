"""Provide match grabber for Spire.gg."""
import json
import logging
from datetime import datetime

import scctool.settings
import scctool.settings.translation
from scctool.matchgrabber.custom import MatchGrabber as MatchGrabberParent
import re
from _datetime import timedelta, timezone

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

    def grabData(self, metaChange=False, logoManager=None):
        """Grab match data."""
        data = self._getJson()

        if(data['code'] != "ok"):
            msg = 'API-Error: ' + data['code']
            raise ValueError(msg)
        else:
            self._rawData = data.get('result', {})
            setsLimits = self._rawData.get('setsLimits', {})
            overwrite = (metaChange
                         or self._matchData.getURL().strip()
                         != self.getURL().strip())
            with self._matchData.emitLock(overwrite,
                                          self._matchData.metaChanged):
                self._setMatchFormat(setsLimits, overwrite)
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

                for idx, mapData in enumerate(self._rawData.get('maps', [])):
                    mapname = mapData.get('name')
                    self._matchData.setMap(idx, mapname)

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

                    for set_idx, player in enumerate(self._rawData['lineups'][team_label].get('lineup', [])):
                        name = self._aliasPlayer(
                            player.get('name', 'TBD'))
                        race = json.loads(player.get('playerJson')).get('race')
                        if self._format == 'CHINESE':
                            self._matchData.setPlayer(
                                self._matchData.getSwappedIdx(team_idx),
                                set_idx*2,
                                name,
                                race)
                            self._matchData.setPlayer(
                                self._matchData.getSwappedIdx(team_idx),
                                set_idx*2+1,
                                name,
                                race)
                        else:
                            self._matchData.setPlayer(
                                self._matchData.getSwappedIdx(team_idx),
                                set_idx,
                                name,
                                'Random')

                # TODO: Set score

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

    def _setMatchFormat(self, setsLimits, overwrite):
        self._format = setsLimits.get('format', '')
        re_proleague = re.compile(r'^PROLEAGUE_(\d+)$')
        re_chinese = re.compile(r'^CHINESE_(\d+)$')
        re_allkill = re.compile(r'^ALLKILL_(\d+)$')
        if (match := re_chinese.match(self._format)) is not None:
            sets = int(match.group(1))
            self._format = 'CHINESE'
            self._matchData.setNoSets(sets + 1, 1, resetPlayers=overwrite)
            self._matchData.setMinSets(setsLimits.get('maxWins', sets))
            self._matchData.setAllKill(False)
            self._matchData.setSolo(False)
            self._matchData.setNoVetoes(0)
        elif (match := re_proleague.match(self._format)) is not None:
            sets = int(match.group(1))
            self._format = 'PROLEAGUE'
            self._matchData.setNoSets(
                sets + 1, 1, resetPlayers=overwrite)
            self._matchData.setMinSets(setsLimits.get('maxWins', int(sets/2)))
            self._matchData.setAllKill(False)
            self._matchData.setSolo(False)
            self._matchData.setNoVetoes(0)
        elif (match := re_proleague.match(self._format)) is not None:
            sets = int(match.group(1))
            self._format = 'ALLKILL'
            self._matchData.setNoSets(
                sets + 1, 0, resetPlayers=overwrite)
            self._matchData.setMinSets(setsLimits.get('maxWins', int(sets/2)))
            self._matchData.setAllKill(True)
            self._matchData.setSolo(False)
            self._matchData.setNoVetoes(0)
        else:
            self._format = None
            raise ValueError('Unknown Format')

            self._matchData.resetLabels()

    def updateCountdown(self, datetime_str):
        """Set countdown to datetime of the match."""
        if not datetime_str or not scctool.settings.config.parser.getboolean(
                "Countdown", "matchgrabber_update"):
            return
        dt_obj = datetime.fromisoformat(datetime_str)
        dt_obj = dt_obj.replace(tzinfo=timezone(timedelta(hours=0)))
        dt_obj = dt_obj.astimezone()
        self._controller.view.countdownTab.setFromTimestamp(dt_obj.timestamp())
