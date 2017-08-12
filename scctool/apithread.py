#!/usr/bin/env python
import logging

# create logger
module_logger = logging.getLogger('scctool.apithread')

try:
    from PyQt5.QtCore import *
    import platform
    import requests
    import time
    import json
    from difflib import SequenceMatcher
    import scctool.settings

except Exception as e:
    module_logger.exception("message") 
    raise  
    
if(platform.system()=="Windows"):
    try:
        import ctypes
        from win32gui import GetWindowText, GetForegroundWindow #pip install pypiwin32
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
            _fields_ = [("wVk", ctypes.c_ushort),
                        ("wScan", ctypes.c_ushort),
                        ("dwFlags", ctypes.c_ulong),
                        ("time", ctypes.c_ulong),
                        ("dwExtraInfo", PUL)]
        
        class HardwareInput(ctypes.Structure):
            _fields_ = [("uMsg", ctypes.c_ulong),
                        ("wParamL", ctypes.c_short),
                        ("wParamH", ctypes.c_ushort)]
        
        class MouseInput(ctypes.Structure):
            _fields_ = [("dx", ctypes.c_long),
                        ("dy", ctypes.c_long),
                        ("mouseData", ctypes.c_ulong),
                        ("dwFlags", ctypes.c_ulong),
                        ("time",ctypes.c_ulong),
                        ("dwExtraInfo", PUL)]
        
        class Input_I(ctypes.Union):
            _fields_ = [("ki", KeyBdInput),
                        ("mi", MouseInput),
                        ("hi", HardwareInput)]
        
        class Input(ctypes.Structure):
            _fields_ = [("type", ctypes.c_ulong),
                        ("ii", Input_I)]
        
        # Actuals Functions
        
        def PressKey(hexKeyCode):
            extra = ctypes.c_ulong(0)
            ii_ = Input_I()
            ii_.ki = KeyBdInput( 0, hexKeyCode, 0x0008, 0, ctypes.pointer(extra) )
            x = Input( ctypes.c_ulong(1), ii_ )
            ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))
        
        def ReleaseKey(hexKeyCode):
            extra = ctypes.c_ulong(0)
            ii_ = Input_I()
            ii_.ki = KeyBdInput( 0, hexKeyCode, 0x0008 | 0x0002, 0, ctypes.pointer(extra) )
            x = Input( ctypes.c_ulong(1), ii_ )
            ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))
        
        
        def ToggleScore(score1_in,score2_in,bestof=5):
    
            score1,skip1 = int2DIK(score1_in)
            score2,skip2 = int2DIK(score2_in)  
            
            if(bestof == 3):
                bestof,skipBestof = int2DIK(bestof)
                skipBestof = True
            else:
                bestof,skipBestof = int2DIK(bestof)
                
            lag = 0.01
            
            
            PressKey(CONTROL)
            PressKey(SHIFT)
            PressKey(S)
            time.sleep(lag)
            ReleaseKey(S)
            ReleaseKey(SHIFT)
            ReleaseKey(CONTROL)
            time.sleep(lag)
                
            if(not skipBestof):
                print("Best of")
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
                PressKey(score2) #Score player2
                time.sleep(lag)
                ReleaseKey(score2)
                ReleaseKey(CONTROL)
                time.sleep(lag)
                
            if(not skip1):     
                PressKey(SHIFT)
                PressKey(score1) #Score player1
                time.sleep(lag)    
                ReleaseKey(score1)
                ReleaseKey(SHIFT)
                time.sleep(lag)
                
            print("Toggled Score")
        
        def ToggleProduction():
            lag = 0.01
            time.sleep(lag)
            PressKey(CONTROL)
            PressKey(D)
            time.sleep(lag)
            ReleaseKey(CONTROL)
            ReleaseKey(D)   
            
        def int2DIK(integer):
            if(integer==0):
                return DIK_0, True
            elif(integer==1):
                return DIK_1, False
            elif(integer==2):
                return DIK_2, False
            elif(integer==3):
                return DIK_3, False
            elif(integer==4):
                return DIK_4, False
            elif(integer==5):
                return DIK_5, False
            elif(integer==6):
                return DIK_6, False
            elif(integer==7):
                return DIK_7, False
            elif(integer==8):
                return DIK_8, False
            elif(integer==9):
                return DIK_9, False
            else:
                raise ValueError('The integer has to be in the range 0 to 9')
                
    except Exception as e:
        module_logger.exception("message") 

