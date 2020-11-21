"""Provide match grabber for AlphaTL."""
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
    """Grabs match data from Alpha SC2 Teamleague."""

    _provider = "AlphaSC2"

    def __init__(self, *args):
        """Init match grabber."""
        super().__init__(*args)
        self._urlprefix = "https://alpha.tl/match/"
        self._apiprefix = "https://alpha.tl/api?match="

    def updateCountdown(self, datetime_str):
        if not datetime_str or not scctool.settings.config.parser.getboolean(
                "Countdown", "matchgrabber_update"):
            return
        dt_obj = datetime.strptime(
            datetime_str, '%Y-%m-%d %H:%M:%S')
        dt_obj = dt_obj.replace(tzinfo=timezone(timedelta(hours=0)))
        dt_obj = dt_obj.astimezone()
        self._controller.view.countdownTab.setFromTimestamp(dt_obj.timestamp())

    def grabData(self, metaChange=False, logoManager=None):
        """Grab match data."""
        data = self._getJson()

        if(data['code'] != 200):
            msg = 'API-Error: ' + data['error']
            raise ValueError(msg)
        else:
            self._rawData = data
            overwrite = (metaChange
                         or self._matchData.getURL().strip()
                         != self.getURL().strip())
            with self._matchData.emitLock(overwrite,
                                          self._matchData.metaChanged):
                self._matchData.setNoSets(5, 1, resetPlayers=overwrite)
                self._matchData.setMinSets(3)
                self._matchData.setSolo(False)
                self._matchData.setNoVetoes(0)
                self._matchData.resetLabels()
                if overwrite:
                    self._matchData.resetSwap()
                self.updateCountdown(data.get('datetime', ''))
                league = data['tournament']
                if not isinstance(league, str):
                    league = "TBD"
                league = league.replace('Non-pro', 'Non-Pro')
                league = league.replace('Semi-pro', 'Semi-Pro')
                self._matchData.setLeague(
                    self._matchData.setLeague(self._aliasLeague(league)))

                for idx, mapname in enumerate(data['maps']):
                    if not isinstance(mapname, str):
                        mapname = "TBD"
                    self._matchData.setMap(idx, mapname)

                for team_idx in range(2):
                    for set_idx, player in enumerate(
                            data[f'lineup{team_idx + 1}']):
                        try:
                            playername = self._aliasPlayer(player['nickname'])
                            if not isinstance(playername, str):
                                playername = "TBD"
                            self._matchData.setPlayer(
                                self._matchData.getSwappedIdx(team_idx),
                                set_idx,
                                playername, str(player['race']))
                        except Exception:
                            self._matchData.setPlayer(
                                self._matchData.getSwappedIdx(team_idx),
                                set_idx, 'TBD', 'Random')

                    team = data[f'team{team_idx + 1}']
                    name, tag = team['name'], team['tag']
                    if not isinstance(name, str):
                        name = "TBD"
                    if not isinstance(tag, str):
                        tag = ""
                    self._matchData.setTeam(
                        self._matchData.getSwappedIdx(team_idx),
                        self._aliasTeam(name), tag)

                for set_idx in range(5):
                    try:
                        score = int(data['games'][set_idx]) * 2 - 3
                    except Exception:
                        score = 0

                    self._matchData.setMapScore(
                        set_idx, score, overwrite, True)

                self._matchData.setAllKill(False)
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

        for idx in range(2):
            try:
                logo_idx = self._matchData.getSwappedIdx(idx) + 1
                oldLogo = logoManager.getTeam(logo_idx)
                logo = logoManager.newLogo()
                url = self._rawData[f'team{idx + 1}']['logo']
                if url:
                    new_logo = logo.fromURL(
                        self._rawData[f'team{idx + 1}']['logo'],
                        localFile=oldLogo.getAbsFile())
                    if new_logo:
                        logoManager.setTeamLogo(logo_idx, logo)
                    else:
                        module_logger.info("Logo download is not needed.")

            except Exception:
                module_logger.exception("message")

    def downloadBanner(self):
        """Download team logos."""
        data_dir = scctool.settings.casting_data_dir
        transparent = scctool.settings.config.parser.getboolean(
            "SCT", "transparent_match_banner")

        if self._rawData is None:
            raise ValueError(
                "Error: No raw data.")

        fname = data_dir + "/matchbanner.png"
        url = "https://alpha.tl/announcement/"\
            + str(self.getID())

        if transparent:
            url = url + "?transparent"
        else:
            url = url + "?vs"

        localFile = scctool.settings.getAbsPath(fname)
        needs_download = True
        size = 1024 * 400
        try:
            with open(localFile, "rb") as in_file:
                local_byte = in_file.read(size)

            file = urlopen(url)
            data = file.read(size)

            if(data == local_byte):
                needs_download = False
        except FileNotFoundError:
            module_logger.warning("Match banner not found.")
        except Exception:
            module_logger.exception("message")

        if needs_download:
            try:
                urlretrieve(url, scctool.settings.getAbsPath(fname))

            except Exception:
                module_logger.exception("message")
        else:
            module_logger.info('No need to redownload match banner')
