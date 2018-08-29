"""Interact with SC2-Client via thread."""
import logging
import os.path
import re
import time
from difflib import SequenceMatcher

import keyboard
import requests
from PyQt5.QtCore import QThread, pyqtSignal

import scctool.settings

# create logger
module_logger = logging.getLogger(__name__)

if(scctool.settings.windows):
    from PIL import ImageGrab  # pip install Pillow
    import pytesseract  # pip install pytesseract
    from win32gui import GetWindowText, GetForegroundWindow


def skipScore(score):
    return score == 0


def skipBestOf(bo):
    return bo == 3


def ToggleScore(score1=0, score2=0, bestof=5):
    """Set and toggle SC2-ingame score."""

    if scctool.settings.config.parser.getboolean("SCT", "CtrlShiftS"):
        keyboard.send("ctrl+shift+s")

    if scctool.settings.config.parser.getboolean("SCT", "CtrlShiftC"):
        keyboard.send("ctrl+shift+c")

    times = scctool.settings.config.parser.getint("SCT", "CtrlShiftR")
    if times > 0:
        # For some reason the first time pressing CTRL+SHIFT+R does nothing.
        for x in range(0, times + 1):
            keyboard.send("ctrl+shift+r")

    if(not skipBestOf(bestof)):
        keyboard.send("ctrl+shift+{}".format(bestof))

    if(not skipScore(score2)):
        keyboard.send("ctrl+{}".format(score2))

    if(not skipScore(score1)):
        keyboard.send("shift+{}".format(score1))


def TogglePlayerNames():
    """Toggle Score ahead of OCR."""
    if scctool.settings.config.parser.getboolean("SCT", "CtrlN"):
        keyboard.send("ctrl+n")


def SwapPlayerNames():
    """Toggle Score ahead of OCR."""
    keyboard.send("ctrl+x")


def ToggleProduction():
    """Toggle SC2-ingame production tab."""
    keyboard.send("d")


