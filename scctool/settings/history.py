"""Provide history manager for SCCTool."""
import logging
import json

from scctool.settings import history_json_file, race2idx, idx2race

module_logger = logging.getLogger(
    'scctool.settings.history')  # create logger


class HistoryManager:

    __max_length = 100

    def __init__(self):
        self.loadJson()

    def loadJson(self):
        """Read json data from file."""
        try:
            with open(history_json_file, 'r', encoding='utf-8-sig') as json_file:
                data = json.load(json_file)
        except Exception as e:
            data = dict()

        self.__player_history = data.get('player', [])

    def dumpJson(self):
        """Write json data to file."""
        data = dict()
        data['player'] = self.__player_history
        try:
            with open(history_json_file, 'w', encoding='utf-8-sig') as outfile:
                json.dump(data, outfile)
        except Exception as e:
            module_logger.exception("message")

    def insertPlayer(self, player, race):
        player = player.strip()
        if not player or player.lower() == "tbd":
            return
        if race is str:
            race = race2idx(race)
        race = idx2race(race)
        for item in self.__player_history:
            if item.get('player', '') == player:
                self.__player_history.remove(item)
                if race == "Random":
                    race = item.get('race', 'Random')
                break
        self.__player_history.insert(0, {"player": player, "race": race})
        self.enforeMaxLength()

    def enforeMaxLength(self):
        while len(self.__player_history) > self.__max_length:
            self.__player_history.pop()

    def getPlayerList(self):
        playerList = list()
        for item in self.__player_history:
            player = item['player']
            if player not in playerList:
                playerList.append(player)
        return playerList
        
    def getRace(self, player):
        player = player.lower().strip()
        race = "Random"
        for item in self.__player_history:
            if item.get('player', '').lower() == player:
                race = item.get('race', 'Random')
                break
        return race