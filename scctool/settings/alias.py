"""Provide alias manager for SCCTool."""
import json
import logging

from scctool.settings import getJsonFile

module_logger = logging.getLogger(__name__)


class AliasManager:

    def __init__(self):
        self.loadJson()

    def loadJson(self):
        """Read json data from file."""
        try:
            with open(getJsonFile('alias'), 'r',
                      encoding='utf-8-sig') as json_file:
                data = json.load(json_file)
        except Exception as e:
            data = dict()

        self.__player_alias = data.get('player', dict())
        self.__team_alias = data.get('team', dict())

        if not isinstance(self.__player_alias, dict):
            self.__team_alias = dict()

        if not isinstance(self.__player_alias, dict):
            self.__team_alias = dict()

    def dumpJson(self):
        """Write json data to file."""
        data = dict()
        data['player'] = self.__player_alias
        data['team'] = self.__team_alias
        try:
            with open(getJsonFile('alias'), 'w',
                      encoding='utf-8-sig') as outfile:
                json.dump(data, outfile)
        except Exception as e:
            module_logger.exception("message")

    def addPlayerAlias(self, name, alias):
        name = str(name).strip()
        alias = str(alias).strip()
        if not name or name.lower() == 'tbd':
            raise ValueError('Invalid player name.')
        if not alias or alias.lower() == 'tbd':
            raise ValueError('Invalid alias name.')
        if name == alias:
            raise ValueError('Alias matches name.')

        if alias in self.__player_alias:
            raise ValueError('Alias {} is already used by {}'.format(
                alias, self.__player_alias[alias]))
        self.__player_alias[alias] = name

    def addTeamAlias(self, name, alias):
        name = str(name).strip()
        alias = str(alias).strip()
        if not name or name.lower() == 'tbd':
            raise ValueError('Invalid team name.')
        if not alias or alias.lower() == 'tbd':
            raise ValueError('Invalid alias name.')
        if name == alias:
            raise ValueError('Alias matches name.')

        if alias in self.__team_alias:
            raise ValueError('Alias {} is already used by {}'.format(
                alias, self.__team_alias[alias]))
        self.__team_alias[alias] = name

    def removePlayerAlias(self, name, alias):
        name = str(name).strip()
        alias = str(alias).strip()

        try:
            if self.__player_alias[alias] == name:
                del self.__player_alias[alias]
        except KeyError:
            pass

    def removeTeamAlias(self, name, alias):
        name = str(name).strip()
        alias = str(alias).strip()

        try:
            if self.__team_alias[alias] == name:
                del self.__team_alias[alias]
        except KeyError:
            pass

    def translatePlayer(self, name):
        name = str(name).strip()
        return self.__player_alias.get(name, name)

    def translateTeam(self, name):
        name = str(name).strip()
        return self.__team_alias.get(name, name)

    def playerAliasList(self):
        list = dict()
        for alias, player in self.__player_alias.items():
            if player not in list.keys():
                list[player] = []
            list[player].append(alias)
        return list

    def teamAliasList(self):
        list = dict()
        for alias, player in self.__team_alias.items():
            if player not in list.keys():
                list[player] = []
            list[player].append(alias)
        return list