class SC2ApiThread(QThread):
    """Thread to interact with SC2-Client."""

    requestScoreUpdate = pyqtSignal(object)

    def __init__(self, controller, parent=None):
        """Init thread."""
        try:
            QThread.__init__(self, parent)
            self.exiting = False
            self.activeTask = {}
            self.activeTask['updateScore'] = False
            self.activeTask['toggleScore'] = False
            self.activeTask['toggleProduction'] = False
            self.activeTask['playerIntros'] = False
            self.activeTask['playerLogos'] = False
            self.currentData = SC2MatchData()
            self.introData = SC2MatchData()
            self.controller = controller
            self.currentÍngameStatus = False
        except Exception as e:
            module_logger.exception("message")

    def startTask(self, task):
        """Start a task in thread."""
        try:
            self.activeTask[task] = True
            self.start()
        except Exception as e:
            module_logger.exception("message")

    def requestTermination(self, task):
        """Request termination of a task in thread."""
        try:
            if(task == 'ALL'):
                for task in self.activeTask:
                    self.activeTask[task] = False
            else:
                self.activeTask[task] = False
                module_logger.info(
                    'Requesting termination of task "' + task + '"')

            if(not any(self.activeTask.values())):
                self.exiting = True
                module_logger.info('Requesting termination of thread')
        except Exception as e:
            module_logger.exception("message")

    def cancelTerminationRequest(self, task):
        """Cancel the request to terminate a task."""
        self.activeTask[task] = True
        self.exiting = False
        module_logger.info(
            'Termination request fo task "' + task + '" cancelled')

    def run(self):
        """Run the thread."""
        try:
            module_logger.info("Start Sc2 Interation Thread")
            self.exiting = False

            GAMEurl = "http://localhost:6119/game"
            UIurl = "http://localhost:6119/ui"

            while self.exiting is False:
                # See: https://us.battle.net/forums/en/sc2/topic/20748195420
                try:
                    GAMEresponse = requests.get(GAMEurl, timeout=30).json()
                    # activate script if 2 players are playing right now
                    if(len(GAMEresponse["players"]) == 2):
                        UIresponse = requests.get(UIurl, timeout=30).json()
                        self.parseMatchData(
                            SC2MatchData(GAMEresponse, UIresponse))

                except requests.exceptions.ConnectionError:
                    time.sleep(10)
                except ValueError:
                    time.sleep(10)

                time.sleep(1)

        except Exception as e:
            module_logger.exception("message")

    def parseMatchData(self, newData):
        """Parse SC2-Client-API data and run tasks accordingly."""
        try:
            if(not self.exiting and self.activeTask['playerIntros'] and
               self.introData != newData):
                self.controller.updatePlayerIntros(newData)
                self.introData = newData

            if(not self.exiting and
                (newData != self.currentData or
                 newData.time < self.currentData.time or
                 newData.isLive() != self.currentData.isLive())):

                if(self.activeTask['updateScore'] and
                   newData.isDecidedGame() and
                   self.currentData != SC2MatchData()):
                    self.requestScoreUpdate.emit(newData)

                if(newData.isLive() and (self.activeTask['toggleScore'] or
                                         self.activeTask['toggleProduction'] or
                                         self.activeTask['playerLogos'])):
                    self.tryToggle(newData)

                self.currentData = newData
        except Exception as e:
            module_logger.exception("message")

    def tryToggle(self, data):
        """Wait until SC2 is in foreground and toggle"""
        """production tab and score."""
        if (scctool.settings.config.parser.getboolean(
            "SCT", "blacklist_on") and
                not data.replay):
            blacklist = scctool.settings.config.getBlacklist()
            if data.player1 in blacklist or data.player2 in blacklist:
                module_logger.info("Do not toogle due to blacklist.")
                return
        try:
            while self.exiting is False\
                and (self.activeTask['toggleScore'] or
                     self.activeTask['toggleProduction'] or
                     self.activeTask['playerLogos']):
                if(isSC2onForeground()):
                    if(self.activeTask['toggleScore'] or
                       self.activeTask['playerLogos']):
                        TogglePlayerNames()
                        swapPlayers = self.swapPlayers(
                            data, self.activeTask['playerLogos'])
                        if(self.activeTask['playerLogos']):
                            self.controller.requestScoreLogoUpdate(data,
                                                                   swapPlayers)
                        if(self.activeTask['toggleScore']):
                            self.controller.requestToggleScore(
                                data, swapPlayers)
                    if(self.activeTask['toggleProduction']):
                        ToggleProduction()
                    break
                else:
                    time.sleep(0.1)
        except Exception:
            module_logger.info("Toggle not working on this OS.")

    def swapPlayers(self, data, force=False):
        """Detect if players are swapped relative"""
        """to SC2-Client-API data via ocr."""
        try:
            if(not scctool.settings.config.parser.getboolean("SCT",
                                                             "use_ocr")):
                return False

            # Don't use OCR if the score is tied.
            score = self.controller.matchControl.activeMatch().getScore()
            if(score[0] == score[1] and
               (not scctool.settings.config.parser.getboolean(
                   "SCT", "CtrlX")) and
               not force):
                return False

            tesseract = scctool.settings.config.getTesserAct()
            pytesseract.pytesseract.tesseract_cmd = tesseract
            players = data.getPlayerList()
            full_img = ImageGrab.grab().convert('L')

            crop_regions = []
            if scctool.settings.config.parser.getboolean("SCT", "CtrlN"):
                crop_regions.append((0.3, 0.7, 0.0, 0.08))
                crop_regions.append((0.3, 0.7, 0.0, 0.14))
                crop_regions.append((0.12, 0.35, 0.88, 1.0))
                crop_regions.append((0.1, 0.4, 0.8, 1.0))
            else:
                crop_regions.append((0.12, 0.35, 0.88, 1.0))
                crop_regions.append((0.1, 0.4, 0.8, 1.0))
                crop_regions.append((0.3, 0.7, 0.0, 0.08))

            crop_regions.append((0.0, 1.0, 0.0, 1.0))

            for crop_region in crop_regions:
                img = cropImage(full_img, crop_region)
                found, swap = ocr(players, img, tesseract)
                if found:
                    break

            if found:
                module_logger.info("OCR was successfull.")
            else:
                module_logger.info("OCR was not successfull.")

            return swap

        except Exception as e:
            module_logger.exception("message")
            return False


