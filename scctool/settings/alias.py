"""Provide alias manager for SCCTool."""
import json
import logging

import scctool.settings.translation
from scctool.settings import getJsonFile

module_logger = logging.getLogger(__name__)
_ = scctool.settings.translation.gettext


class AliasManager:
    """Alias manager for SCCTool."""

    def __init__(self):
        """Init the manager."""
        self.loadJson()

    def loadJson(self):
        """Read json data from file."""
        try:
            with open(getJsonFile('alias'), 'r',
                      encoding='utf-8-sig') as json_file:
                data = json.load(json_file)
        except Exception:
            data = dict()

        self.__player_alias = data.get('player', dict())
        self.__team_alias = data.get('team', dict())
        self.__league_alias = data.get('league', dict())

        if not isinstance(self.__player_alias, dict):
            self.__team_alias = dict()

        if not isinstance(self.__player_alias, dict):
            self.__team_alias = dict()

        if not isinstance(self.__league_alias, dict):
            self.__league_alias = dict()

    def dumpJson(self):
        """Write json data to file."""
        data = dict()
        data['player'] = self.__player_alias
        data['team'] = self.__team_alias
        data['league'] = self.__league_alias
        try:
            with open(getJsonFile('alias'), 'w',
                      encoding='utf-8-sig') as outfile:
                json.dump(data, outfile)
        except Exception:
            module_logger.exception("message")

    def addPlayerAlias(self, name, alias):
        """Add a player alias."""
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
        """Add a team alias."""
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

    def addLeagueAlias(self, name, alias):
        """Add a league alias."""
        name = str(name).strip()
        alias = str(alias).strip()
        if not name:
            raise ValueError('Invalid team name.')
        if not alias:
            raise ValueError('Invalid alias name.')
        if name == alias:
            raise ValueError('Alias matches name.')

        if alias in self.__league_alias:
            raise ValueError('Alias {} is already used by {}'.format(
                alias, self.__league_alias[alias]))
        self.__league_alias[alias] = name

    def removePlayerAlias(self, name, alias):
        """Remove a player alias."""
        name = str(name).strip()
        alias = str(alias).strip()

        try:
            if self.__player_alias[alias] == name:
                del self.__player_alias[alias]
        except KeyError:
            pass

    def removeTeamAlias(self, name, alias):
        """Remove a team alias."""
        name = str(name).strip()
        alias = str(alias).strip()

        try:
            if self.__team_alias[alias] == name:
                del self.__team_alias[alias]
        except KeyError:
            pass

    def removeLeagueAlias(self, name, alias):
        """Remove a team alias."""
        name = str(name).strip()
        alias = str(alias).strip()

        try:
            if self.__league_alias[alias] == name:
                del self.__league_alias[alias]
        except KeyError:
            pass

    def translatePlayer(self, name):
        """Translate a player name."""
        name = str(name).strip()
        return self.__player_alias.get(name, name)

    def translateTeam(self, name):
        """Translate a team name."""
        name = str(name).strip()
        return self.__team_alias.get(name, name)

    def translateLeague(self, name):
        """Translate a league name."""
        name = str(name).strip()
        return self.__league_alias.get(name, name)

    def playerAliasList(self):
        """Get the list of player aliases."""
        player_list = dict()
        for alias, player in self.__player_alias.items():
            if player not in player_list.keys():
                player_list[player] = []
            player_list[player].append(alias)
        return player_list

    def teamAliasList(self):
        """Get list of team aliases."""
        alias_list = dict()
        for alias, team in self.__team_alias.items():
            if team not in alias_list.keys():
                alias_list[team] = []
            alias_list[team].append(alias)
        return alias_list

    def leagueAliasList(self):
        """Get list of league aliases."""
        alias_list = dict()
        for alias, league in self.__league_alias.items():
            if league not in alias_list.keys():
                alias_list[league] = []
            alias_list[league].append(alias)
        return alias_list
