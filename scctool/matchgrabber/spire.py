"""Provide match grabber for Spire.gg."""
import json
import logging
import re
from datetime import datetime, timedelta, timezone

import requests
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
                self._matchData.setLeague(self._aliasLeague(league))

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
                            set_list = [set_idx*2, set_idx*2+1]
                        elif self._format == 'BESTOF':
                            set_list = list(range(self._matchData.getNoSets()))
                        else:
                            set_list = [set_idx]
                        for index in set_list:
                            self._matchData.setPlayer(
                                self._matchData.getSwappedIdx(team_idx),
                                index,
                                name,
                                race)
                    ace_players = self.getAcePlayers()
                    if len(ace_players) == 2:
                        for team_idx, player in enumerate(ace_players):
                            self._matchData.setPlayer(
                                self._matchData.getSwappedIdx(team_idx),
                                self._matchData.getNoSets() - 1,
                                player['name'],
                                player['race'])

                # TODO: Set score
                self.getResults()

                self._matchData.autoSetMyTeam(
                    swap=scctool.settings.config.parser.getboolean(
                        "SCT", "swap_myteam"))
                if logoManager is not None:
                    self.downloadLogos(logoManager)

    def getResults(self, overwrite=True):
        sets = requests.get(
            url=f'{self._getAPI()}/sets').json().get('result', [])
        if len(sets) < 1:
            for set_idx in range(self._matchData.getNoSets()):
                self._matchData.setMapScore(
                    set_idx, 0, overwrite, True)
            return
        for set_idx, data in enumerate(sets):
            winForTeamA = data.get('resultsMap', {}).get('A', '')
            if winForTeamA == 'WIN':
                score = -1
            elif winForTeamA == 'DEFEAT':
                score = 1
            else:
                score = 0
            self._matchData.setMapScore(set_idx, score, overwrite, True)

    def getAcePlayers(self):
        players = []
        try:
            data = requests.get(
                url=f'{self._getAPI()}/acePlayers').json().get('result', {})
            for team_idx in ['A', 'B']:
                if team_idx in data:
                    players.append({
                        'name': data[team_idx]['account']['props']['nickName'],
                        'race': data[team_idx]['account']['props']['race']
                    })
        except Exception:
            module_logger.exception('message')
        return players

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
        re_allkill = re.compile(r'^ALLKILL_BO(\d+)$')
        re_bestof = re.compile(r'^BESTOF_(\d+)$')
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
        elif (match := re_allkill.match(self._format)) is not None:
            sets = int(match.group(1))
            self._format = 'ALLKILL'
            self._matchData.setNoSets(
                sets, 0, resetPlayers=overwrite)
            self._matchData.setMinSets(
                setsLimits.get('maxWins', int(sets/2) + 1))
            self._matchData.setAllKill(True)
            self._matchData.setSolo(False)
            self._matchData.setNoVetoes(0)
        elif (match := re_bestof.match(self._format)) is not None:
            sets = int(match.group(1))
            self._format = 'BESTOF'
            self._matchData.setNoSets(
                sets, 0, resetPlayers=overwrite)
            self._matchData.setMinSets(
                setsLimits.get('maxWins', int(sets/2) + 1))
            self._matchData.setAllKill(False)
            self._matchData.setSolo(True)
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
