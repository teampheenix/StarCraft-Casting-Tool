"""Provide match grabber for AlphaTL."""

import logging
import os
import scctool.settings

from urllib.request import urlretrieve
from scctool.matchgrabber.custom import MatchGrabber as MatchGrabberParent

# create logger
module_logger = logging.getLogger('scctool.matchgrabber.rstl')


class MatchGrabber(MatchGrabberParent):
    """Grabs match data from Russian StarCraft 2 Teamleague."""

    def __init__(self, *args):
        """Init match grabber."""
        super(MatchGrabber, self).__init__(*args)
        self._provider = "RSTL"
        self._urlprefix = \
            "http://hdgame.net/en/tournaments/list/tournament"\
            + "/rstl-12/tmenu/tmatches/?match="
        self._apiprefix = \
            "http://hdgame.net/index.php?ajax=1&do=tournament&act=api"\
            + "&data_type=json&lang=en&service=match&match_id="

    def grabData(self):
        """Grab match data."""
        data = self._getJson()
        if(data['code'] != "200"):
            msg = 'API-Error: ' + data['code']
            raise ValueError(msg)

        data = data['data']
        self._rawData = data

        if(data['game_format'] == "3"):
            self._matchData.setNoSets(7, 6, resetPlayers=True)
            self._matchData.setMinSets(4)
            self._matchData.setLeague(data['tournament']['name'])

            for set_idx in range(7):
                self._matchData.setMap(
                    set_idx, data['start_maps'][str(set_idx)]['name'])

            for team_idx in range(2):
                for set_idx in range(4):
                    try:
                        lu = 'lu' + str(team_idx + 1)
                        self._matchData.setPlayer(
                            team_idx, set_idx,
                            data[lu][str(set_idx)]['member_name'],
                            data[lu][str(set_idx)]['r_name'])
                    except:
                        pass

                for set_idx in range(4, 7):
                    try:
                        idx = str(4 + set_idx)
                        if(not data['result'][idx]['r_name'
                                                   + str(team_idx + 1)]):
                            try:
                                idx = str(4 + set_idx)
                                race = data['result'][idx]['r_name' +
                                                           str(team_idx + 1)]
                            except:
                                race = "Random"
                        else:
                            race = data['result'][str(
                                4 + set_idx)]['r_name' + str(team_idx + 1)]
                        player = data['result'][str(
                            4 + set_idx)]['tu_name' + str(team_idx + 1)]
                        self._matchData.setPlayer(team_idx, set_idx,
                                                  player, race)
                    except:
                        pass

                team = data['member' + str(team_idx + 1)]
                self._matchData.setTeam(team_idx, team['name'], team['tag'])

            self._matchData.setLabel(4, "Ace Map 1")
            self._matchData.setLabel(5, "Ace Map 2")
            self._matchData.setLabel(6, "Ace Map 3")

            for set_idx in range(4):
                try:
                    score1 = int(
                        data['result'][str(set_idx * 2)]['score1'])
                    score2 = int(
                        data['result'][str(set_idx * 2)]['score2'])
                except:
                    score1 = 0
                    score2 = 0

                if(score1 > score2):
                    score = -1
                elif(score1 < score2):
                    score = 1
                else:
                    score = 0

                self._matchData.setMapScore(set_idx, score)

            for set_idx in range(4, 7):
                try:
                    score1 = int(
                        data['result'][str(4 + set_idx)]['score1'])
                    score2 = int(
                        data['result'][str(4 + set_idx)]['score2'])
                except:
                    score1 = 0
                    score2 = 0

                if(score1 > score2):
                    score = -1
                elif(score1 < score2):
                    score = 1
                else:
                    score = 0
                self._matchData.setMapScore(set_idx, score)

            self._matchData.setAllKill(False)

        elif(data['game_format'] == "2"):  # All-Kill BoX

            self._matchData.resetData()
            bo = int(data['game_format_bo'])
            self._matchData.setNoSets(bo, bo, resetPlayers=True)
            self._matchData.setMinSets(0)
            self._matchData.setLeague(data['tournament']['name'])

            for set_idx in range(1):
                self._matchData.setMap(
                    set_idx, data['start_maps'][str(set_idx)]['name'])

            for team_idx in range(2):
                for set_idx in range(1):
                    try:
                        lu = 'lu' + str(team_idx + 1)
                        self._matchData.setPlayer(
                            team_idx, set_idx,
                            data[lu][str(set_idx)]['member_name'],
                            data[lu][str(set_idx)]['r_name'])
                    except:
                        pass

                for set_idx in range(1, bo):
                    try:
                        idx = str(set_idx * 2)
                        if(not data['result'][idx]['r_name' +
                                                   str(team_idx + 1)]):
                            try:
                                idx = str(set_idx * 2 + 1)
                                race = data['result'][idx]['r_name'
                                                           + str(team_idx + 1)]
                            except:
                                race = "Random"
                        else:
                            race = data['result'][str(
                                set_idx * 2)]['r_name' + str(team_idx + 1)]
                        player = data['result'][str(
                            set_idx * 2)]['member_name' + str(team_idx + 1)]
                        self._matchData.setPlayer(team_idx, set_idx,
                                                  player, race)
                    except:
                        pass

                team = data['member' + str(team_idx + 1)]
                self._matchData.setTeam(team_idx, team['name'], team['tag'])

            for set_idx in range(bo):
                try:
                    score1 = int(
                        data['result'][str(set_idx * 2)]['score1'])
                    score2 = int(
                        data['result'][str(set_idx * 2)]['score2'])
                except:
                    score1 = 0
                    score2 = 0

                if(score1 > score2):
                    score = -1
                elif(score1 < score2):
                    score = 1
                else:
                    score = 0

                self._matchData.setMapScore(set_idx, score)
                self._matchData.resetLabels()

            self._matchData.setAllKill(True)
        else:
            module_logger.info("RSTL Format Unkown")

    def downloadLogos(self):
        """Download team logos."""
        dir = scctool.settings.OBSdataDir

        if self._rawData is None:
            raise ValueError(
                "Error: No raw data.")

        for i in range(1, 3):
            try:
                os.remove(scctool.settings.getAbsPath(
                    dir + "/logo" + str(i) + ".png"))
            except:
                pass
            try:
                os.remove(scctool.settings.getAbsPath(
                    dir + "/logo" + str(i) + ".jpg"))
            except:
                pass

            url = "http://hdgame.net" + \
                self._rawData['member' + str(i)]['img_m']
            base, ext = os.path.splitext(url)
            ext = ext.split("?")[0]
            fname = dir + "/logo" + str(i) + ext
            urlretrieve(url, fname)
            self._controller.ftpUploader.cwd(dir)
            self._controller.ftpUploader.upload(fname, "logo" + str(i) + ext)
            self._controller.ftpUploader.cwd("..")