def ocr(players, img, dir=''):
    cfg = '--psm 3 --oem 0'
    if dir:
        dir = os.path.join(os.path.dirname(dir), 'tessdata')
        cfg = cfg + ' --tessdata-dir "{}"'.format(dir)
    crop_text = pytesseract.image_to_string(img, config=cfg)
    items = re.split(r'\s+', crop_text)
    threshold = 0.35
    ratios = [0.0, 0.0]
    positions = [None, None]
    regex = re.compile(r"<[^>]+>")
    for item_idx, item in enumerate(items):
        item = regex.sub("", item)
        for player_idx, player in enumerate(players):
            ratio = SequenceMatcher(None, item.lower(), player.lower()).ratio()
            if(ratio >= max(threshold, ratios[player_idx])):
                positions[player_idx] = item_idx
                ratios[player_idx] = ratio

    found = ratios[0] > 0.0 and ratios[1] > 0.0

    if found:
        if(positions[0] > positions[1]):
            return True, True
        else:
            return True, False
    else:
        return False, False


def cropImage(full_img, crop_region):
    x1, x2, y1, y2 = crop_region
    width, height = full_img.size
    if x1 != 0.0 and x2 == 1.0 and y1 == 0.0 and y2 == 1.0:
        return full_img
    else:
        return full_img.crop((int(width * x1),
                              int(height * y1),
                              int(width * x2),
                              int(height * y2)))


def isSC2onForeground():
    """Detect if SC2-Client is the foreground window (only Windows)."""
    try:
        fg_window_name = GetWindowText(GetForegroundWindow()).lower()
        sc2 = "StarCraft II".lower()
        return fg_window_name == sc2
    except Exception as e:
        module_logger.exception("message")
        return False


