"""Interact with SC2-Client via thread."""
import logging

# create logger
module_logger = logging.getLogger('scctool.tasks.apithread')

try:
    import PyQt5

    import requests
    import time
    from difflib import SequenceMatcher
    import re

    import scctool.settings


except Exception as e:
    module_logger.exception("message")
    raise

if(scctool.settings.windows):
    from PIL import ImageGrab  # pip install Pillow
    import pytesseract  # pip install pytesseract
    import ctypes
    from win32gui import GetWindowText, GetForegroundWindow

    try:
        SendInput = ctypes.windll.user32.SendInput
        CONTROL = 0x1D
        SHIFT = 0x2A
        S = 0x1F
        D = 0x20
        X = 0x2D
        DIK_1 = 0x02
        DIK_2 = 0x03
        DIK_3 = 0x04
        DIK_4 = 0x05
        DIK_5 = 0x06
        DIK_6 = 0x07
        DIK_7 = 0x08
        DIK_8 = 0x09
        DIK_9 = 0x0A
        DIK_0 = 0x0B

        # C struct redefinitions
        PUL = ctypes.POINTER(ctypes.c_ulong)

        class KeyBdInput(ctypes.Structure):
            """Keyboard Input."""

            _fields_ = [("wVk", ctypes.c_ushort),
                        ("wScan", ctypes.c_ushort),
                        ("dwFlags", ctypes.c_ulong),
                        ("time", ctypes.c_ulong),
                        ("dwExtraInfo", PUL)]

        class HardwareInput(ctypes.Structure):
            """Hardware Input."""

            _fields_ = [("uMsg", ctypes.c_ulong),
                        ("wParamL", ctypes.c_short),
                        ("wParamH", ctypes.c_ushort)]

        class MouseInput(ctypes.Structure):
            """Mouse Input."""

            _fields_ = [("dx", ctypes.c_long),
                        ("dy", ctypes.c_long),
                        ("mouseData", ctypes.c_ulong),
                        ("dwFlags", ctypes.c_ulong),
                        ("time", ctypes.c_ulong),
                        ("dwExtraInfo", PUL)]

        class Input_I(ctypes.Union):
            """General Input."""

            _fields_ = [("ki", KeyBdInput),
                        ("mi", MouseInput),
                        ("hi", HardwareInput)]

        class Input(ctypes.Structure):
            """General Input."""

            _fields_ = [("type", ctypes.c_ulong),
                        ("ii", Input_I)]

        # Actuals Functions

        def PressKey(hexKeyCode):
            """Simulate a key press down."""
            extra = ctypes.c_ulong(0)
            ii_ = Input_I()
            ii_.ki = KeyBdInput(0, hexKeyCode, 0x0008,
                                0, ctypes.pointer(extra))
            x = Input(ctypes.c_ulong(1), ii_)
            ctypes.windll.user32.SendInput(
                1, ctypes.pointer(x), ctypes.sizeof(x))

        def ReleaseKey(hexKeyCode):
            """Simulate a key release."""
            extra = ctypes.c_ulong(0)
            ii_ = Input_I()
            ii_.ki = KeyBdInput(0, hexKeyCode, 0x0008 |
                                0x0002, 0, ctypes.pointer(extra))
            x = Input(ctypes.c_ulong(1), ii_)
            ctypes.windll.user32.SendInput(
                1, ctypes.pointer(x), ctypes.sizeof(x))

        def int2DIK(integer):
            """Convert Integer to KeyBdInput."""
            if(integer == 0):
                return DIK_0, True
            elif(integer == 1):
                return DIK_1, False
            elif(integer == 2):
                return DIK_2, False
            elif(integer == 3):
                return DIK_3, False
            elif(integer == 4):
                return DIK_4, False
            elif(integer == 5):
                return DIK_5, False
            elif(integer == 6):
                return DIK_6, False
            elif(integer == 7):
                return DIK_7, False
            elif(integer == 8):
                return DIK_8, False
            elif(integer == 9):
                return DIK_9, False
            else:
                raise ValueError('The integer has to be in the range 0 to 9')

    except Exception as e:
        module_logger.exception("message")


