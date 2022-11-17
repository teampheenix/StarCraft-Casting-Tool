"""Matchdata."""
import copy
import difflib
import logging
import re
import shutil

from PyQt5.QtCore import QObject, pyqtSignal

import scctool.settings
import scctool.settings.translation
from scctool.matchgrabber import MatchGrabber

_ = scctool.settings.translation.gettext
# create logger
module_logger = logging.getLogger(__name__)


class MatchData(QObject):
    """Matchdata."""

    dataChanged = pyqtSignal(str, object)
    metaChanged = pyqtSignal()

    def __init__(self, matchControl, controller, match_id, data=None):
        """Init and define custom providers."""
        super().__init__()
        self.__rawData = None
        self.__matchControl = matchControl
        self.__controller = controller
        self.__id = match_id
        self._url = ''
        self.__initData()
        if data is None:
            data = dict()
        self.readData(data)
        self.emitLock = EmitLock()

    def __emitSignal(self, scope, name='', data=None):
        if not self.emitLock.locked():
            if scope == 'data':
                self.dataChanged.emit(name, data)
            elif scope == 'meta':
                self.metaChanged.emit()
            elif scope == 'outcome':
                self.dataChanged.emit('outcome', self.getWinner())
                for idx in range(self.getNoSets()):
                    if self.getMapScore(idx) == 0:
                        colorData = self.getColorData(idx)
                        self.__emitSignal(
                            'data', 'color', {
                                'set_idx': idx,
                                'score_color': colorData["score_color"],
                                'border_color': colorData["border_color"],
                                'hide': colorData["hide"],
                                'opacity': colorData["opacity"]})

    def getControlID(self):
        """Get control ID."""
        return self.__id

    def readData(self, data):
        """Read data."""
        if len(data) > 0:
            self.__data = copy.deepcopy(data)
        else:
            self.setCustom(5, False, False)

    def writeJsonFile(self):
        """Write data to json file."""
        self.__matchControl.writeJsonFile()

    def getData(self):
        """Return the raw data."""
        return self.__data

    def __initMatchGrabber(self):
        provider = self.getProvider()
        (*args,) = (self, self.__controller)

        if provider in self.__matchControl.VALID_PROVIDERS:
            self.__matchGrabber = \
                self.__matchControl.VALID_PROVIDERS[provider](*args)
        else:
            self.__matchGrabber = MatchGrabber(*args)

    def applyCustomFormat(self, name):
        """Apply a custom format."""
        if name in self.__matchControl.CUSTOM_FORMATS:
            customFormat = self.__matchControl.CUSTOM_FORMATS[name](self)
            with self.emitLock(True, self.metaChanged):
                customFormat.applyFormat()
        else:
            raise ValueError("Unknown Custom Match Format.")

    def __str__(self):
        """Return match data as string."""
        return str(self.__data)

    def isValid(self):
        """Check if data is valid."""
        return self.__data is not None

    def parseURL(self, url):
        """Parse a URL and set provider accordingly."""
    # try:
        url = str(url).lower()

        chg = self.setProvider("Custom")

        try:
            self.setID(re.findall(r'\d+', url)[-1])
        except IndexError:
            pass

        self._url = url
        return chg
    # except Exception:
        # self.setProvider("Custom")
        # self.setID(0)
        # module_logger.exception("message")

    def __initData(self):
        self.__data = {}
        self.__data['provider'] = MatchGrabber._provider
        self.__data['league'] = "TBD"
        self.__data['id'] = 0
        self.__data['matchlink'] = ""
        self.__data['no_sets'] = 0
        self.__data['best_of'] = 0
        self.__data['min_sets'] = 0
        self.__data['no_vetoes'] = 0
        self.__data['ace_sets'] = 0
        self.__data['allkill'] = False
        self.__data['solo'] = False
        self.__data['my_team'] = 0
        self.__data['swapped'] = False
        self.__data['teams'] = []
        self.__data['teams'].append({'name': 'TBD', 'tag': None})
        self.__data['teams'].append({'name': 'TBD', 'tag': None})
        self.__data['vetoes'] = []
        self.__data['sets'] = []
        self.__data['players'] = [[], []]

    def swapTeams(self):
        """Swap the teams."""
        module_logger.info("Swapping teams")
        self.__data['swapped'] = not self.__data.get('swapped', False)
        self.__data['my_team'] = -self.__data['my_team']
        self.__data['teams'][1], self.__data['teams'][0] = \
            self.__data['teams'][0], self.__data['teams'][1]
        self.__data['players'][1], self.__data['players'][0] = \
            self.__data['players'][0], self.__data['players'][1]
        for set_idx in range(len(self.__data['sets'])):
            self.__data['sets'][set_idx]['score'] = - \
                self.__data['sets'][set_idx]['score']
        for veto_idx in range(len(self.__data['vetoes'])):
            self.__data['vetoes'][veto_idx]['team'] = \
                1 - self.__data['vetoes'][veto_idx]['team']
        self.__emitSignal('meta')

    def getSwappedIdx(self, idx):
        """Get the swapped index."""
        if self.isSwapped():
            return 1 - idx
        else:
            return idx

    def isSwapped(self):
        """Return if the teams are swapped."""
        return bool(self.__data.get('swapped', False))

    def resetSwap(self):
        """Reset the swap."""
        self.__data['swapped'] = False

    def setMinSets(self, minSets):
        """Set minium number of sets that are played."""
        if(minSets > 0):
            if(minSets > self.getNoSets()):
                self.__data['min_sets'] = self.getNoSets()
            else:
                self.__data['min_sets'] = int(minSets)
        else:
            self.__data['min_sets'] = 0

    def getMinSets(self):
        """Get the minium number of sets that are played."""
        try:
            return int(self.__data['min_sets'])
        except Exception:
            return 0

    def setSolo(self, solo):
        """Set allkill format."""
        self.__data['solo'] = bool(solo)

        if self.__data['solo']:
            for set_idx in range(self.getNoSets()):
                for team_idx in range(2):
                    self.setPlayer(team_idx, set_idx,
                                   self.getPlayer(team_idx, 0))

    def getSolo(self):
        """Check if format is solo (or team)."""
        return bool(self.__data['solo'])

    def setAllKill(self, allkill):
        """Set allkill format."""
        self.__data['allkill'] = bool(allkill)

    def extendAce(self, sets):
        """Extend the ace."""
        self.__data['ace_sets'] = max(int(sets), 0)

        self.resetLabels()

    def getAceSets(self):
        """Get the number of ace sets."""
        return int(self.__data.get('ace_sets', 0))

    def getAllKill(self):
        """Check if format is allkill."""
        return bool(self.__data.get('allkill', 0))

    def allkillUpdate(self):
        """Move the winner to the next set in case of allkill format."""
        if(not self.getAllKill()):
            return False

        for set_idx in range(self.getNoSets()):
            if self.getMapScore(set_idx) == 0:
                if(set_idx == 0):
                    continue
                previous_score = self.getMapScore(set_idx - 1)
                if previous_score == 0:
                    continue
                team_idx = int((previous_score + 1) / 2)
                player = self.getPlayer(team_idx, set_idx).strip().lower()
                if(player != "tbd" and player != ""):
                    continue
                self.setPlayer(team_idx, set_idx, self.getPlayer(team_idx,
                                                                 set_idx - 1),
                               self.getRace(team_idx, set_idx - 1))
                return True

        return False

    def setNoVetoes(self, no_vetoes):
        """Set the number of vetoes."""
        no_vetoes = int(no_vetoes)
        self.__data['no_vetoes'] = int(no_vetoes)
        vetoes = []
        for i in range(no_vetoes):
            try:
                sc2_map = self.__data['vetoes'][i]['map']
            except Exception:
                sc2_map = "TBD"
            try:
                team = self.__data['vetoes'][i]['team']
            except Exception:
                team = i % 2
            vetoes.append({'map': sc2_map, 'team': team})

        self.__data['vetoes'] = vetoes

    def getNoVetoes(self):
        """Get the number of vetoes."""
        return int(self.__data.get('no_vetoes', 0))

    def setCustom(self, regular_sets, allkill, solo, ace_sets=0, vetoes=0):
        """Set a custom match format."""
        regular_sets = int(regular_sets)
        ace_sets = int(ace_sets)
        self.setNoSets(regular_sets, ace_sets)
        self.resetLabels()
        self.setNoVetoes(vetoes)
        self.setAllKill(bool(allkill))
        self.setProvider("Custom")
        self.setID(0)
        self.setURL("", intern=True)
        self.setSolo(solo)

    def resetData(self, reset_options=True):
        """Reset all data to default values."""
        with self.emitLock():
            for team_idx in range(2):
                for set_idx in range(self.getNoSets()):
                    self.setPlayer(team_idx, set_idx, "TBD", "Random")
                self.setTeam(team_idx, "TBD", "TBD")

            for set_idx in range(self.getNoSets()):
                self.setMapScore(set_idx, 0, overwrite=True)
                self.setMap(set_idx)

            self.resetLabels()

            for idx in range(self.getNoVetoes()):
                self.setVeto(idx, 'TBD', idx % 2)

            self.setLeague("TBD")
            self.resetSwap()
            self.setMyTeam(0)
            if reset_options:
                self.setAllKill(False)
                self.setSolo(False)
        self.__emitSignal('meta')

    def resetLabels(self):
        """Reset the map labels."""
        no_sets = self.getNoSets()
        ace_sets = self.getNoAceSets()

        ace_start = no_sets - ace_sets

        for set_idx in range(ace_start):
            self.setLabel(set_idx, "Map " + str(set_idx + 1))
            self.setAce(set_idx, False)

        for set_idx in range(ace_start, no_sets):
            self.setAce(set_idx, True)
            if(ace_sets == 1):
                self.setLabel(set_idx, "Ace Map")
            else:
                self.setLabel(set_idx, "Ace Map "
                              + str(set_idx - ace_start + 1))

    @classmethod
    def calcTotalSets(cls, regular_sets, ace_sets):
        """Calculate the total number of sets."""
        if ace_sets > 0:
            if regular_sets % 2:
                total_sets = regular_sets + ace_sets - 1
            else:
                total_sets = regular_sets + ace_sets
        else:
            total_sets = regular_sets
        return total_sets

    def setNoSets(self, regular_sets=5, ace_sets=0, resetPlayers=False):
        """Set the number of sets/maps."""
        try:
            regular_sets = int(regular_sets)
            ace_sets = int(ace_sets)
            total_sets = self.calcTotalSets(regular_sets, ace_sets)

            if(total_sets < 0):
                total_sets = 0
            elif(total_sets > scctool.settings.max_no_sets):
                total_sets = scctool.settings.max_no_sets

            self.__data['best_of'] = regular_sets
            self.__data['ace_sets'] = ace_sets

            sets = []
            players = [[], []]

            for i in range(total_sets):
                try:
                    sc2_map = self.__data['sets'][i]['map']
                except Exception:
                    sc2_map = "TBD"
                try:
                    score = self.__data['sets'][i]['score']
                except Exception:
                    score = 0
                try:
                    label = self.__data['sets'][i]['label']
                except Exception:
                    label = f'Map {i + 1}'
                try:
                    ace = bool(self.__data['sets'][i].get('ace', False))
                except Exception:
                    ace = False
                for j in range(2):
                    if(not resetPlayers):
                        try:
                            player_name = self.__data['players'][j][i]['name']
                        except Exception:
                            player_name = 'TBD'
                        try:
                            player_race = getRace(
                                self.__data['players'][j][i]['race'])
                        except Exception:
                            player_race = 'Random'
                    else:
                        player_name = 'TBD'
                        player_race = 'Random'

                    players[j].append(
                        {'name': player_name, 'race': player_race})

                sets.append({'label': label, 'map': sc2_map,
                             'score': score, 'ace': ace})

            self.__data['no_sets'] = total_sets
            self.__data['min_sets'] = 0
            self.__data['sets'] = sets
            self.__data['players'] = players

        except Exception:
            module_logger.exception("message")

    def setMyTeam(self, myteam, swap=False):
        """Set "my team"."""
        if(isinstance(myteam, str)):
            new = self.__selectMyTeam(myteam)
        elif(myteam in [-1, 0, 1]):
            new = myteam
        else:
            return False

        if(new != self.__data['my_team']):
            self.__data['my_team'] = new
            for i in range(self.getNoSets()):
                score = self.getMapScore(i)
                colorData = self.getColorData(i)
                self.__emitSignal(
                    'data',
                    'color-data', {
                        'set_idx': i,
                        'score': score,
                        'score_color': colorData['score_color'],
                        'border_color': colorData['border_color'],
                        'hide': colorData['hide'],
                        'opacity': colorData['opacity']})

        if swap and int(self.__data['my_team']) > 0:
            self.swapTeams()
            return True
        return False

    def getMyTeam(self):
        """Return my team: (-1,0,1)."""
        try:
            return int(self.__data['my_team'])
        except Exception:
            return 0

    def __selectMyTeam(self, string):
        teams = [self.getTeam(0).lower(), self.getTeam(1).lower()]
        matches = difflib.get_close_matches(string.lower(), teams, 1)
        if(len(matches) != 1):
            return 0
        elif(matches[0] == teams[0]):
            return -1
        else:
            return 1

    def getNoSets(self):
        """Get number of sets."""
        try:
            return int(self.__data['no_sets'])
        except Exception:
            return 0

    def getNoAceSets(self):
        """Get number of ace sets."""
        try:
            return int(self.__data.get('ace_sets', 0))
        except Exception:
            return 0

    def setVeto(self, idx, sc2_map="TBD", team=None):
        """Set a map veto."""
        try:
            if(not (idx >= 0 and idx < self.__data['no_vetoes'])):
                return False
            sc2_map, __ = autoCorrectMap(sc2_map)
            if team not in [0, 1]:
                team = self.__data['vetoes'][idx]['team']
            is_new_map = self.__data['vetoes'][idx]['map'] != sc2_map
            if(is_new_map or self.__data['vetoes'][idx]['team'] != team):
                old_map = self.__data['vetoes'][idx]['map']
                self.__data['vetoes'][idx]['map'] = sc2_map
                self.__data['vetoes'][idx]['team'] = team
                self.__emitSignal(
                    'data', 'map_veto',
                    {'idx': idx, 'map': sc2_map,
                     'team': team, 'old_map': old_map})
            return True
        except Exception:
            return False

    def getVeto(self, idx):
        """Get the map of a veto."""
        try:
            if(not (idx >= 0 and idx < self.__data['no_vetoes'])):
                return {'idx': idx, 'map': 'TBD', 'team':  idx % 2}

            return self.__data['vetoes'][idx]
        except Exception:
            return {'idx': idx, 'map': 'TBD', 'team':  idx % 2}

    def setMap(self, set_idx, sc2_map="TBD"):
        """Set the map of a set."""
        try:
            if(not (set_idx >= 0 and set_idx < self.__data['no_sets'])):
                return False
            sc2_map, __ = autoCorrectMap(sc2_map)
            if(self.__data['sets'][set_idx]['map'] != sc2_map):
                self.__data['sets'][set_idx]['map'] = sc2_map
                self.__emitSignal(
                    'data', 'map', {'set_idx': set_idx, 'value': sc2_map})

            return True
        except Exception:
            return False

    def getMap(self, set_idx):
        """Get the map of a set."""
        try:
            if(not (set_idx >= 0 and set_idx < self.__data['no_sets'])):
                return False

            return str(self.__data['sets'][set_idx]['map'])
        except Exception:
            return False

    def yieldMaps(self):
        """Yield all maps (including vetoes)."""
        yielded = set()
        for idx in range(self.getNoSets()):
            sc2_map = self.getMap(idx)
            if sc2_map and sc2_map.lower() != "TBD" and sc2_map not in yielded:
                yield sc2_map
                yielded.add(sc2_map)
        for idx in range(self.getNoVetoes()):
            sc2_map = self.getVeto(idx).get('map', 'TBD')
            if sc2_map and sc2_map.lower() != "TBD" and sc2_map not in yielded:
                yield sc2_map
                yielded.add(sc2_map)

    def getScoreString(self, middleStr=':'):
        """Get the score as a string."""
        score = self.getScore()
        return str(score[0]) + middleStr + str(score[1])

    def getScore(self):
        """Get the score as an list."""
        score = [0, 0]

        for set_idx in range(self.getNoSets()):
            map_score = self.getMapScore(set_idx)
            if(map_score < 0):
                score[0] += 1
            elif(map_score > 0):
                score[1] += 1
            else:
                continue
        return score

    def getBestOfRaw(self):
        """Get raw BestOf number."""
        try:
            return int(self.__data['best_of'])
        except Exception:
            return False

    def getBestOf(self):
        """Get filtered BestOf number (only odd)."""
        try:
            best_of = self.getBestOfRaw()
            no_sets = self.getNoSets()
            score = self.getScore()

            if(min(score) < int(best_of / 2)):
                return best_of
            else:
                return no_sets
        except Exception:
            return 0

    def isDecided(self):
        """Check if match is decided."""
        return max(self.getScore()) > int(self.getBestOf() / 2)

    def getWinner(self):
        """Get the winner."""
        score = self.getScore()
        if not self.isDecided() or score[0] == score[1]:
            return 0
        elif score[0] > score[1]:
            return -1
        else:
            return 1

    def setMapScore(self, set_idx, score, overwrite=False, applySwap=False):
        """Set the score of a set."""
        try:
            if(not (set_idx >= 0 and set_idx < self.__data['no_sets'])):
                return False
            if(score in [-1, 0, 1]):
                if applySwap and self.isSwapped():
                    score = -score
                if(overwrite or self.__data['sets'][set_idx]['score'] == 0):
                    if(self.__data['sets'][set_idx]['score'] != score):
                        was_decided = self.isDecided()
                        old_bestof = self.getBestOf()
                        self.__data['sets'][set_idx]['score'] = score
                        outcome_changed = self.isDecided() != was_decided
                        new_bestof = self.getBestOf()
                        if outcome_changed:
                            self.__emitSignal('outcome')
                        if new_bestof != old_bestof:
                            self.__emitSignal('data', 'bestof',
                                              {'value': new_bestof})
                        self.__emitSignal('data', 'score',
                                          {'set_idx': set_idx,
                                           'value': score})
                return True
            else:
                return False
        except Exception:
            return False

    def getMapScore(self, set_idx):
        """Get the score of a set."""
        try:
            if(not (set_idx >= 0 and set_idx < self.__data['no_sets'])):
                return False

            return int(self.__data['sets'][set_idx]['score'])
        except Exception:
            return False

    def getNextSet(self):
        """Get the next set."""
        for set_idx in range(self.getNoSets()):
            if self.getMapScore(set_idx) == 0:
                return set_idx
        return -1

    def getNextMap(self, next_idx=-1):
        """Return the next map (if the set index matches)."""
        set_idx = self.getNextSet()
        if set_idx != -1 and (next_idx == -1 or set_idx == next_idx):
            return self.getMap(set_idx)
        else:
            return "TBD"

    def wasMapPlayed(self, sc2_map):
        """Return if map was already played."""
        for set_idx in range(self.getNoSets()):
            if (sc2_map.lower() == self.getMap(set_idx).lower()
                    and self.getMapScore(set_idx) != 0):
                return True
        return False

    def isMapVetoed(self, sc2_map):
        """Return if map is vetoed."""
        for idx in range(self.getNoVetoes()):
            if (sc2_map.lower() == self.getVeto(idx).get('map').lower()):
                return True
        return False

    def getNextPlayer(self, team_idx):
        """Get the player of the next undecided set."""
        player = "TBD"
        for set_idx in range(self.getNoSets()):
            if self.getMapScore(set_idx) == 0:
                player = self.getPlayer(team_idx, set_idx)
                break

        return player

    def getNextRace(self, team_idx):
        """Get the players race of the next undecided set."""
        player = "Random"
        for set_idx in range(self.getNoSets()):
            if self.getMapScore(set_idx) == 0:
                player = self.getRace(team_idx, set_idx)
                break

        return player

    def setPlayer(self, team_idx, set_idx, name="TBD", race=False):
        """Set the player of a set."""
        try:
            if(not (set_idx >= 0 and set_idx < self.__data['no_sets']
                    and team_idx in range(2))):
                return False

            if(self.__data['players'][team_idx][set_idx]['name'] != name):
                self.__data['players'][team_idx][set_idx]['name'] = name
                self.__emitSignal('data', 'player', {
                                  'team_idx': team_idx,
                                  'set_idx': set_idx,
                                  'value': name})

            if(race):
                self.setRace(team_idx, set_idx, race)

            return True
        except Exception:
            return False

    def getPlayerList(self, team_idx):
        """Get complete player list of a team."""
        player_list = []
        try:
            for set_idx in range(self.getNoSets()):
                player_list.append(self.getPlayer(team_idx, set_idx))
            return player_list
        except Exception:
            return []

    def getPlayer(self, team_idx, set_idx):
        """Get the player (name) of a set."""
        try:
            if(not (set_idx >= 0 and set_idx < self.__data['no_sets']
                    and team_idx in range(2))):
                return False

            return self.__data['players'][team_idx][set_idx]['name'].strip()

        except Exception:
            return False

    def setRace(self, team_idx, set_idx, race="Random"):
        """Set a players race."""
        try:
            if(not (set_idx >= 0 and set_idx < self.__data['no_sets']
                    and team_idx in range(2))):
                return False

            race = getRace(race)

            if(self.__data['players'][team_idx][set_idx]['race'] != race):
                self.__data['players'][team_idx][set_idx]['race'] = race
                self.__emitSignal(
                    'data', 'race', {'team_idx': team_idx,
                                     'set_idx': set_idx,
                                     'value': race})
            return True
        except Exception:
            return False

    def getRace(self, team_idx, set_idx):
        """Get a players race."""
        try:
            if(not (set_idx >= 0 and set_idx < self.__data['no_sets']
                    and team_idx in range(2))):
                return False

            return getRace(self.__data['players'][team_idx][set_idx]['race'])

        except Exception:
            return False

    def setAce(self, set_idx, ace):
        """Label set as ace."""
        ace = bool(ace)
        try:
            if(not (set_idx >= 0 and set_idx < self.__data['no_sets'])):
                return False
            if(self.__data['sets'][set_idx]['ace'] != ace):
                self.__data['sets'][set_idx]['ace'] = ace
            return True
        except Exception:
            return False

    def isAce(self, set_idx):
        """Return if set is labeld as ace."""
        try:
            return bool(self.__data['sets'][set_idx].get('ace', False))
        except Exception:
            return False

    def setLabel(self, set_idx, label):
        """Set a map label."""
        try:
            if(not (set_idx >= 0 and set_idx < self.__data['no_sets'])):
                return False
            if(self.__data['sets'][set_idx]['label'] != label):
                self.__data['sets'][set_idx]['label'] = label
                self.__emitSignal('data', 'map_label', {
                                  'set_idx': set_idx, 'value': label})
            return True
        except Exception:
            return False

    def getLabel(self, set_idx):
        """Get a map label."""
        try:
            if(not (set_idx >= 0 and set_idx < self.__data['no_sets'])):
                return False
            return str(self.__data['sets'][set_idx]['label'])
        except Exception:
            return False

    def setTeam(self, team_idx, name, tag=False):
        """Set a team name."""
        if team_idx not in range(2):
            return False

        new = str(name.strip())

        if(self.__data['teams'][team_idx]['name'] != new):
            self.__data['teams'][team_idx]['name'] = new
            self.__emitSignal('data', 'team', {'idx': team_idx, 'value': new})

        if(tag):
            self.setTeamTag(team_idx, tag)

        return True

    def getTeam(self, team_idx):
        """Get team name."""
        if team_idx not in range(2):
            return False

        return str(self.__data['teams'][team_idx]['name'])

    def getTeamOrPlayer(self, team_idx):
        """Get team name or player name depending on mode."""
        if self.getSolo():
            return self.getPlayer(team_idx, 0)
        else:
            return self.getTeam(team_idx)

    def setTeamTag(self, team_idx, tag):
        """Set team tag."""
        if team_idx not in range(2):
            return False

        new = str(tag)

        if(self.__data['teams'][team_idx]['tag'] != new):
            self.__data['teams'][team_idx]['tag'] = new

        return True

    def getTeamTag(self, team_idx):
        """Get team tag."""
        if team_idx not in range(2):
            return False
        name = str(self.__data['teams'][team_idx]['tag'])
        if(name):
            return str(name)
        else:
            return self.getTeam(team_idx)

    def setID(self, match_id):
        """Set match id."""
        self.__data['id'] = int(match_id)
        self.__matchGrabber.setID(match_id)
        return True

    def getID(self):
        """Get match id."""
        return int(self.__data['id'])

    def setLeague(self, league):
        """Set league."""
        league = str(league)
        if(self.__data['league'] != league):
            self.__data['league'] = league
            self.__emitSignal('data', 'league', league)
        return True

    def getLeague(self):
        """Get league."""
        return self.__data['league']

    def setURL(self, url, intern=False):
        """Set URL."""
        self.__data['matchlink'] = str(url)
        if all:
            self.__url = url
        return True

    def getURL(self):
        """Get league."""
        return str(self.__data['matchlink'])

    def setProvider(self, provider):
        """Set the provider."""
        provider_changed = False
        if provider:
            matches = difflib.get_close_matches(
                provider, self.__matchControl.VALID_PROVIDERS.keys(), 1)
            if len(matches) == 0:
                new = MatchGrabber._provider
            else:
                new = matches[0]

            if self.__data['provider'] != new:
                self.__data['provider'] = new
                provider_changed = True
                module_logger.info(
                    'Changed MathGrabber Provider to {}'.format(new))
        else:
            self.__data['provider'] = MatchGrabber._provider

        self.__initMatchGrabber()
        return provider_changed

    def getProvider(self):
        """Get the provider."""
        return str(self.__data['provider'])

    def grabData(self, metaChange=False, logoManager=None):
        """Grab the match data via a provider."""
        self.__matchGrabber.grabData(metaChange, logoManager)
        self.setURL(self.__matchGrabber.getURL(), intern=True)

    def downloadBanner(self):
        """Download the match banner via a provider."""
        self.__matchGrabber.downloadBanner()

    def downloadLogos(self):
        """Grab the team logos via a provider."""
        self.__matchGrabber.downloadLogos(self.__controller.logoManager)

    def getScoreData(self):
        """Return the score data."""
        data = dict()

        if self.getSolo():
            data['team1'] = self.getPlayer(0, 0)
            data['team2'] = self.getPlayer(1, 0)
        else:
            data['team1'] = self.getTeam(0)
            data['team2'] = self.getTeam(1)

        data['logo1'] = self.__controller.logoManager.getTeam1(
            self.__id).getFile(True)
        data['logo2'] = self.__controller.logoManager.getTeam2(
            self.__id).getFile(True)

        score = [0, 0]
        winner = [False, False]
        sets = []
        bestof = self.getBestOf()
        threshold = int(bestof / 2)

        for i in range(self.getNoSets()):
            sets.insert(i, ["", ""])
            if(max(score) > threshold and i >= self.getMinSets()):
                sets[i][0] = scctool.settings.config.parser.get(
                    "MapIcons", "notplayed_color")
                sets[i][1] = scctool.settings.config.parser.get(
                    "MapIcons", "notplayed_color")
            elif(self.getMapScore(i) == -1):
                sets[i][0] = scctool.settings.config.parser.get(
                    "MapIcons", "win_color")
                sets[i][1] = scctool.settings.config.parser.get(
                    "MapIcons", "lose_color")
                score[0] += 1
            elif(self.getMapScore(i) == 1):
                sets[i][0] = scctool.settings.config.parser.get(
                    "MapIcons", "lose_color")
                sets[i][1] = scctool.settings.config.parser.get(
                    "MapIcons", "win_color")
                score[1] += 1
            else:
                sets[i][0] = scctool.settings.config.parser.get(
                    "MapIcons", "undecided_color")
                sets[i][1] = scctool.settings.config.parser.get(
                    "MapIcons", "undecided_color")

        winner[0] = score[0] > threshold
        winner[1] = score[1] > threshold

        data['sets'] = sets
        data['bestof'] = bestof
        data['winner'] = winner
        data['score1'] = score[0]
        data['score2'] = score[1]

        return data

    def getVetoData(self):
        """Return the veto data."""
        data = []

        for idx in range(self.getNoVetoes()):
            veto = self.getVeto(idx)
            data.append(
                {'map_name': veto['map'],
                 'map_img': self.__controller.getMapImg(veto['map']),
                 'team': veto['team']})

        return data

    def getScoreIconColor(self, team_idx, set_idx):
        """Return the score icon color."""
        score = self.getMapScore(set_idx)
        team = 2 * team_idx - 1
        if score == 0:
            if (set_idx >= self.getMinSets()
                    and max(self.getScore()) > int(self.getBestOf() / 2)):
                return scctool.settings.config.parser.get(
                    "MapIcons",
                    "notplayed_color")
            else:
                return scctool.settings.config.parser.get(
                    "MapIcons",
                    "undecided_color")
        elif score == team:
            return scctool.settings.config.parser.get(
                "MapIcons",
                "win_color")
        else:
            return scctool.settings.config.parser.get(
                "MapIcons",
                "lose_color")

    def getColorData(self, set_idx):
        """Return the color data."""
        score = self.getMapScore(set_idx)
        team = self.getMyTeam()
        won = score * team
        hide = team == 0
        opacity = scctool.settings.config.parser.get(
            "MapIcons",
            "notplayed_opacity")
        if won == 1:
            border_color = scctool.settings.config.parser.get(
                "MapIcons",
                "win_color")
            score_color = border_color
            opacity = 0.0
        elif won == -1:
            border_color = scctool.settings.config.parser.get(
                "MapIcons",
                "lose_color")
            score_color = border_color
            opacity = 0.0
        else:
            if (score == 0
                and set_idx >= self.getMinSets()
                    and max(self.getScore()) > int(self.getBestOf() / 2)):
                border_color = scctool.settings.config.parser.get(
                    "MapIcons",
                    "notplayed_color")
                score_color = border_color
            else:
                border_color = scctool.settings.config.parser.get(
                    "MapIcons",
                    "default_border_color")
                score_color = scctool.settings.config.parser.get(
                    "MapIcons",
                    "undecided_color")
                opacity = 0.0

        return {'score_color': score_color,
                'border_color': border_color,
                'opacity': opacity,
                'hide': hide}

    def getMapIconsData(self):
        """Update map icons."""
        websocket_data = dict()
        try:
            team = self.getMyTeam()
            score = [0, 0]

            hide_scoreicon = team == 0

            for i in range(self.getNoSets()):
                winner = self.getMapScore(i)
                won = winner * team
                opacity = 0.0

                threshold = int(self.getBestOf() / 2)

                if(max(score) > threshold and i >= self.getMinSets()):
                    border_color = scctool.settings.config.parser.get(
                        "MapIcons", "notplayed_color")
                    score_color = scctool.settings.config.parser.get(
                        "MapIcons", "notplayed_color")
                    opacity = scctool.settings.config.parser.get(
                        "MapIcons", "notplayed_opacity")
                    winner = 0
                elif(won == 1):
                    border_color = scctool.settings.config.parser.get(
                        "MapIcons", "win_color")
                    score_color = scctool.settings.config.parser.get(
                        "MapIcons", "win_color")
                elif(won == -1):
                    border_color = scctool.settings.config.parser.get(
                        "MapIcons", "lose_color")
                    score_color = scctool.settings.config.parser.get(
                        "MapIcons", "lose_color")
                else:
                    border_color = scctool.settings.config.parser.get(
                        "MapIcons", "default_border_color")
                    score_color = scctool.settings.config.parser.get(
                        "MapIcons", "undecided_color")

                if(winner == -1):
                    player1status = 'winner'
                    player2status = 'loser'
                    score[0] += 1
                elif(winner == 1):
                    player1status = 'loser'
                    player2status = 'winner'
                    score[1] += 1
                else:
                    player1status = ''
                    player2status = ''

                data = dict()
                data['player1'] = self.getPlayer(0, i)
                data['player2'] = self.getPlayer(1, i)
                data['race1'] = self.getRace(0, i).lower()
                data['race2'] = self.getRace(1, i).lower()
                data['map_img'] = self.__controller.getMapImg(self.getMap(i))
                data['mapname'] = self.getMap(i)
                data['maplabel'] = self.getLabel(i)
                data['score_color'] = score_color
                data['border_color'] = border_color
                data['hide_scoreicon'] = hide_scoreicon
                data['opacity'] = opacity
                data['status1'] = player1status
                data['status2'] = player2status

                websocket_data[i + 1] = data

        except Exception:
            module_logger.exception("message")

        return websocket_data

    def autoSetMyTeam(self, swap=False):
        """Try to set team via fav teams."""
        try:
            team_matches = []
            for team_idx in range(2):
                team = self.__data['teams'][team_idx]['name']
                if not team or team == "TBD":
                    continue
                matches = difflib.get_close_matches(
                    team.lower(), scctool.settings.config.getMyTeams(), 1)
                if(len(matches) > 0):
                    team_matches.append(team_idx)
            if len(team_matches) == 1:
                self.setMyTeam(team_matches.pop() * 2 - 1, swap)
                return True
            else:
                self.setMyTeam(0)
                return False

        except Exception:
            module_logger.exception("message")
            return False

    def parseScope(self, scope='all'):
        """Parse the scope."""
        if scope == 'all':
            for idx in range(self.getNoSets()):
                yield idx
            return
        if scope == 'not-ace':
            for idx in range(self.getNoSets()):
                if not self.isAce(idx):
                    yield idx
            return
        if scope == 'ace':
            for idx in range(self.getNoSets()):
                if self.isAce(idx):
                    yield idx
            return
        if scope == 'decided':
            for idx in range(self.getNoSets()):
                if self.getMapScore(idx) != 0:
                    yield idx
            return
        if scope == 'decided+1':
            stop = False
            for idx in range(self.getNoSets()):
                if self.getMapScore(idx) != 0:
                    stop = False
                    yield idx
                elif not stop:
                    stop = True
                    yield idx
                else:
                    return
            return
        if scope == 'undecided':
            for idx in range(self.getNoSets()):
                if self.getMapScore(idx) == 0:
                    yield idx
            return
        if scope == 'current':
            idx = self.getNextSet()
            if idx == -1:
                if self.getNoSets() > 0:
                    yield self.getNoSets() - 1
            else:
                yield idx
            return
        if scope == 'current+1':
            idx = self.getNextSet()
            if idx == -1:
                if self.getNoSets() > 0:
                    yield self.getNoSets() - 1
                if self.getNoSets() - 1 > 0:
                    yield self.getNoSets() - 2
            else:
                yield idx
                if idx > 0:
                    yield idx - 1
                elif idx < self.getNoSets():
                    yield idx + 1
            return

        m = re.match(r'^(\d+)-(\d+)$', scope)
        if m and int(m.group(1)) <= int(m.group(2)):
            for idx in range(max(int(m.group(1)) - 1, 0),
                             min(int(m.group(2)), self.getNoSets())):
                yield idx
            return
        else:
            for idx in range(self.getNoSets()):
                yield idx
            return

    def isValidScope(self, scope):
        """Check if scope is valid."""
        if scope in self.__matchControl.scopes.keys():
            return True
        else:
            m = re.match(r'^(\d+)-(\d+)$', scope)
            if m and int(m.group(1)) <= int(m.group(2)):
                return int(m.group(1)) > 0
            else:
                return False


