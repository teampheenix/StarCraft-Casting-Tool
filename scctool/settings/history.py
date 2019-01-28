"""Provide history manager for SCCTool."""
import json
import logging

import scctool.settings.translation
from scctool.settings import getJsonFile, idx2race, race2idx

module_logger = logging.getLogger(__name__)
_ = scctool.settings.translation.gettext


class HistoryManager:
    """History manager for SCCTool."""

    __max_length = 100

    def __init__(self):
        """Init the history manager."""
        self.loadJson()
        self.updateDataStructure()

    def loadJson(self):
        """Read json data from file."""
        try:
            with open(getJsonFile('history'), 'r',
                      encoding='utf-8-sig') as json_file:
                data = json.load(json_file)
        except Exception:
            data = dict()

        self.__player_history = data.get('player', [])
        self.__team_history = data.get('team', [])

    def dumpJson(self):
        """Write json data to file."""
        data = dict()
        data['player'] = self.__player_history
        data['team'] = self.__team_history
        try:
            with open(getJsonFile('history'), 'w',
                      encoding='utf-8-sig') as outfile:
                json.dump(data, outfile)
        except Exception:
            module_logger.exception("message")

    def updateDataStructure(self):
        """Update the data structure (from a previous version)."""
        for idx, item in enumerate(self.__team_history):
            if isinstance(item, str):
                self.__team_history[idx] = {'team': item, 'logo': '0'}

    def insertPlayer(self, player, race):
        """Insert a player into the history."""
        player = player.strip()
        if not player or player.lower() == "tbd":
            return
        if race is str:
            race = race2idx(race)
        race = idx2race(race)
        for item in self.__player_history:
            if item.get('player', '').lower() == player.lower():
                self.__player_history.remove(item)
                if race == "Random":
                    race = item.get('race', 'Random')
                break
        self.__player_history.insert(0, {"player": player, "race": race})
        # self.enforeMaxLength("player")

    def insertTeam(self, team, logo='0'):
        """Insert a team into the history."""
        team = team.strip()
        if not team or team.lower() == "tbd":
            return
        for item in self.__team_history:
            if item.get('team', '').lower() == team.lower():
                self.__team_history.remove(item)
                if logo == '0':
                    logo = item.get('logo', '0')
                break
        self.__team_history.insert(0, {"team": team, "logo": logo})
        # self.enforeMaxLength("team")

    def enforeMaxLength(self, scope=None):
        """Delete old history elements."""
        if not scope or scope == "player":
            while len(self.__player_history) > self.__max_length:
                self.__player_history.pop()
        if not scope or scope == "team":
            while len(self.__team_history) > self.__max_length:
                self.__team_history.pop()

    def getPlayerList(self):
        """Return a list of all players in history."""
        playerList = list()
        for item in self.__player_history:
            player = item['player']
            if player not in playerList:
                playerList.append(player)
        return playerList

    def getTeamList(self):
        """Return a list of all teams in history."""
        teamList = list()
        for item in self.__team_history:
            team = item.get('team')
            if team not in teamList:
                teamList.append(team)
        return teamList

    def getRace(self, player):
        """Look up the race of a player in the history."""
        player = player.lower().strip()
        race = "Random"
        for item in self.__player_history:
            if item.get('player', '').lower() == player:
                race = item.get('race', 'Random')
                break
        return race

    def getLogo(self, team):
        """Look up the logo of a team in history."""
        team = team.lower().strip()
        logo = '0'
        for item in self.__team_history:
            if item.get('team', '').lower() == team:
                logo = item.get('logo', '0')
                break
        return logo