class SC2MatchData:
    """Relevant SC2 data extracted from SC2-Client API."""

    def __init__(self, GAMEresponse=False, UIresponse=False):
        """Init data."""
        if(GAMEresponse):
            self.player1 = GAMEresponse["players"][0]["name"]
            self.player2 = GAMEresponse["players"][1]["name"]
            self.race1 = self.translateRace(GAMEresponse["players"][0]["race"])
            self.race2 = self.translateRace(GAMEresponse["players"][1]["race"])
            self.time = GAMEresponse["displayTime"]
            self.replay = GAMEresponse["isReplay"]
            self.ingame = UIresponse["activeScreens"] == []
            if(GAMEresponse["players"][0]["result"] == "Victory"):
                self.result = -1
            elif(GAMEresponse["players"][0]["result"] == "Defeat"):
                self.result = 1
            elif(GAMEresponse["players"][0]["result"] == "Undecided"):
                self.result = 99
            else:
                self.result = 0
        else:
            self.player1 = ""
            self.player2 = ""
            self.race1 = ""
            self.race2 = ""
            self.result = 0
            self.time = 0
            self.ingame = False
            self.replay = False

    def compare_returnScore(self, player1, player2, weak=False,
                            translator=None):
        """Fuzzy compare playernames and return order and their score."""
        player1, player2 = player1.strip(), player2.strip()
        player1_notset = not player1 or player1.lower() == "tbd"
        player2_notset = not player2 or player2.lower() == "tbd"

        if not translator:
            translator = self.__no_translator

        myplayers1 = set()
        myplayers1.add(translator(self.player1))
        myplayers1.add(self.player1)

        myplayers2 = set()
        myplayers2.add(translator(self.player2))
        myplayers2.add(self.player2)

        myplayers = [(p1, p2) for p1 in myplayers1 for p2 in myplayers2]

        if not (player1_notset or player2_notset):
            for p1, p2 in myplayers:
                if(compareStr(p1, player1) and compareStr(p2, player2)):
                    return True, True, self.result, -1
                elif(compareStr(p1, player2) and compareStr(p2, player1)):
                    return True, False, -self.result, -1
        elif weak and not (player1_notset and player2_notset):
            if player1_notset:
                noset_idx = 0
            elif player2_notset:
                noset_idx = 1
            else:
                raise ValueError

            for p1, p2 in myplayers:
                if((player1_notset and compareStr(p2, player2)) or
                   (compareStr(p1, player1) and player2_notset)):
                    return True, True, self.result, noset_idx
                elif((player1_notset and compareStr(p1, player1)) or
                     (compareStr(p2, player1) and player2_notset)):
                    return True, False, -self.result, noset_idx

        return False, False, 0, -1

    def compare_returnOrder(self, player1, player2, weak=False,
                            translator=None):
        """Fuzzy compare playernames and return the correct order."""
        found, inorder, _, _ = self.compare_returnScore(
            player1, player2, weak=weak, translator=translator)
        return found, inorder

    def __no_translator(self, x):
        return x

    def playerInList(self, player_idx, players, translator=None):
        """Fuzzy check if player is in list of players."""
        if not translator:
            translator = self.__no_translator

        myplayers = set()
        if player_idx == 0:
            myplayers.add(translator(self.player1))
            myplayers.add(self.player1)
        elif player_idx == 1:
            myplayers.add(translator(self.player2))
            myplayers.add(self.player2)
        else:
            raise ValueError

        for player in players:
            for myplayer in myplayers:
                if compareStr(player, myplayer):
                    return True

        return False

    def translateRace(self, str):
        """Translate SC2-Client-API race to no normal values."""
        try:
            for idx, race in enumerate(scctool.settings.races):
                if(str[0].upper() == race[0].upper()):
                    return scctool.settings.races[idx]
        except Exception as e:
            module_logger.exception("message")

        module_logger.info("Race " + str + " not found")
        return ""

    def isDecidedGame(self):
        """Check if the game is decided."""
        return ((self.result == 1 or self.result == -1) and self.time > 60)

    def isLive(self):
        """Check if the game is running (first 30 sec)."""
        return (self.ingame and self.result == 99 and self.time < 30)

    def isStarting(self):
        """Check if the game has started in the past 5 sec."""
        return (self.ingame and self.result == 99 and self.time < 5)

    def __str__(self):
        """Convert data to string."""
        return str(self.__dict__)

    def __eq__(self, other):
        """Compare data."""
        return (self.player1 == other.player1 and
                self.player2 == other.player2 and
                self.race1 == other.race1 and
                self.race2 == other.race2 and
                self.result == other.result)

    def getPlayerList(self):
        """Get list of players."""
        return [self.player1, self.player2]

    def getPlayer(self, idx):
        """Get player via index."""
        if(idx == 0):
            return self.player1
        elif(idx == 1):
            return self.player2
        else:
            return False

    def getRace(self, idx):
        """Get races via index."""
        if(idx == 0):
            return self.race1
        elif(idx == 1):
            return self.race2
        else:
            return False


def compareStr(str1, str2):
    """Compare two string (optionally with fuzzy compare)."""
    try:
        fuzzymatch = scctool.settings.config.parser.getboolean(
            "SCT", "fuzzymatch")
        if(fuzzymatch):
            threshold = 0.75
            match = SequenceMatcher(None, str1.upper(), str2.upper()).ratio()
            return match >= threshold
        else:
            return str1 == str2
    except Exception as e:
        module_logger.exception("message")
        return False