def autoCorrectMap(sc2_map):
    """Corrects map using list in config."""
    lower_map_dict = {value.lower(): value for value in scctool.settings.maps}
    if not isinstance(sc2_map, str):
        sc2_map = "TBD"
    try:
        matches = difflib.get_close_matches(
            sc2_map.lower(), lower_map_dict.keys(), 1)
        if(len(matches) == 0):
            return sc2_map, False
        else:
            return lower_map_dict[matches[0]], True

    except Exception:
        module_logger.exception("message")


def getRace(race_input):
    """Get race by using the first letter."""
    try:
        for idx, race in enumerate(scctool.settings.races):
            if(race_input[0].upper() == race[0].upper()):
                return scctool.settings.races[idx]
    except Exception:
        return "Random"


class EmitLock():
    """Emit lock."""

    def __init__(self):
        """Init lock."""
        self.__locked = False
        self.__useLock = True
        self.__signal = None

    def __call__(self, useLock=True, signal=None):
        """Call the lock."""
        self.__useLock = bool(useLock)
        self.__signal = signal
        return self

    def __enter__(self):
        """Enter the lock."""
        self.__locked = self.__useLock
        return self

    def __exit__(self, error_type, value, traceback):
        """Exit the lock."""
        self.__locked = False
        if self.__useLock and self.__signal:
            self.__signal.emit()

    def locked(self):
        """Return if the lock is active."""
        return bool(self.__locked)