class SC2ApiThread(QThread):
   
    def __init__(self, controller, parent = None):
        try:
            QThread.__init__(self, parent)
            self.exiting = False
            self.activeTask = {}
            self.activeTask['updateScore'] = False
            self.activeTask['toggleScore'] = False
            self.activeTask['toggleProduction'] = False
            self.currentData = SC2MatchData()
            self.controller = controller
            self.currentÍngameStatus = False
        except Exception as e:
            module_logger.exception("message") 
        
    def startTask(self,task):
        try:
            self.activeTask[task] = True
            self.start() 
        except Exception as e:
            module_logger.exception("message") 
      
    def requestTermination(self,task):
        try:
            if(task == 'ALL'):
                for task in self.activeTask:
                    self.activeTask[task] = False
            else:
                self.activeTask[task] = False
                module_logger.info('Requesting termination fo task "'+task+'"')
                
            if(not any(self.activeTask.values())):
                self.exiting = True
                module_logger.info('Requesting termination of thread')  
        except Exception as e:
            module_logger.exception("message") 
   
    def cancelTerminationRequest(self,task):
        self.activeTask[task] = True
        self.exiting = False
        module_logger.info('Termination request fo task "'+task+'" cancelled')  
      
    def run(self):
        try:
            module_logger.info("Start  Thread")
            self.exiting=False
        
            GAMEurl = "http://localhost:6119/game"
            UIurl = "http://localhost:6119/ui"
        
            while self.exiting==False:
                #See: https://us.battle.net/forums/en/sc2/topic/20748195420
                try:
                    GAMEresponse = requests.get(GAMEurl, timeout=100).json()
                    UIresponse = requests.get(UIurl, timeout=100).json()
    
                    if(len(GAMEresponse["players"]) == 2): #activate script if 2 players are playing right now 
                        self.parseMatchData(SC2MatchData(GAMEresponse,UIresponse))
    
                except requests.exceptions.ConnectionError: #handle exception when starcraft is detected as not running
                    print("StarCraft 2 not running!")
                    time.sleep(10)
                except ValueError:
                    print("StarCraft 2 starting.")
                    time.sleep(10)
    
                time.sleep(2)
        
            print('terminated')
        except Exception as e:
            module_logger.exception("message")
            
        
    def parseMatchData(self,newData):
        try:
            if(self.exiting==False and (newData!=self.currentData or newData.time < self.currentData.time)):
                print("New data:")
                print(str(newData))
                if(self.activeTask['updateScore'] and newData.isDecidedGame()):
                    self.controller.requestScoreUpdate(newData)
                    
                if(newData.isLive() and (self.activeTask['toggleScore'] or self.activeTask['toggleProduction'])):
                    self.tryToggle(newData)
                    
                self.currentData = newData    
        except Exception as e:
            module_logger.exception("message")
    
    def tryToggle(self,data):
        try:
            while self.exiting==False and (self.activeTask['toggleScore'] or self.activeTask['toggleProduction']):
                if(isSC2onForeground()):
                    if(self.activeTask['toggleScore']):
                        self.controller.requestToggleScore(data)
                    if(self.activeTask['toggleProduction']):
                        ToggleProduction()
                    break
                else:
                    print("SC2 not on foreground... waiting.")
                    time.sleep(4)
        except:
            module_logger.info("Toggle not working on this OS")

def isSC2onForeground():
    try:
        return GetWindowText(GetForegroundWindow()).lower()=="StarCraft II".lower()
    except Exception as e:
        module_logger.exception("message")
        return False
            
    
class SC2MatchData:
    
    def __init__(self, GAMEresponse = False, UIresponse = False):
        if(GAMEresponse):
            self.player1 = GAMEresponse["players"][0]["name"]
            self.player2 = GAMEresponse["players"][1]["name"]
            self.race1   = self.getRace(GAMEresponse["players"][0]["race"])
            self.race2   = self.getRace(GAMEresponse["players"][1]["race"])
            self.time  = GAMEresponse["displayTime"]
            self.ingame = UIresponse["activeScreens"] == []
            if(GAMEresponse["players"][0]["result"]=="Victory"):
                self.result = -1
            elif(GAMEresponse["players"][0]["result"]=="Defeat"):
                self.result = 1
            elif(GAMEresponse["players"][0]["result"]=="Undecided"):
                self.result = 99
            else:
                self.result = 0
        else:
            self.player1 = ""
            self.player2 = ""
            self.race1   = ""
            self.race2   = ""
            self.result  = 0
            self.time  = 0
            self.ingame = False

    def compare_returnScore(self, player1, player2):

        if(compareStr(self.player1,player1) and compareStr(self.player2,player2)):
            return True, self.result
        elif(compareStr(self.player1,player2) and compareStr(self.player2,player1)):
            return True, -self.result
        else:
            return False, 0    

    def compare_returnOrder(self, player1, player2):

        if(compareStr(self.player1,player1) and compareStr(self.player2,player2)):
            return True, True
        elif(compareStr(self.player1,player2) and compareStr(self.player2,player1)):
            return True, False
        else:
            return False, False

            
            
    def getRace(self,str):
        try: 
            for idx, race in enumerate(scctool.settings.races):
                if(str[0].upper()==race[0].upper()):
                    return scctool.settings.races[idx]
        except Exception as e:
            module_logger.exception("message")
            
        module_logger.info("Race "+str+" not found")    
        return ""
            
    def isDecidedGame(self):
        return ((self.result==1 or self.result==-1) and self.time > 60)  
        
    def isLive(self):
        return (self.ingame and self.result==99 and self.time < 30)      
        
    def __str__(self):
        return str(self.__dict__)

    def __eq__(self, other): 
        return (self.player1 == other.player1 and self.player2 == other.player2\
                and self.race1 == other.race1 and self.race2 == other.race2\
                and self.result == other.result and self.ingame == other.ingame)
                
                
def compareStr(str1,str2):
    try:
        fuzzymatch = scctool.settings.fuzzymatch
        if(fuzzymatch):
            threshold = 0.75
            return SequenceMatcher(None, str1.upper(), str2.upper()).ratio() >= threshold
        else:
            return str1 == str2 
    except Exception as e:
        module_logger.exception("message")
        return False
    