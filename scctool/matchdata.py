"""Matchdata."""
import difflib
import json
import logging
import re
import shutil
from collections import OrderedDict

from PyQt5.QtCore import QObject, pyqtSignal

import scctool.settings
from scctool.matchformat import *
from scctool.matchgrabber import *

# create logger
module_logger = logging.getLogger('scctool.matchdata')


class matchData(QObject):
    """Matchdata."""
    dataChanged = pyqtSignal(str, object)
    metaChangedSignal = pyqtSignal()

    def __init__(self, controller):
        """Init and define custom providers."""
        super().__init__()
        self.__rawData = None
        self.__controller = controller
        self.__initProviderList()
        self.__initData()
        self.__initMatchGrabber()
        self.__initCustomFormats()

        self.emitLock = EmitLock()
        self.metaChangedSignal.connect(lambda: print('meta Changed'))

    def __initProviderList(self):
        self.__VALID_PROVIDERS = dict()
        self.__VALID_PROVIDERS[MatchGrabber._provider] = MatchGrabber
        for cls in MatchGrabber.__subclasses__():
            self.__VALID_PROVIDERS[cls._provider] = cls

    def __initMatchGrabber(self):
        provider = self.getProvider()
        (*args,) = (self, self.__controller)

        if provider in self.__VALID_PROVIDERS:
            self.__matchGrabber = self.__VALID_PROVIDERS[provider](*args)
        else:
            self.__matchGrabber = MatchGrabber(*args)

    def __initCustomFormats(self):
        formats = dict()
        for cls in MatchFormat.__subclasses__():
            formats[cls._name] = cls
        self.__CUSTOM_FORMATS = OrderedDict(sorted(formats.items()))

    def getCustomFormats(self):
        for format in self.__CUSTOM_FORMATS.keys():
            yield format, self.__CUSTOM_FORMATS[format]._icon

    def applyCustomFormat(self, name):
        if name in self.__CUSTOM_FORMATS:
            customFormat = self.__CUSTOM_FORMATS[name](self)
            customFormat.applyFormat()
        else:
            raise ValueError("Unknown Custom Match Format.")

    def __emitSignal(self, scope, name='', object=None):
        if not self.emitLock.locked():
            if scope == 'data':
                self.dataChanged.emit(name, object)
            elif scope == 'meta':
                self.metaChangedSignal.emit()
            elif scope == 'outcome':
                self.dataChanged.emit('outcome', self.getWinner())
                if self.isDecided():
                    color = scctool.settings.config.parser.get(
                        "MapIcons", "notplayed_color")
                    color2 = color
                else:
                    color = scctool.settings.config.parser.get(
                        "MapIcons", "undecided_color")
                    color2 = scctool.settings.config.parser.get(
                        "MapIcons", "default_border_color")
                for idx in range(self.getNoSets()):
                    if self.getMapScore(idx) == 0:
                        self.__emitSignal('data', 'color', {
                                          'set_idx': idx,
                                          'color': color,
                                          'color2': color2})

    def readJsonFile(self):
        """Read json data from file."""
        try:
            with open(scctool.settings.getJsonFile('matchdata'),
                      'r', encoding='utf-8-sig') as json_file:
                self.__data = json.load(json_file)
        except Exception as e:
            # module_logger.exception("message")
            self.setCustom(5, False, False)

        self.allSetsChanged()

    def writeJsonFile(self):
        """Write json data to file."""
        try:
            with open(scctool.settings.getJsonFile('matchdata'),
                      'w', encoding='utf-8-sig') as outfile:
                json.dump(self.__data, outfile)
        except Exception as e:
            module_logger.exception("message")

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

        if(url.find('alpha') != -1):
            chg = self.setProvider("AlphaSC2")
        elif(url.find('hdgame') != -1):
            chg = self.setProvider("RSTL")
        else:
            chg = self.setProvider("Custom")

        self.setID(re.findall('\d+', url)[-1])

        return chg
    # except Exception as e:
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
        self.__data['allkill'] = False
        self.__data['solo'] = False
        self.__data['my_team'] = 0
        self.__data['swapped'] = False
        self.__data['teams'] = []
        self.__data['teams'].append({'name': 'TBD', 'tag': None})
        self.__data['teams'].append({'name': 'TBD', 'tag': None})
        self.__data['sets'] = []
        self.__data['players'] = [[], []]

        self.__setsChanged = []
        self.__metaChanged = False

    def swapTeams(self):
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
        self.allChanged()
        self.__emitSignal('meta')

    def getSwappedIdx(self, idx):
        if self.isSwapped():
            return 1 - idx
        else:
            return idx

    def isSwapped(self):
        return bool(self.__data.get('swapped', False))

    def resetSwap(self):
        self.__data['swapped'] = False

    def allChanged(self):
        """Mark all data changed."""
        self.allSetsChanged()
        self.__metaChanged = True

    def allSetsChanged(self):
        """Mark all sets changed."""
        self.__setsChanged = [True] * self.getNoSets()

    def resetChanged(self):
        """Reset the changed status of the data."""
        self.__setsChanged = [False] * self.getNoSets()
        self.__metaChanged = False

    def metaChanged(self):
        """Mark meta data has changed."""
        self.__metaChanged = True

    def hasMetaChanged(self):
        """Check if meta data has changed."""
        return bool(self.__metaChanged)

    def hasAnySetChanged(self):
        """Check if any set data has changed."""
        for i in range(self.getNoSets()):
            if(self.hasSetChanged(i)):
                return True
        return False

    def hasSetChanged(self, set_idx):
        """Check if data of a set has changed."""
        try:
            return bool(self.__setsChanged[set_idx])
        except Exception:
            return False

    def setMinSets(self, minSets):
        """Set minium number of sets that are played."""
        if(minSets > 0):
            if(minSets > self.getBestOfRaw()):
                self.__data['min_sets'] = self.getBestOfRaw()
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

    def getAllKill(self):
        """Check if format is allkill."""
        return bool(self.__data['allkill'])

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

    def setCustom(self, bestof, allkill, solo):
        """Set a custom match format."""
        with self.emitLock():
            bestof = int(bestof)
            allkill = bool(allkill)
            if(bestof == 2):
                no_sets = 2
            else:
                no_sets = bestof + 1 - bestof % 2

            self.setNoSets(no_sets, bestof)
            self.resetLabels()
            self.setAllKill(allkill)
            self.setProvider("Custom")
            self.setID(0)
            self.setURL("")
            self.setSolo(solo)
        self.__emitSignal('meta')

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

            self.setLeague("TBD")
            self.setMyTeam(0)
            if reset_options:
                self.setAllKill(False)
                self.setSolo(False)
        self.__emitSignal('meta')

    def resetLabels(self):
        """Reset the map labels."""
        best_of = self.__data['best_of']
        no_sets = self.getNoSets()

        if(best_of == 2):
            for set_idx in range(no_sets):
                self.setLabel(set_idx, "Map " + str(set_idx + 1))
            return

        ace_start = no_sets - 3 + 2 * (best_of % 2)
        skip_one = (ace_start + 1 == no_sets)
        ace = (best_of % 2) == 0

        for set_idx in range(no_sets):
            self.setLabel(set_idx, "Map " + str(set_idx + 1))

        if ace:
            for set_idx in range(ace_start, no_sets):
                if(skip_one):
                    self.setLabel(set_idx, "Ace Map")
                else:
                    self.setLabel(set_idx, "Ace Map " +
                                  str(set_idx - ace_start + 1))

    def setNoSets(self, no_sets=5, bestof=False, resetPlayers=False):
        """Set the number of sets/maps."""
        try:
            no_sets = int(no_sets)

            if(no_sets < 0):
                no_sets = 0
            elif(no_sets > scctool.settings.max_no_sets):
                no_sets = scctool.settings.max_no_sets

            if((not bestof) or bestof <= 0 or bestof > no_sets):
                self.__data['best_of'] = no_sets
            else:
                self.__data['best_of'] = int(bestof)

            sets = []
            changed = []
            players = [[], []]

            for i in range(no_sets):
                try:
                    map = self.__data['sets'][i]['map']
                except Exception:
                    map = "TBD"
                try:
                    score = self.__data['sets'][i]['score']
                except Exception:
                    score = 0
                try:
                    label = self.__data['sets'][i]['label']
                except Exception:
                    label = 'Map ' + str(i + 1)
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

                sets.append({'label': label, 'map': map, 'score': score})
                changed.append(True)

            self.__data['no_sets'] = no_sets
            self.__data['min_sets'] = 0
            self.__data['sets'] = sets
            self.__data['players'] = players
            self.__setsChanged = changed

        except Exception as e:
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
                self.__setsChanged[i] = True

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

    def setMap(self, set_idx, map="TBD"):
        """Set the map of a set."""
        try:
            if(not (set_idx >= 0 and set_idx < self.__data['no_sets'])):
                return False
            map, _ = autoCorrectMap(map)
            if(self.__data['sets'][set_idx]['map'] != map):
                self.__data['sets'][set_idx]['map'] = map
                self.__setsChanged[set_idx] = True
                self.__emitSignal(
                    'data', 'map', {'set_idx': set_idx, 'value': map})

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
        yielded = set()
        for idx in range(self.getNoSets()):
            map = self.getMap(idx)
            if map and map.lower() != "TBD" and map not in yielded:
                yield map
                yielded.add(map)

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
        """Get flitered BestOf number (only odd)."""
        try:
            best_of = self.__data['best_of']

            if(best_of == 2):
                return 3

            if(best_of % 2):  # odd, okay
                return best_of
            else:  # even
                score = self.getScore()
                if(min(score) < best_of / 2 - 1):
                    return best_of - 1
                else:
                    return best_of + 1
            return
        except Exception:
            return False

    def isDecided(self):
        """Check if match is decided."""
        return max(self.getScore()) > int(self.getBestOf() / 2)

    def getWinner(self):
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
                        if(self.isDecided()):
                            self.__metaChanged = True
                        was_decided = self.isDecided()
                        self.__data['sets'][set_idx]['score'] = score
                        outcome_changed = self.isDecided() != was_decided
                        if outcome_changed:
                            self.__emitSignal('outcome')
                        self.__setsChanged[set_idx] = True
                        self.__emitSignal('data', 'score',
                                          {'set_idx': set_idx, 'value': score})
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
            if(not (set_idx >= 0 and set_idx < self.__data['no_sets'] and
                    team_idx in range(2))):
                return False

            if(self.__data['players'][team_idx][set_idx]['name'] != name):
                self.__data['players'][team_idx][set_idx]['name'] = name
                self.__setsChanged[set_idx] = True
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
        list = []
        try:
            for set_idx in range(self.getNoSets()):
                list.append(self.getPlayer(team_idx, set_idx))
            return list
        except Exception:
            return []

    def getPlayer(self, team_idx, set_idx):
        """Get the player (name) of a set."""
        try:
            if(not (set_idx >= 0 and set_idx < self.__data['no_sets'] and
                    team_idx in range(2))):
                return False

            return self.__data['players'][team_idx][set_idx]['name'].strip()

        except Exception:
            return False

    def setRace(self, team_idx, set_idx, race="Random"):
        """Set a players race."""
        try:
            if(not (set_idx >= 0 and set_idx < self.__data['no_sets'] and
                    team_idx in range(2))):
                return False

            race = getRace(race)

            if(self.__data['players'][team_idx][set_idx]['race'] != race):
                self.__data['players'][team_idx][set_idx]['race'] = race
                self.__setsChanged[set_idx] = True
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
            if(not (set_idx >= 0 and set_idx < self.__data['no_sets'] and
                    team_idx in range(2))):
                return False

            return getRace(self.__data['players'][team_idx][set_idx]['race'])

        except Exception:
            return False

    def setLabel(self, set_idx, label):
        """Set a map label."""
        try:
            if(not (set_idx >= 0 and set_idx < self.__data['no_sets'])):
                return False
            if(self.__data['sets'][set_idx]['label'] != label):
                self.__data['sets'][set_idx]['label'] = label
                self.__setsChanged[set_idx] = True
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
            self.__metaChanged = True
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
            self.__metaChanged = True

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

    def setID(self, id):
        """Set match id."""
        self.__data['id'] = int(id)
        self.__matchGrabber.setID(id)
        return True

    def getID(self):
        """Get match id."""
        return int(self.__data['id'])

    def setLeague(self, league):
        """Set league."""
        league = str(league)
        if(self.__data['league'] != league):
            self.__data['league'] = league
            self.__metaChanged = True
        return True

    def getLeague(self):
        """Get league."""
        return self.__data['league']

    def setURL(self, url):
        """Set URL."""
        self.__data['matchlink'] = str(url)
        return True

    def getURL(self):
        """Get league."""
        return str(self.__data['matchlink'])

    def setProvider(self, provider):
        """Set the provider."""
        provider_changed = False
        if(provider):
            matches = difflib.get_close_matches(
                provider, self.__VALID_PROVIDERS.keys(), 1)
            if(len(matches) == 0):
                new = MatchGrabber._provider
            else:
                new = matches[0]

            if(self.__data['provider'] != new):
                self.__data['provider'] = new
                self.__metaChanged = True
                provider_changed = True
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
        self.setURL(self.__matchGrabber.getURL())

    def downloadBanner(self):
        """Download the match banner via a provider."""
        self.__matchGrabber.downloadBanner()

    def downloadLogos(self):
        """Grab the team logos via a provider."""
        self.__matchGrabber.downloadLogos(self.__controller.logoManager)

    def createOBStxtFiles(self):
        """Create OBS txt files."""
        try:

            if(self.hasAnySetChanged()):
                f = open(scctool.settings.getAbsPath(
                    scctool.settings.OBSdataDir +
                    "/lineup.txt"),
                    mode='w', encoding='utf-8-sig')
                f2 = open(scctool.settings.getAbsPath(
                    scctool.settings.OBSdataDir +
                    "/maps.txt"),
                    mode='w', encoding='utf-8-sig')
                for idx in range(self.getNoSets()):
                    map = self.getMap(idx)
                    f.write(map + "\n")
                    f2.write(map + "\n")
                    try:
                        string = self.getPlayer(
                            0, idx) + ' vs ' + self.getPlayer(1, idx)
                        f.write(string + "\n\n")
                    except IndexError:
                        f.write("\n\n")
                        pass
                f.close()
                f2.close()

                try:
                    score = self.getScore()
                    score_str = str(score[0]) + " - " + str(score[1])
                except Exception:
                    score_str = "0 - 0"

                f = open(scctool.settings.getAbsPath(
                    scctool.settings.OBSdataDir +
                    "/score.txt"), mode='w',
                    encoding='utf-8-sig')
                f.write(score_str)
                f.close()

                f = open(scctool.settings.getAbsPath(
                    scctool.settings.OBSdataDir +
                    "/nextplayer1.txt"), mode='w',
                    encoding='utf-8-sig')
                f.write(self.getNextPlayer(0))
                f.close()

                f = open(scctool.settings.getAbsPath(
                    scctool.settings.OBSdataDir +
                    "/nextplayer2.txt"), mode='w',
                    encoding='utf-8-sig')
                f.write(self.getNextPlayer(1))
                f.close()

                f = open(scctool.settings.getAbsPath(
                    scctool.settings.OBSdataDir +
                    "/nextrace1.txt"), mode='w',
                    encoding='utf-8-sig')
                f.write(self.getNextRace(0))
                f.close()

                f = open(scctool.settings.getAbsPath(
                    scctool.settings.OBSdataDir +
                    "/nextrace2.txt"), mode='w',
                    encoding='utf-8-sig')
                f.write(self.getNextRace(1))
                f.close()

            if(self.hasMetaChanged()):

                f = open(scctool.settings.getAbsPath(
                    scctool.settings.OBSdataDir +
                    "/teams_vs_long.txt"),
                    mode='w', encoding='utf-8-sig')
                f.write(self.getTeam(0) + ' vs ' + self.getTeam(1) + "\n")
                f.close()

                f = open(scctool.settings.getAbsPath(
                    scctool.settings.OBSdataDir +
                    "/teams_vs_short.txt"),
                    mode='w', encoding='utf-8-sig')
                f.write(self.getTeamTag(0) + ' vs ' +
                        self.getTeamTag(1) + "\n")
                f.close()

                f = open(scctool.settings.getAbsPath(
                    scctool.settings.OBSdataDir +
                    "/team1.txt"),
                    mode='w', encoding='utf-8-sig')
                f.write(self.getTeam(0))
                f.close()

                f = open(scctool.settings.getAbsPath(
                    scctool.settings.OBSdataDir +
                    "/team2.txt"),
                    mode='w', encoding='utf-8-sig')
                f.write(self.getTeam(1))
                f.close()

                f = open(scctool.settings.getAbsPath(
                    scctool.settings.OBSdataDir +
                    "/tournament.txt"),
                    mode='w', encoding='utf-8-sig')
                f.write(self.getLeague())
                f.close()

        except Exception as e:
            module_logger.exception("message")

    def getScoreData(self):
        data = dict()

        if self.getSolo():
            data['team1'] = self.getPlayer(0, 0)
            data['team2'] = self.getPlayer(1, 0)
        else:
            data['team1'] = self.getTeam(0)
            data['team2'] = self.getTeam(1)

        data['logo1'] = self.__controller.logoManager.getTeam1().getFile(True)
        data['logo2'] = self.__controller.logoManager.getTeam2().getFile(True)

        score = [0, 0]
        winner = [False, False]
        sets = []
        threshold = int(self.getBestOf() / 2)

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
        data['winner'] = winner
        data['score1'] = score[0]
        data['score2'] = score[1]

        return data

    def getScoreIconColor(self, team_idx, set_idx):
        score = self.getMapScore(set_idx)
        team = 2 * team_idx - 1
        if score == 0:
            if max(self.getScore()) > int(self.getBestOf() / 2):
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

    def getBorderColor(self, set_idx):
        score = self.getMapScore(set_idx)
        team = self.getMyTeam()
        won = score * team
        if max(self.getScore()) > int(self.getBestOf() / 2):
            return scctool.settings.config.parser.get(
                "MapIcons",
                "notplayed_color")
        elif won == 1:
            return scctool.settings.config.parser.get(
                "MapIcons",
                "win_color")
        elif won == -1:
            return scctool.settings.config.parser.get(
                "MapIcons",
                "lose_color")
        else:
            return scctool.settings.config.parser.get(
                "MapIcons",
                "default_border_color")

    def getMapIconsData(self):
        """Update map icons."""
        websocket_data = dict()
        try:
            team = self.getMyTeam()
            score = [0, 0]

            if(team == 0):
                landscape_score_hide = ";display: none"
            else:
                landscape_score_hide = ""

            for i in range(self.getNoSets()):
                winner = self.getMapScore(i)
                won = winner * team
                opacity = "0.0"

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
                data['map_name'] = self.getMap(i)
                data['map_id'] = self.getLabel(i)
                data['score_color'] = score_color + landscape_score_hide
                data['border_color'] = border_color
                data['opacity'] = opacity
                data['status1'] = player1status
                data['status2'] = player2status

                websocket_data[i + 1] = data

        except Exception as e:
            module_logger.exception("message")

        return websocket_data

    def updateMapIcons(self):
        """Update map icons."""
        websocket_data = dict()
        try:
            team = self.getMyTeam()
            score = [0, 0]
            skip = [False] * self.getNoSets()
            meta_changed = self.hasMetaChanged()

            if(team == 0):
                landscape_score_hide = ";display: none"
            else:
                landscape_score_hide = ""

            for i in range(self.getNoSets()):
                winner = self.getMapScore(i)
                won = winner * team
                opacity = "0.0"

                threshold = int(self.getBestOf() / 2)
                if(not self.hasSetChanged(i) and not meta_changed):
                    skip[i] = True

                if(max(score) > threshold and i >= self.getMinSets()):
                    border_color = scctool.settings.config.parser.get(
                        "MapIcons", "notplayed_color")
                    score_color = scctool.settings.config.parser.get(
                        "MapIcons", "notplayed_color")
                    opacity = scctool.settings.config.parser.get(
                        "MapIcons", "notplayed_opacity")
                    winner = 0
                    skip[i] = False
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

                if(skip[i]):
                    continue

                data = dict()
                data['player1'] = self.getPlayer(0, i)
                data['player2'] = self.getPlayer(1, i)
                data['race1'] = self.getRace(0, i).lower()
                data['race2'] = self.getRace(1, i).lower()
                data['map_img'] = self.__controller.getMapImg(self.getMap(i))
                data['map_name'] = self.getMap(i)
                data['map_id'] = self.getLabel(i)
                data['score_color'] = score_color + landscape_score_hide
                data['border_color'] = border_color
                data['opacity'] = opacity
                data['status1'] = player1status
                data['status2'] = player2status

                websocket_data[i + 1] = data
                data['vars'] = "--winner-color: {};".format(
                    scctool.settings.config.parser.get(
                        "MapIcons", "winner_highlight_color"))
                if scctool.settings.config.parser.getboolean(
                        "Style", "use_custom_font"):
                    data['font'] = "font-family: {};".format(
                        scctool.settings.config.parser.get("Style",
                                                           "custom_font"))

                dataFile = scctool.settings.OBSmapDir + \
                    "/icons_box/data/" + str(i + 1) + ".html"
                templateFile = scctool.settings.OBSmapDir + \
                    "/icons_box/data/template.html"

                self._useTemplate(templateFile, dataFile, data)

                dataFile = scctool.settings.OBSmapDir + \
                    "/icons_landscape/data/" + str(i + 1) + ".html"
                templateFile = scctool.settings.OBSmapDir + \
                    "/icons_landscape/data/template.html"

                self._useTemplate(templateFile, dataFile, data)

            for i in range(self.getNoSets(), scctool.settings.max_no_sets):
                data = dict()
                data['hidden'] = 'visibility: hidden;'
                if scctool.settings.config.parser.getboolean(
                        "Style", "use_custom_font"):
                    data['font'] = "font-family: {};".format(
                        scctool.settings.config.parser.get("Style",
                                                           "custom_font"))
                dataFile = scctool.settings.OBSmapDir + \
                    "/icons_box/data/" + str(i + 1) + ".html"
                templateFile = scctool.settings.OBSmapDir +\
                    "/icons_box/data/template.html"
                self._useTemplate(templateFile, dataFile, data)

                dataFile = scctool.settings.OBSmapDir + \
                    "/icons_landscape/data/" + str(i + 1) + ".html"
                templateFile = scctool.settings.OBSmapDir + \
                    "/icons_landscape/data/template.html"
                self._useTemplate(templateFile, dataFile, data)

            # self.__controller.websocketThread.sendData2Path(
            #     'mapicons_box', 'DATA', websocket_data)

        except Exception as e:
            module_logger.exception("message")

    def updateLeagueIcon(self):
        """Update league icon."""
        if(not self.hasMetaChanged()):
            return

        try:
            filename_old = scctool.settings.OBShtmlDir + "/data/" + \
                self.getProvider() + ".html"
            filename_new = scctool.settings.OBShtmlDir + \
                "/data/league-data.html"
            shutil.copy(scctool.settings.getAbsPath(filename_old),
                        scctool.settings.getAbsPath(filename_new))

        except Exception as e:
            module_logger.exception("message")

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

        except Exception as e:
            module_logger.exception("message")
            return False

    def _useTemplate(self, filein, fileout, replacements):
        filein = scctool.settings.getAbsPath(filein)
        fileout = scctool.settings.getAbsPath(fileout)
        regex = re.compile(r"%[\w_-]+%")
        compiled_replacements = dict()
        for placeholder, value in replacements.items():
            compiled_replacements['%{}%'.format(
                placeholder.upper())] = str(value)
        with open(filein, "rt", encoding='utf-8-sig') as fin:
            with open(fileout, "wt", encoding='utf-8-sig') as fout:
                for line in fin:
                    for placeholder, value in compiled_replacements.items():
                        line = line.replace(placeholder, value)
                    line = regex.sub("", line)
                    fout.write(line)


def autoCorrectMap(map):
    """Corrects map using list in config."""
    if not isinstance(map, str):
        map = "TBD"
    try:
        matches = difflib.get_close_matches(
            map.lower(), scctool.settings.maps, 1)
        if(len(matches) == 0):
            return map, False
        else:
            return matches[0], True

    except Exception as e:
        module_logger.exception("message")


def getRace(str):
    """Get race by using the first letter."""
    try:
        for idx, race in enumerate(scctool.settings.races):
            if(str[0].upper() == race[0].upper()):
                return scctool.settings.races[idx]
    except Exception:
        pass

    return "Random"


class EmitLock():
    def __init__(self):
        self.__locked = False
        self.__useLock = True
        self.__signal = None

    def __call__(self, useLock=True, signal=None):
        self.__useLock = bool(useLock)
        self.__signal = signal
        return self

    def __enter__(self):
        self.__locked = self.__useLock
        return self

    def __exit__(self, type, value, traceback):
        self.__locked = False
        if self.__useLock and self.__signal:
            self.__signal.emit()

    def locked(self):
        return bool(self.__locked)