def ToggleScore(score1_in, score2_in, bestof=5):
    """Set and toggle SC2-ingame score."""
    if(not scctool.settings.windows):
        raise UserWarning("Only Windows!")

    score1, skip1 = int2DIK(score1_in)
    score2, skip2 = int2DIK(score2_in)

    if(bestof == 3):
        bestof, skipBestof = int2DIK(bestof)
        skipBestof = True
    else:
        bestof, skipBestof = int2DIK(bestof)

    lag = 0.01

    if scctool.settings.config.parser.getboolean("SCT", "StrgShiftS"):
        PressKey(CONTROL)
        PressKey(SHIFT)
        PressKey(S)
        time.sleep(lag)
        ReleaseKey(S)
        ReleaseKey(SHIFT)
        ReleaseKey(CONTROL)
        time.sleep(lag)

    if(not skipBestof):
        PressKey(CONTROL)
        PressKey(SHIFT)
        PressKey(bestof)
        time.sleep(lag)
        ReleaseKey(bestof)
        ReleaseKey(SHIFT)
        ReleaseKey(CONTROL)
        time.sleep(lag)

    if(not skip2):
        PressKey(CONTROL)
        PressKey(score2)  # Score player2
        time.sleep(lag)
        ReleaseKey(score2)
        ReleaseKey(CONTROL)
        time.sleep(lag)

    if(not skip1):
        PressKey(SHIFT)
        PressKey(score1)  # Score player1
        time.sleep(lag)
        ReleaseKey(score1)
        ReleaseKey(SHIFT)
        time.sleep(lag)


def ToggleProduction():
    """Toggle SC2-ingame production tab."""
    if(not scctool.settings.windows):
        raise UserWarning("Only Windows!")
    lag = 0.01
    time.sleep(lag)
    PressKey(CONTROL)
    PressKey(D)
    time.sleep(lag)
    ReleaseKey(CONTROL)
    ReleaseKey(D)


