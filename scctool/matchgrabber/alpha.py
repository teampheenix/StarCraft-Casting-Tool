"""Provide match grabber for AlphaTL."""

import logging
import scctool.settings

import os
from urllib.request import urlretrieve
from scctool.matchgrabber.custom import MatchGrabber as MatchGrabberParent

# create logger
module_logger = logging.getLogger('scctool.matchgrabber.alpha')


class MatchGrabber(MatchGrabberParent):
    """Grabs match data from Alpha SC2 Teamleague."""

    def __init__(self, *args):
        """Init match grabber."""
        super(MatchGrabber, self).__init__(*args)
        self._provider = "AlphaSC2"
        self._urlprefix = "http://alpha.tl/match/"
        self._apiprefix = "http://alpha.tl/api?match="

    def grabData(self):
        """Grab match data."""
        data = self._getJson()

        if(data['code'] != 200):
            msg = 'API-Error: ' + data['error']
            raise ValueError(msg)
        else:
            self._rawData = data
            self._matchData.setURL(self.getURL())
            self._matchData.setNoSets(5, resetPlayers=True)
            self._matchData.setMinSets(3)
            self._matchData.setSolo(False)
            self._matchData.resetLabels()
            league = data['tournament']
            if not isinstance(league, str):
                league = "TBD"
            league = league.replace('Non-pro', 'Non-Pro')
            self._matchData.setLeague(league)

            for idx, map in enumerate(data['maps']):
                if not isinstance(map, str):
                    map = "TBD"
                self._matchData.setMap(idx, map)

            self._matchData.setLabel(4, "Ace Map")

            for team_idx in range(2):
                for set_idx, player in enumerate(data['lineup' +
                                                      str(team_idx + 1)]):
                    try:
                        playername = player['nickname']
                        if not isinstance(playername, str):
                            playername = "TBD"
                        self._matchData.setPlayer(
                            team_idx, set_idx, playername, str(player['race']))
                    except Exception:
                        self._matchData.setPlayer(
                            team_idx, set_idx, 'TBD', 'Random')

                team = data['team' + str(team_idx + 1)]
                name, tag = team['name'], team['tag']
                if not isinstance(name, str):
                    name = "TBD"
                if not isinstance(tag, str):
                    tag = ""
                self._matchData.setTeam(team_idx, name, tag)

            for set_idx in range(5):
                try:
                    score = int(data['games'][set_idx]) * 2 - 3
                except Exception:
                    score = 0

                self._matchData.setMapScore(set_idx, score)

            self._matchData.setAllKill(False)

    def downloadLogos(self):
        """Download team logos."""
        dir = scctool.settings.OBSdataDir
        if self._rawData is None:
            raise ValueError(
                "Error: No raw data.")

        for idx in range(2):
            try:
                os.remove(scctool.settings.getAbsPath(
                    dir + "/logo" + str(idx + 1) + ".png"))
            except Exception:
                pass
            try:
                os.remove(scctool.settings.getAbsPath(
                    dir + "/logo" + str(idx + 1) + ".jpg"))
            except Exception:
                pass
            try:
                url = self._rawData['team' + str(idx + 1)]['logo']
                base, ext = os.path.splitext(url)
                ext = ext.split("?")[0].lower()
                fname = dir + "/logo" + str(idx + 1) + ext
                urlretrieve(url, scctool.settings.getAbsPath(fname))

                self._controller.ftpUploader.cwd(dir)
                self._controller.ftpUploader.upload(
                    fname,
                    "logo" + str(idx + 1) + ext)
                self._controller.ftpUploader.cwd("..")
            except Exception as e:
                module_logger.exception("message")

    def downloadBanner(self):
        """Download team logos."""
        dir = scctool.settings.OBSdataDir
        transparent = scctool.settings.config.parser.getboolean(
            "SCT", "transparent_match_banner")

        if self._rawData is None:
            raise ValueError(
                "Error: No raw data.")

        fname = dir + "/matchbanner.png"
        url = "http://alpha.tl/announcement/"\
            + str(self.getID())

        if transparent:
            url = url + "?transparent"
        else:
            url = url + "?vs"

        try:
            urlretrieve(url, scctool.settings.getAbsPath(fname))

            self._controller.ftpUploader.cwd(dir)
            self._controller.ftpUploader.upload(fname, "matchbanner.png")
            self._controller.ftpUploader.cwd("..")
        except Exception as e:
            module_logger.exception("message")
