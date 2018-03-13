"""Matchdata."""
import logging

# create logger
module_logger = logging.getLogger('scctool.matchdata')

try:
    import scctool.settings
    import json
    import re
    import time
    import difflib
    import shutil
    from scctool.matchgrabber import MatchGrabber
    from scctool.matchgrabber.alpha import MatchGrabber as MatchGrabberAlpha
    from scctool.matchgrabber.rstl import MatchGrabber as MatchGrabberRSTL

except Exception as e:
    module_logger.exception("message")
    raise


class matchData:
    """Matchdata."""

    def __init__(self, controller):
        """Init and define custom providers."""
        self.__VALID_PROVIDERS = ['Custom', 'AlphaSC2', 'RSTL']
        self.__rawData = None
        self.__controller = controller
        self.__initData()
        self.__initMatchGrabber()

    def __initMatchGrabber(self):
        provider = self.getProvider()
        (*args,) = (self, self.__controller)

        if(provider == "AlphaSC2"):
            self.__matchGrabber = MatchGrabberAlpha(*args)
        elif(provider == "RSTL"):
            self.__matchGrabber = MatchGrabberRSTL(*args)
        else:
            self.__matchGrabber = MatchGrabber(*args)

    def readJsonFile(self):
        """Read json data from file."""
        try:
            with open(scctool.settings.matchdata_json_file) as json_file:
                self.__data = json.load(json_file)
        except Exception as e:
            # module_logger.exception("message")
            self.setCustom(5, False, False)
        self.allSetsChanged()

    def writeJsonFile(self):
        """Write json data to file."""
        try:
            with open(scctool.settings.matchdata_json_file, 'w') as outfile:
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
            self.setProvider("AlphaSC2")
        elif(url.find('hdgame') != -1):
            self.setProvider("RSTL")
        else:
            self.setProvider("Custom")

        self.setID(re.findall('\d+', url)[-1])
    # except Exception as e:
        # self.setProvider("Custom")
        # self.setID(0)
        # module_logger.exception("message")

    def __initData(self):
        self.__data = {}
        self.__data['provider'] = self.__VALID_PROVIDERS[0]
        self.__data['league'] = "TBD"
        self.__data['id'] = 0
        self.__data['matchlink'] = ""
        self.__data['no_sets'] = 0
        self.__data['best_of'] = 0
        self.__data['min_sets'] = 0
        self.__data['allkill'] = False
        self.__data['solo'] = False
        self.__data['my_team'] = 0
        self.__data['teams'] = []
        self.__data['teams'].append({'name': 'TBD', 'tag': None})
        self.__data['teams'].append({'name': 'TBD', 'tag': None})
        self.__data['sets'] = []
        self.__data['players'] = [[], []]

        self.__setsChanged = []
        self.__metaChanged = False

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
                    return False
                team_idx = int((self.getMapScore(set_idx - 1) + 1) / 2)
                if(self.getPlayer(team_idx, set_idx) != "TBD"):
                    return False
                self.setPlayer(team_idx, set_idx, self.getPlayer(team_idx, set_idx - 1),
                               self.getRace(team_idx, set_idx - 1))
                return True

        return False

    def setCustom(self, bestof, allkill, solo):
        """Set a custom match format."""
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

    def resetData(self):
        """Reset all data to default values."""
        for team_idx in range(2):
            for set_idx in range(self.getNoSets()):
                self.setPlayer(team_idx, set_idx, "TBD", "Random")
            self.setTeam(team_idx, "TBD", "TBD")

        for set_idx in range(self.getNoSets()):
            self.setMapScore(set_idx, 0)
            self.setMap(set_idx)

        self.setLeague("TBD")
        self.setMyTeam(0)
        self.setAllKill(False)
        self.setSolo(False)

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

        for set_idx in range(ace_start):
            self.setLabel(set_idx, "Map " + str(set_idx + 1))

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

    def setMyTeam(self, myteam):
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

    def getMyTeam(self):
        """Return my team: (-1,0,1)."""
        try:
            return int(self.__data['my_team'])
        except Exception:
            return 0

    def __selectMyTeam(self, string):
        teams = [self.getTeam(0).lower(), self.getTeam(1).lower()]
        matches = difflib.get_close_matches(string.lower(), teams, 1)
        if(len(matches) == 0):
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

    def setMapScore(self, set_idx, score, overwrite=False):
        """Set the score of a set."""
        try:
            if(not (set_idx >= 0 and set_idx < self.__data['no_sets'])):
                return False
            if(score in [-1, 0, 1]):
                if(overwrite or self.__data['sets'][set_idx]['score'] == 0):
                    if(self.__data['sets'][set_idx]['score'] != score):
                        if(self.isDecided()):
                            self.__metaChanged = True
                        self.__data['sets'][set_idx]['score'] = score
                        self.__setsChanged[set_idx] = True
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
            if(not (set_idx >= 0 and set_idx < self.__data['no_sets']
                    and team_idx in range(2))):
                return False

            if(self.__data['players'][team_idx][set_idx]['name'] != name):
                self.__data['players'][team_idx][set_idx]['name'] = name
                self.__setsChanged[set_idx] = True

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
            if(not (set_idx >= 0 and set_idx < self.__data['no_sets']
                    and team_idx in range(2))):
                return False

            return self.__data['players'][team_idx][set_idx]['name']

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
                self.__setsChanged[set_idx] = True
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

    def setLabel(self, set_idx, label):
        """Set a map label."""
        try:
            if(not (set_idx >= 0 and set_idx < self.__data['no_sets'])):
                return False
            if(self.__data['sets'][set_idx]['label'] != label):
                self.__data['sets'][set_idx]['label'] = label
                self.__setsChanged[set_idx] = True
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

        new = str(name)

        if(self.__data['teams'][team_idx]['name'] != new):
            self.__data['teams'][team_idx]['name'] = new
            self.__metaChanged = True

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
        if(provider):
            matches = difflib.get_close_matches(
                provider, self.__VALID_PROVIDERS, 1)
            if(len(matches) == 0):
                new = self.__VALID_PROVIDERS[0]
            else:
                new = matches[0]

            if(self.__data['provider'] != new):
                self.__data['provider'] = new
                self.__metaChanged = True
        else:
            self.__data['provider'] = self.__VALID_PROVIDERS[0]

        self.__initMatchGrabber()
        return True

    def getProvider(self):
        """Get the provider."""
        return str(self.__data['provider'])

    def grabData(self):
        """Grab the match data via a provider."""
        self.__matchGrabber.grabData()
        self.setURL(self.__matchGrabber.getURL())

    def downloadBanner(self):
        """Download the match banner via a provider."""
        self.__matchGrabber.downloadBanner()

    def downloadLogos(self):
        """Grab the team logos via a provider."""
        self.__matchGrabber.downloadLogos()

    def createOBStxtFiles(self):
        """Create OBS txt files."""
        try:
            files2upload = []

            if(self.hasAnySetChanged()):
                files2upload = files2upload + ["lineup.txt",
                                               "maps.txt",
                                               "score.txt",
                                               "nextplayer1.txt",
                                               "nextplayer2.txt",
                                               "nextrace1.txt",
                                               "nextrace2.txt"]
                f = open(scctool.settings.getAbsPath(scctool.settings.OBSdataDir +
                                                     "/lineup.txt"),
                         mode='w', encoding='utf-8-sig')
                f2 = open(scctool.settings.getAbsPath(scctool.settings.OBSdataDir +
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

                f = open(scctool.settings.getAbsPath(scctool.settings.OBSdataDir +
                                                     "/score.txt"), mode='w',
                         encoding='utf-8-sig')
                f.write(score_str)
                f.close()

                f = open(scctool.settings.getAbsPath(scctool.settings.OBSdataDir +
                                                     "/nextplayer1.txt"), mode='w',
                         encoding='utf-8-sig')
                f.write(self.getNextPlayer(0))
                f.close()

                f = open(scctool.settings.getAbsPath(scctool.settings.OBSdataDir +
                                                     "/nextplayer2.txt"), mode='w',
                         encoding='utf-8-sig')
                f.write(self.getNextPlayer(1))
                f.close()

                f = open(scctool.settings.getAbsPath(scctool.settings.OBSdataDir +
                                                     "/nextrace1.txt"), mode='w',
                         encoding='utf-8-sig')
                f.write(self.getNextRace(0))
                f.close()

                f = open(scctool.settings.getAbsPath(scctool.settings.OBSdataDir +
                                                     "/nextrace2.txt"), mode='w',
                         encoding='utf-8-sig')
                f.write(self.getNextRace(1))
                f.close()

            if(self.hasMetaChanged()):

                files2upload = files2upload + \
                    ["teams_vs_long.txt", "teams_vs_short.txt",
                        "team1.txt", "team2.txt", "tournament.txt"]

                f = open(scctool.settings.getAbsPath(scctool.settings.OBSdataDir +
                                                     "/teams_vs_long.txt"),
                         mode='w', encoding='utf-8-sig')
                f.write(self.getTeam(0) + ' vs ' + self.getTeam(1) + "\n")
                f.close()

                f = open(scctool.settings.getAbsPath(scctool.settings.OBSdataDir +
                                                     "/teams_vs_short.txt"),
                         mode='w', encoding='utf-8-sig')
                f.write(self.getTeamTag(0) + ' vs ' +
                        self.getTeamTag(1) + "\n")
                f.close()

                f = open(scctool.settings.getAbsPath(scctool.settings.OBSdataDir +
                                                     "/team1.txt"),
                         mode='w', encoding='utf-8-sig')
                f.write(self.getTeam(0))
                f.close()

                f = open(scctool.settings.getAbsPath(scctool.settings.OBSdataDir +
                                                     "/team2.txt"),
                         mode='w', encoding='utf-8-sig')
                f.write(self.getTeam(1))
                f.close()

                f = open(scctool.settings.getAbsPath(scctool.settings.OBSdataDir +
                                                     "/tournament.txt"),
                         mode='w', encoding='utf-8-sig')
                f.write(self.getLeague())
                f.close()

            if(len(files2upload) > 0):
                self.__controller.ftpUploader.cwd(scctool.settings.OBSdataDir)
                for file in files2upload:
                    self.__controller.ftpUploader.upload(
                        scctool.settings.OBSdataDir + "/" + file, file)

                self.__controller.ftpUploader.cwd("..")

        except Exception as e:
            module_logger.exception("message")

    def updateScoreIcon(self):
        """Update scor icons."""
        if(not(self.hasMetaChanged() or self.hasAnySetChanged())):
            return

        score = [0, 0]
        display = []
        winner = ["", ""]
        border_color = [[], []]
        threshold = int(self.getBestOf() / 2)

        for i in range(self.getNoSets()):
            display.append("inline-block")

            if(max(score) > threshold and i >= self.getMinSets()):
                border_color[0].append(scctool.settings.config.parser.get(
                    "MapIcons", "notplayed_color"))
                border_color[1].append(scctool.settings.config.parser.get(
                    "MapIcons", "notplayed_color"))
            elif(self.getMapScore(i) == -1):
                border_color[0].append(
                    scctool.settings.config.parser.get("MapIcons", "win_color"))
                border_color[1].append(
                    scctool.settings.config.parser.get("MapIcons", "lose_color"))
                score[0] += 1
            elif(self.getMapScore(i) == 1):
                border_color[0].append(
                    scctool.settings.config.parser.get("MapIcons", "lose_color"))
                border_color[1].append(
                    scctool.settings.config.parser.get("MapIcons", "win_color"))
                score[1] += 1
            else:
                border_color[0].append(scctool.settings.config.parser.get(
                    "MapIcons", "undecided_color"))
                border_color[1].append(scctool.settings.config.parser.get(
                    "MapIcons", "undecided_color"))

        for i in range(self.getNoSets(), scctool.settings.max_no_sets):
            display.append("none")
            border_color[0].append(scctool.settings.config.parser.get(
                "MapIcons", "notplayed_color"))
            border_color[1].append(scctool.settings.config.parser.get(
                "MapIcons", "notplayed_color"))

        if(score[0] > threshold):
            winner[0] = "winner"
        elif(score[1] > threshold):
            winner[1] = "winner"

        logo1 = self.__controller.linkFile(
            scctool.settings.OBSdataDir + "/logo1")
        if logo1 == "":
            logo1 = scctool.settings.OBShtmlDir + "/src/SC2.png"

        logo2 = self.__controller.linkFile(
            scctool.settings.OBSdataDir + "/logo2")
        if logo2 == "":
            logo2 = scctool.settings.OBShtmlDir + "/src/SC2.png"

        filename = scctool.settings.getAbsPath(
            scctool.settings.OBShtmlDir + "/data/score-data.html")
        with open(scctool.settings.getAbsPath(scctool.settings.OBShtmlDir +
                                              "/data/score-template.html"),
                  "rt", encoding='utf-8-sig') as fin:
            with open(filename, "wt", encoding='utf-8-sig') as fout:
                for line in fin:
                    if self.getSolo():
                        line = line.replace('%TEAM1%', self.getPlayer(
                            0, 0)).replace('%TEAM2%', self.getPlayer(1, 0))
                    else:
                        line = line.replace('%TEAM1%', self.getTeam(
                            0)).replace('%TEAM2%', self.getTeam(1))
                    line = line.replace('%LOGO1%', logo1).replace(
                        '%LOGO2%', logo2)
                    line = line.replace('%WINNER1%', winner[0]).replace(
                        '%WINNER2%', winner[1])
                    line = line.replace('%SCORE-T1%', str(score[0]))
                    line = line.replace('%SCORE-T2%', str(score[1]))
                    line = line.replace('%SCORE%', str(
                        score[0]) + ' - ' + str(score[1]))
                    line = line.replace('%TIMESTAMP%', str(time.time()))
                    for i in range(scctool.settings.max_no_sets):
                        line = line.replace(
                            '%SCORE-M' + str(i + 1) + '-T1%', border_color[0][i])
                        line = line.replace(
                            '%SCORE-M' + str(i + 1) + '-T2%', border_color[1][i])
                        line = line.replace(
                            '%DISPLAY-M' + str(i + 1) + '%', display[i])
                    fout.write(line)

        self.__controller.ftpUploader.cwd(
            scctool.settings.OBShtmlDir + "/data")
        self.__controller.ftpUploader.upload(filename, "score-data.html")
        self.__controller.ftpUploader.cwd("../../..")

    def updateMapIcons(self):
        """Update map icons."""
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
                player1 = self.getPlayer(0, i)
                player2 = self.getPlayer(1, i)

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

                map = self.getMap(i)
                mappng = self.__controller.getMapImg(map)
                race1png = self.getRace(0, i) + ".png"
                race2png = self.getRace(1, i) + ".png"
                hidden = ""

                filename = scctool.settings.getAbsPath(scctool.settings.OBSmapDir +
                                                       "/icons_box/data/"
                                                       + str(i + 1) + ".html")
                filename2 = scctool.settings.getAbsPath(scctool.settings.OBSmapDir +
                                                        "/icons_landscape/data/"
                                                        + str(i + 1) + ".html")
                with open(scctool.settings.getAbsPath(scctool.settings.OBSmapDir +
                                                      "/icons_box/data/template.html"),
                          "rt", encoding='utf-8-sig') as fin:
                    with open(filename, "wt", encoding='utf-8-sig') as fout:
                        for line in fin:
                            line = line.replace('%PLAYER1%', player1).replace(
                                '%PLAYER2%', player2)
                            line = line.replace('%RACE1_PNG%', race1png).replace(
                                '%RACE2_PNG%', race2png)
                            line = line.replace('%MAP_PNG%', mappng).replace(
                                '%MAP_NAME%', map)
                            line = line.replace('%MAP_ID%', self.getLabel(i))
                            line = line.replace('%BORDER_COLOR%', border_color).replace(
                                '%OPACITY%', opacity)
                            line = line.replace('%HIDDEN%', hidden)
                            line = line.replace('%STATUS1%', player1status).replace(
                                '%STATUS2%', player2status)
                            fout.write(line)

                with open(scctool.settings.getAbsPath(scctool.settings.OBSmapDir +
                                                      "/icons_landscape/data/template.html"),
                          "rt", encoding='utf-8-sig') as fin:
                    with open(filename2, "wt", encoding='utf-8-sig') as fout:
                        for line in fin:
                            line = line.replace('%PLAYER1%', player1).replace(
                                '%PLAYER2%', player2)
                            line = line.replace('%RACE1_PNG%', race1png).replace(
                                '%RACE2_PNG%', race2png)
                            line = line.replace('%MAP_PNG%', mappng).replace(
                                '%MAP_NAME%', map)
                            line = line.replace('%MAP_ID%', self.getLabel(i))
                            line = line.replace('%SCORE_COLOR%',
                                                score_color + landscape_score_hide)
                            line = line.replace('%OPACITY%', opacity)
                            line = line.replace('%HIDDEN%', hidden)
                            line = line.replace('%STATUS1%', player1status).replace(
                                '%STATUS2%', player2status)
                            fout.write(line)

            for i in range(self.getNoSets(), scctool.settings.max_no_sets):
                filename = scctool.settings.getAbsPath(scctool.settings.OBSmapDir +
                                                       "/icons_box/data/" + str(i + 1) +
                                                       ".html")
                filename2 = scctool.settings.getAbsPath(scctool.settings.OBSmapDir +
                                                        "/icons_landscape/data/" + str(i + 1) +
                                                        ".html")
                hidden = "visibility: hidden;"
                with open(scctool.settings.getAbsPath(scctool.settings.OBSmapDir +
                                                      "/icons_box/data/template.html"),
                          "rt", encoding='utf-8-sig') as fin:
                    with open(filename, "wt", encoding='utf-8-sig') as fout:
                        for line in fin:
                            line = line.replace('%HIDDEN%', hidden)
                            fout.write(line)

                with open(scctool.settings.getAbsPath(scctool.settings.OBSmapDir +
                                                      "/icons_landscape/data/template.html"),
                          "rt") as fin:
                    with open(filename2, "wt", encoding='utf-8-sig') as fout:
                        for line in fin:
                            line = line.replace('%HIDDEN%', hidden)
                            fout.write(line)

            if(False in skip or self.hasMetaChanged()):
                self.__controller.ftpUploader.cwd(scctool.settings.OBSmapDir)
                for type in ["box", "landscape"]:
                    self.__controller.ftpUploader.cwd(
                        "icons_" + type + "/data")
                    for i in range(scctool.settings.max_no_sets):
                        if(i < self.getNoSets() and skip[i]):
                            continue
                        if(i >= self.getNoSets() and not self.hasMetaChanged()):
                            continue
                        filename = scctool.settings.OBSmapDir + "/icons_" + \
                            type + "/data/" + str(i + 1) + ".html"
                        self.__controller.ftpUploader.upload(
                            filename, str(i + 1) + ".html")
                    self.__controller.ftpUploader.cwd("../..")
                self.__controller.ftpUploader.cwd("..")

        except Exception as e:
            module_logger.exception("message")

    def updateLeagueIcon(self):
        """Update league icon."""
        if(not self.hasMetaChanged()):
            return

        try:
            filename_old = scctool.settings.OBShtmlDir + "/data/" + self.getProvider() + \
                ".html"
            filename_new = scctool.settings.OBShtmlDir + "/data/league-data.html"
            shutil.copy(scctool.settings.getAbsPath(filename_old),
                        scctool.settings.getAbsPath(filename_new))
            self.__controller.ftpUploader.cwd(
                scctool.settings.OBShtmlDir + "/data")
            self.__controller.ftpUploader.upload(
                filename_new, "league-data.html")
            self.__controller.ftpUploader.cwd("../..")

        except Exception as e:
            module_logger.exception("message")

    def autoSetMyTeam(self):
        """Try to set team via fav teams."""
        try:
            for team_idx in range(2):
                team = self.__data['teams'][team_idx]['name']
                matches = difflib.get_close_matches(
                    team.lower(), scctool.settings.config.getMyTeams(), 1)
                if(len(matches) > 0):
                    self.setMyTeam(team_idx * 2 - 1)
                    return True

            self.setMyTeam(0)

            return False

        except Exception as e:
            module_logger.exception("message")
            return False


def autoCorrectMap(map):
    """Corrects map using list in config."""
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