class SC2ApiThread(PyQt5.QtCore.QThread):
    """Thread to interact with SC2-Client."""

    def __init__(self, controller, parent=None):
        """Init thread."""
        try:
            PyQt5.QtCore.QThread.__init__(self, parent)
            self.exiting = False
            self.activeTask = {}
            self.activeTask['updateScore'] = False
            self.activeTask['toggleScore'] = False
            self.activeTask['toggleProduction'] = False
            self.activeTask['playerIntros'] = False
            self.currentData = SC2MatchData()
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
            module_logger.info("Start  Thread")
            self.exiting = False

            GAMEurl = "http://localhost:6119/game"
            UIurl = "http://localhost:6119/ui"

            while self.exiting is False:
                # See: https://us.battle.net/forums/en/sc2/topic/20748195420
                try:
                    GAMEresponse = requests.get(GAMEurl, timeout=100).json()
                    UIresponse = requests.get(UIurl, timeout=100).json()

                    # activate script if 2 players are playing right now
                    if(len(GAMEresponse["players"]) == 2):
                        self.parseMatchData(
                            SC2MatchData(GAMEresponse, UIresponse))

                except requests.exceptions.ConnectionError:
                    # print("StarCraft 2 not running!")
                    time.sleep(10)
                except ValueError:
                    # print("StarCraft 2 starting.")
                    time.sleep(10)

                time.sleep(2)

            # print('terminated')
        except Exception as e:
            module_logger.exception("message")

    def parseMatchData(self, newData):
        """Parse SC2-Client-API data and run tasks accordingly."""
        #print("Prasing")
        #print(newData)
        #print(self.currentData)
        #print(newData.time)
        #print(self.currentData.time)
        try:
            if(self.exiting is False and
                (newData != self.currentData or
                 newData.time < self.currentData.time)):
                     
                # Skip initial data
                #if(self.currentData == SC2MatchData()):
                #    print("Skipping initial")
                #    self.currentData = newData
                #    return

                if(self.activeTask['playerIntros']):
                    print("Providing player intros...")
                    self.controller.updatePlayerIntros(newData)

                if(self.activeTask['updateScore'] and newData.isDecidedGame() and self.currentData != SC2MatchData()):
                    print("Updating Score")
                    self.controller.requestScoreUpdate(newData)

                if(newData.isLive() and (self.activeTask['toggleScore']
                                         or self.activeTask['toggleProduction'])):
                    print("Toggling")
                    self.tryToggle(newData)

                self.currentData = newData
        except Exception as e:
            module_logger.exception("message")

    def tryToggle(self, data):
        """Wait until SC2 is in foreground and toggle production tab and score."""
        try:
            while self.exiting is False\
                and (self.activeTask['toggleScore']
                     or self.activeTask['toggleProduction']):
                if(isSC2onForeground()):
                    if(self.activeTask['toggleScore']):
                        swapPlayers = self.swapPlayers(data)
                        self.controller.requestToggleScore(data, swapPlayers)
                    if(self.activeTask['toggleProduction']):
                        ToggleProduction()
                    break
                else:
                    # print("SC2 not on foreground... waiting.")
                    time.sleep(2)
        except:
            module_logger.info("Toggle not working on this OS:")

    def swapPlayers(self, data):
        """Detect if players are swapped relative to SC2-Client-API data via ocr."""
        try:
            if(not scctool.settings.config.parser.getboolean("SCT", "use_ocr")):
                return False

            pytesseract.pytesseract.tesseract_cmd = scctool.settings.config.getTesserAct()

            players = data.getPlayerList()
            full_img = ImageGrab.grab()
            width, height = full_img.size
            positions = [None, None]
            ratios = [0.0, 0.0]
            img = full_img.crop((int(width * 0.1), int(height * 0.8),
                                 int(width * 0.5), height))
            text = pytesseract.image_to_string(img)
            items = re.split('\s+', text)

            threshold = 0.5
            for item_idx, item in enumerate(items):
                for player_idx, player in enumerate(players):
                    ratio = SequenceMatcher(
                        None, item.lower(), player.lower()).ratio()
                    if(ratio >= max(threshold, ratios[player_idx])):
                        positions[player_idx] = item_idx
                        ratios[player_idx] = ratio
                        module_logger.info("Player {} at postion {}".format(
                            player_idx, item_idx))

            if None in positions: # Retry with full image.
                positions = [None, None]
                ratios = [0.0, 0.0]
                text = pytesseract.image_to_string(full_img)
                items = re.split('\s+', text)
    
                threshold = 0.5
                for item_idx, item in enumerate(items):
                    for player_idx, player in enumerate(players):
                        ratio = SequenceMatcher(
                            None, item.lower(), player.lower()).ratio()
                        if(ratio >= max(threshold, ratios[player_idx])):
                            positions[player_idx] = item_idx
                            ratios[player_idx] = ratio
                            module_logger.info("Player {} at postion {}".format(
                                player_idx, item_idx))
                                
            if None in positions:
                return False
            elif(positions[0] > positions[1]):
                return True
            else:
                return False
        except Exception as e:
            module_logger.exception("message")
            return False


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

    def compare_returnScore(self, player1, player2):
        """Fuzzy compare playernames and return their score."""
        if(compareStr(self.player1, player1)
           and compareStr(self.player2, player2)):
            return True, self.result
        elif(compareStr(self.player1, player2)
             and compareStr(self.player2, player1)):
            return True, -self.result
        else:
            return False, 0

    def compare_returnOrder(self, player1, player2):
        """Fuzzy compare playernames and return the correct order."""
        if(compareStr(self.player1, player1)
           and compareStr(self.player2, player2)):
            return True, True
        elif(compareStr(self.player1, player2)
             and compareStr(self.player2, player1)):
            return True, False
        else:
            return False, False

    def playerInList(self, player_idx, players):
        """Fuzzy check if player is in list of players."""
        for player in players:
            if(player_idx == 0 and compareStr(self.player1, player)):
                return True
            elif(player_idx == 1 and compareStr(self.player2, player)):
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
        return (self.player1 == other.player1
                and self.player2 == other.player2
                and self.race1 == other.race1
                and self.race2 == other.race2
                and self.result == other.result)

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

    def getPlayerRace(self, idx):
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
