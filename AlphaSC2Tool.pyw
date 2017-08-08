#!python3
#!/usr/bin/env python3
import json
import configparser
import requests
import urllib.request
import os, sys
import webbrowser
import time
import platform

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

system = platform.system()

if(system=="Windows"):
    import ctypes
    from win32gui import GetWindowText, GetForegroundWindow #pip install pypiwin32
    SendInput = ctypes.windll.user32.SendInput
    CONTROL = 0x1D
    SHIFT = 0x2A
    S = 0x1F
    D = 0x20
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
    
    
    def ToggleScore(score1,score2,bestof=5):
        score1=int2DIK(score1)
        score2=int2DIK(score2)
        bestof=int2DIK(bestof)
        lag = 0.01
        time.sleep(lag)
        PressKey(CONTROL)
        PressKey(SHIFT)
        PressKey(S)
        time.sleep(lag)
        ReleaseKey(S)
        PressKey(bestof)
        time.sleep(lag)
        ReleaseKey(bestof)
        ReleaseKey(SHIFT)
        time.sleep(lag)
        PressKey(score2) #Score Player2
        time.sleep(lag)
        ReleaseKey(score2)
        ReleaseKey(CONTROL)
        PressKey(SHIFT)
        PressKey(score1) #Score Player1
        time.sleep(lag)    
        ReleaseKey(score1)
        ReleaseKey(SHIFT)
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
            return DIK_0
        elif(integer==1):
            return DIK_1
        elif(integer==2):
            return DIK_2
        elif(integer==3):
            return DIK_3
        elif(integer==4):
            return DIK_4
        elif(integer==5):
            return DIK_5
        elif(integer==6):
            return DIK_6
        elif(integer==7):
            return DIK_7
        elif(integer==8):
            return DIK_8
        elif(integer==9):
            return DIK_9
        else:
            raise ValueError('The integer has to be in the range 0 to 9')

version='v0.6.0'
configFile = "config.ini"
jsonFile   = "data.json"
OBSdataDir = "OBS_data"
OBSmapDir  = "OBS_mapicons"
OBSmapDirData  = "OBS_mapicons/data"

#Reading the configuration from file
Config = configparser.ConfigParser()
Config.read(configFile)

twitchChannel = Config.get("Twitch", "Channel")
clientID  = Config.get("Twitch", "clientID")
oauth = Config.get("Twitch", "oauth")

twitchTitleTemplate = Config.get("Twitch", "title_template")


win_font_color         = Config.get("MapIcons", "win_font_color")
default_border_color   = Config.get("MapIcons", "default_border_color")
win_border_color       = Config.get("MapIcons", "win_border_color")
lose_border_color      = Config.get("MapIcons", "lose_border_color")
notplayed_border_color = Config.get("MapIcons", "notplayed_border_color")
notplayed_opacity      = Config.get("MapIcons", "notplayed_opacity")

myteam =  Config.get("AlphaSC2","myteam")

races = ("Random","Protoss","Zerg","Terran")




#Creating directories if not exisiting 
if not os.path.exists(OBSdataDir):
    os.makedirs(OBSdataDir)
    
#Creating directories if not exisiting 
if not os.path.exists(OBSmapDir):
    os.makedirs(OBSmapDir)
    
#Creating directories if not exisiting 
if not os.path.exists(OBSmapDirData):
    os.makedirs(OBSmapDirData)
        
        



    
class AlphaMatchData:

    def __init__(self,IDorURL=-1):
        
        self.jsonData = {}
        self.IDorURL=IDorURL
        
    def setIDorURL(self,IDorURL=-1):
        
        self.IDorURL=IDorURL
        
    def getID(self,id=-1):
        
        id = int(id)
        if(id<0): 
            try:
                self.id = str(int(self.IDorURL))
            
            except:
                self.IDorURL = self.IDorURL.replace("http://alpha.tl/match/","")
                self.id = str(int(self.IDorURL))
        else:
            self.id = id
            
        return self.id
        
            
    def readJsonFile(self):
        with open(jsonFile) as json_file:  
            self.jsonData = json.load(json_file)

    def writeJsonFile(self):
        with open(jsonFile, 'w') as outfile:  
            json.dump(self.jsonData, outfile)
            
    def grabJsonData(self, id=-1):
        
        self.getID(id)
        
        url = "http://alpha.tl/api?match="+str(int(self.id))

        data = requests.get(url=url).json()
        
        if(data['code']!=200):
            msg = 'API-Error: '+data['error']
            raise UserWarning(msg)
        else:
            self.jsonData = data
            
        if(self.jsonData['team1']['name']==myteam):
            self.jsonData['myteam']=-1
        elif(self.jsonData['team2']['name']==myteam):
            self.jsonData['myteam']=1
        else:
            self.jsonData['myteam']=0
            
    def downloadMatchBanner(self, id=-1):
        
        self.getID(id)
        fname = OBSdataDir+"/matchbanner.png"
        urllib.request.urlretrieve("http://alpha.tl/announcement/"+self.id+"?vs", fname) 
        
    def downloadLogos(self):
        
        for i in range(1,3):
            fname = OBSdataDir+"/logo"+str(i)+".png"
            urllib.request.urlretrieve(self.jsonData['team'+str(i)]['logo'], fname) 
            
    def createOBStxtFiles(self):
       
        f = open(OBSdataDir+"/lineup.txt", mode = 'w')
        f2 = open(OBSdataDir+"/maps.txt", mode = 'w')
        for idx, map in enumerate(self.jsonData['maps']):
            f3 = open(OBSdataDir+"/map"+str(idx+1)+".txt", mode = 'w')
            f.write(map+"\n")
            f2.write(map+"\n")
            f3.write(map+"\n")
            if(len(self.jsonData['lineup1'])>1):
                try:
                    f.write(self.jsonData['lineup1'][idx]['nickname']+' vs '+self.jsonData['lineup2'][idx]['nickname']+"\n\n")
                    f3.write(self.jsonData['lineup1'][idx]['nickname']+' vs '+self.jsonData['lineup1'][idx]['nickname']+"\n")
                except IndexError:
                    f.write("\n\n")
                    f3.write("\n")
                    pass 
            else:
                f.write("\n\n")
                f3.write("\n")
            f3.close()    
        f.close()
        f2.close()
      
        f = open(OBSdataDir+"/teams_vs_long.txt", mode = 'w')
        f.write(self.jsonData['team1']['name']+' vs '+self.jsonData['team2']['name']+"\n")
        f.close()
        
        f = open(OBSdataDir+"/teams_vs_short.txt", mode = 'w')
        f.write(self.jsonData['team1']['tag']+' vs '+self.jsonData['team2']['tag']+"\n")
        f.close()
      
        f = open(OBSdataDir+"/team1.txt", mode = 'w')
        f.write(self.jsonData['team1']['name'])
        f.close()
      
        f = open(OBSdataDir+"/team2.txt", mode = 'w')
        f.write(self.jsonData['team2']['name'])
        f.close()
      
        f = open(OBSdataDir+"/tournament.txt", mode = 'w')
        f.write(self.jsonData['tournament'])
        f.close()

        try:
            score = [0, 0]
            for winner in self.jsonData['games']:
                if(winner!=0):
                    score[winner-1] += 1
            score_str = str(score[0])+" - "+str(score[1])
        except:
            score_str = "0 - 0"
            
        f = open(OBSdataDir+"/score.txt", mode = 'w')
        f.write(score_str)
        f.close()
        
    def updateMapIcons(self,team=0):
        team = int(team)
        score = [0,0]
        for i in range(1,6):
            filename=OBSmapDirData+"/"+str(i)+".html"
         
            try:
                player1=self.jsonData['lineup1'][i-1]['nickname']
            except:
                player1="TBD"
         
            try:
                player2=self.jsonData['lineup2'][i-1]['nickname']
            except:
                player2="TBD"      
            try:
                race1=self.jsonData['lineup1'][i-1]['race'].title()
            except:
                race1="Random"      
            try:
                race2=self.jsonData['lineup2'][i-1]['race'].title()
            except:
                race2="Random"     
        
            map_name=self.jsonData['maps'][i-1]
            
            if(i==5):
                map_id="Ace Map"
            else:
                map_id="Map "+str(i)
            
            try:
                winner=int(self.jsonData['games'][i-1]*2)-3
            except:
                winner=0
                
            won=winner*team
            opacity = "0.0"
            
            if(score[0]>=3 or score[1] >=3):
                border_color=notplayed_border_color
                opacity = notplayed_opacity 
            elif(won==1):
                border_color=win_border_color 
            elif(won==-1):
                border_color=lose_border_color
            else:
                border_color=default_border_color 
        
            if(winner==-1):
                player1='<font color="'+win_font_color+'">'+player1+'</font>'
                score[0] +=  1
            elif(winner==1):
                player2='<font color="'+win_font_color+'">'+player2+'</font>'
                score[1] +=  1
                
            mappng=map_name.replace(" ","_")+".jpg"
            race1png=race1+".png"
            race2png=race2+".png"

            with open(OBSmapDir+"/data_template.html", "rt") as fin:
                with open(filename, "wt") as fout:
                    for line in fin:
                        line = line.replace('%PLAYER1%', player1).replace('%PLAYER2%', player2)
                        line = line.replace('%RACE1_PNG%', race1png).replace('%RACE2_PNG%', race2png)
                        line = line.replace('%MAP_PNG%', mappng).replace('%MAP_NAME%', map_name)
                        line = line.replace('%MAP_ID%',map_id)
                        line = line.replace('%BORDER_COLOR%',border_color).replace('%OPACITY%',opacity)
                        fout.write(line)

        
def updateTwitchTitle(newTitle):
    
   #Updates the twitch title specified in the config file 
   
   headers = {'Accept':'application/vnd.twitchtv.v3+json', 'Authorization':'OAuth ' + oauth, 'Client-ID':clientID}
   params = {'channel[status]': newTitle}
   r = requests.put('https://api.twitch.tv/kraken/channels/' + twitchChannel,\
                    headers = headers, params = params).raise_for_status()
   msg = "Updated stream title of "+twitchChannel+' to: "' + newTitle.encode("ascii", "ignore").decode()+'"'
   
   return msg
       
       
class mainWindow(QMainWindow):
    def __init__(self,controller):
        super(mainWindow, self).__init__()
        
        self.trigger = True
         
        self.createFormGroupBox()
        self.createFormGroupBox2()
        self.createHorizontalGroupBox()
        self.createSC2APIGroupBox()

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.formGroupBox,2)
        mainLayout.addWidget(self.formGroupBox2,7)
        mainLayout.addWidget(self.SC2APIGroupBox,1)
        mainLayout.addWidget(self.horizontalGroupBox,1)

        self.setWindowTitle("Alpha SC2 Tool "+version)
        
        self.window = QWidget()
        self.window.setLayout(mainLayout)
        self.setCentralWidget(self.window)
        
        self.statusBar()
        self.setGeometry(600, 300, 550, 500)
        self.controller = controller
        self.controller.setView(self)
        self.show()

    def closeEvent(self, event):

        self.controller.cleanUp()

        # close window
        event.accept()
        
    def createFormGroupBox(self):
        self.formGroupBox = QGroupBox("Alpha SC2 Teamleague")
        self.le_url =  QLineEdit()
        self.le_url.setAlignment(Qt.AlignCenter)
        
        self.le_url.setText("http://alpha.tl/match/")
        
        self.pb_refresh = QPushButton("Load Data from URL")
        self.pb_refresh.clicked.connect(self.refresh_click)
        
        self.pb_openBrowser = QPushButton("Open in Browser")
        self.pb_openBrowser.clicked.connect(self.openBrowser_click)
        
        container = QHBoxLayout()
        container.addWidget(QLabel("Match-URL or Match-ID:"),2)
        container.addWidget(self.le_url,4)
        container.addWidget(self.pb_openBrowser,1)
        
        layout = QFormLayout()
        layout.addRow(container)
        layout.addRow(self.pb_refresh)
        
        self.formGroupBox.setLayout(layout)
        
        
    def createFormGroupBox2(self):
       
        self.formGroupBox2 = QGroupBox("Match Data")
        layout2 = QFormLayout()
        
        self.le_league  = QLineEdit()
        self.le_league.setText("League TBD")
        self.le_league.setAlignment(Qt.AlignCenter)
        layout2.addRow(self.le_league)
        
        self.le_team = [QLineEdit() for y in range(2)]
        self.le_player = [[QLineEdit() for x in range(5)] for y in range(2)] 
        self.cb_race   = [[QComboBox() for x in range(5)] for y in range(2)] 
        self.sl_score  = [QSlider(Qt.Horizontal)  for y in range(5)]  
         
        container = QHBoxLayout()
        for team_idx in range(2):
           self.le_team[team_idx].setText("Team TBD")
           self.le_team[team_idx].setAlignment(Qt.AlignCenter)
           
        
        #vslabel = QLabel("vs")
        #vslabel.setAlignment(Qt.AlignCenter)
        
        self.sl_team = QSlider(Qt.Horizontal)
        self.sl_team.setMinimum(-1)
        self.sl_team.setMaximum(1)
        self.sl_team.setValue(0)
        self.sl_team.setTickPosition( QSlider.TicksBothSides)
        self.sl_team.setTickInterval(1)
        self.sl_team.valueChanged.connect(self.sl_changed)
           
        container.addWidget(self.le_team[0],6)    
        container.addWidget(self.sl_team,1)
        container.addWidget(self.le_team[1],6) 
        
        layout2.addRow(container)
           
        for player_idx in range(5):   
           for team_idx in range(2):
              self.le_player[team_idx][player_idx].setText("TBD")
              self.le_player[team_idx][player_idx].setAlignment(Qt.AlignCenter)
              
              for race in races:
                 self.cb_race[team_idx][player_idx].addItem(race)
                 
           self.sl_score[player_idx].setMinimum(-1)
           self.sl_score[player_idx].setMaximum(1)
           self.sl_score[player_idx].setValue(0)
           self.sl_score[player_idx].setTickPosition( QSlider.TicksBothSides)
           self.sl_score[player_idx].setTickInterval(1)
           self.sl_score[player_idx].valueChanged.connect(self.sl_changed)
            
           container = QHBoxLayout()
           container.addWidget(self.cb_race[0][player_idx],2)
           container.addWidget(self.le_player[0][player_idx],4)
           container.addWidget(self.sl_score[player_idx],1)
           container.addWidget(self.le_player[1][player_idx],4)
           container.addWidget(self.cb_race[1][player_idx],2)
           layout2.addRow(container)
           
        
        self.formGroupBox2.setLayout(layout2)
        
    def createHorizontalGroupBox(self):
        self.horizontalGroupBox = QGroupBox("Tasks")
        layout = QHBoxLayout()
        
        self.pb_twitchupdate = QPushButton("Update Twitch Title")
        self.pb_twitchupdate.clicked.connect(self.updatetwitch_click)
        
        if(not(len(clientID)>0 and len(oauth)>0 and len(twitchChannel)>0)):
            self.pb_twitchupdate.setEnabled(False)
        
        self.pb_resetscore = QPushButton("Reset Score")
        self.pb_resetscore.clicked.connect(self.resetscore_click)
        
        self.pb_obsupdate = QPushButton("Update OBS Data")
        self.pb_obsupdate.clicked.connect(self.updateobs_click)
           
        layout.addWidget(self.pb_twitchupdate)
        layout.addWidget(self.pb_resetscore)
        layout.addWidget(self.pb_obsupdate)
        
        self.horizontalGroupBox.setLayout(layout)
        
    def createSC2APIGroupBox(self):
        self.SC2APIGroupBox = QGroupBox("SC2 Client-API")
        layout = QHBoxLayout()
        
        self.cb_autoUpdate = QCheckBox("Score Update")
        self.cb_autoUpdate.setChecked(False)
        self.cb_autoUpdate.stateChanged.connect(self.autoUpdate_change)
        
        self.cb_autoToggleScore = QCheckBox("Set UI-Ingame Score")
        self.cb_autoToggleScore.setChecked(False)
        self.cb_autoToggleScore.stateChanged.connect(self.autoToggleScore_change)
        
        self.cb_autoToggleProduction = QCheckBox("Toggle Production-Tab")
        self.cb_autoToggleProduction.setChecked(False)
        self.cb_autoToggleProduction.stateChanged.connect(self.autoToggleProduction_change)
        
        if(system!="Windows"):
            self.cb_autoToggleScore.setEnabled(False)
            self.cb_autoToggleProduction.setEnabled(False)
        
        layout.addWidget(QLabel("Automatic:"),3)
        layout.addWidget(self.cb_autoUpdate,3)
        layout.addWidget(self.cb_autoToggleScore,3)
        layout.addWidget(self.cb_autoToggleProduction,3)
        
        self.SC2APIGroupBox.setLayout(layout)

    def autoUpdate_change(self):
        if(self.cb_autoUpdate.isChecked()):
           self.controller.runSC2ApiThread("updateScore")
        else:
           self.controller.stopSC2ApiThread("updateScore")
           
    def autoToggleScore_change(self):
        if(self.cb_autoToggleScore.isChecked()):
           self.controller.runSC2ApiThread("toggleScore")
        else:
           self.controller.stopSC2ApiThread("toggleScore")
           
                  
    def autoToggleProduction_change(self):
        if(self.cb_autoToggleProduction.isChecked()):
           self.controller.runSC2ApiThread("toggleProduction")
        else:
           self.controller.stopSC2ApiThread("toggleProduction")
           
        
    def refresh_click(self):
        url = self.le_url.text()
        self.trigger = False
        self.statusBar().showMessage('Reading '+url+'...')
        msg = self.controller.refreshData(url)
        self.statusBar().showMessage(msg)
        self.trigger = True
        
    def openBrowser_click(self):
        url = self.le_url.text()
        self.controller.openURL(url)
        
    def updatetwitch_click(self):
        url = self.le_url.text()
        self.statusBar().showMessage('Updating Twitch Title...')
        msg = self.controller.updateTitle()
        self.statusBar().showMessage(msg)
        
    def updateobs_click(self):
        url = self.le_url.text()
        self.statusBar().showMessage('Updating OBS Data...')
        self.controller.updateOBS()
        self.statusBar().showMessage('')
        
    def resetscore_click(self):
        self.statusBar().showMessage('Resetting Score...')
        self.trigger = False
        for player_idx in range(5): 
            self.sl_score[player_idx].setValue(0)
        self.controller.updateOBS()
        self.statusBar().showMessage('')
        self.trigger = True
        
    def setScore(self,idx,score):
        if(self.sl_score[idx].value()==0):
            self.statusBar().showMessage('Updating Score...')
            self.trigger = False
            self.sl_score[idx].setValue(score)
            self.controller.updateOBS()
            self.statusBar().showMessage('')
            self.trigger = True 
            return True
        else:
            return False
       
    def sl_changed(self):
        if(self.trigger):
            self.controller.updateOBS()

class AlphaController:
    
    def __init__(self):
        self.matchData = AlphaMatchData()
        self.SC2ApiThread = SC2ApiThread(self)

    def setView(self,view):
        self.view = view
        try:
            self.matchData.readJsonFile()
            self.view.trigger = False
            self.updateForms()
            self.view.trigger = True
            self.view.le_url.selectAll()
        except:
            pass

    def updateForms(self):
        self.view.le_url.setText("http://alpha.tl/match/"+str(self.matchData.jsonData['matchid']))
        self.view.le_league.setText(self.matchData.jsonData['tournament'])
        try:
            self.view.sl_team.setValue(int(self.matchData.jsonData['myteam']))
        except:
            self.view.sl_team.setValue(0)
        for i in range(2):
            self.view.le_team[i].setText(self.matchData.jsonData['team'+str(i+1)]['name'])
        for i in range(5):
            for j in range(2):
                try:
                    self.view.le_player[j][i].setText(self.matchData.jsonData['lineup'+str(j+1)][i]['nickname'])
                except:
                    self.view.le_player[j][i].setText("TBD")
                try:
                    index = self.view.cb_race[j][i].findText(self.matchData.jsonData['lineup'+str(j+1)][i]['race'].title(),\
                                                             Qt.MatchFixedString)
                    if index >= 0:
                        self.view.cb_race[j][i].setCurrentIndex(index)
                except:
                    self.view.cb_race[j][i].setCurrentIndex(0)
            
            try:
                value = int(self.matchData.jsonData['games'][i])
                if(value == 0):
                    value = 0
                else:
                    value = self.matchData.jsonData['games'][i]*2-3
                    
                self.view.sl_score[i].setValue(value)
            except:
                pass
                
    def updateData(self):     
        self.matchData.jsonData['myteam'] = self.view.sl_team.value()
        self.matchData.jsonData['tournament'] = self.view.le_league.text()
        
        if(not('team1' in self.matchData.jsonData)):
            self.matchData.jsonData['team1'] = {}
        if(not('team2' in self.matchData.jsonData)):
            self.matchData.jsonData['team2'] = {}
        if(not('lineup1' in self.matchData.jsonData)):
            self.matchData.jsonData['lineup1'] = []
        if(not('lineup2' in self.matchData.jsonData)):
            self.matchData.jsonData['lineup2'] = []  
            
        for i in range(2):
            self.matchData.jsonData['team'+str(i+1)]['name'] = self.view.le_team[i].text()
            
        for i in range(5):
            for j in range(2):
                try:
                    self.matchData.jsonData['lineup'+str(j+1)][i]['nickname'] = self.view.le_player[j][i].text()
                    self.matchData.jsonData['lineup'+str(j+1)][i]['race'] = self.view.cb_race[j][i].currentText()
                except:
                    self.matchData.jsonData['lineup'+str(j+1)].insert(i,\
                        {'nickname': self.view.le_player[j][i].text(),'race': self.view.cb_race[j][i].currentText()})
            
            if(self.view.sl_score[i].value()==0):
                score = 0
            else:
                score = int((self.view.sl_score[i].value()+3)/2)
            
            try:
                self.matchData.jsonData['games'][i] = score
            except:
                if(not('games' in self.matchData.jsonData)):
                        self.matchData.jsonData['games'] = []
                self.matchData.jsonData['games'].insert(i,score)
                    
    def refreshData(self,IDorURL):      
        self.matchData.setIDorURL(IDorURL)
        msg = ''
        try:
            self.matchData.grabJsonData()
            self.matchData.writeJsonFile()
            self.matchData.downloadMatchBanner()
            self.matchData.downloadLogos()
            self.updateForms()  
        except Exception as e:
            msg = str(e)
            pass
          
        return msg
        
    def updateOBS(self):
        self.updateData()
        self.matchData.createOBStxtFiles()
        self.matchData.updateMapIcons(self.view.sl_team.value())
        self.matchData.writeJsonFile()
        
    def updateTitle(self):
        msg = ''
        self.updateData()
        try:
            title = twitchTitleTemplate
            title = title.replace("<TOUR>",self.matchData.jsonData['tournament'])
            title = title.replace("<TEAM1>",self.matchData.jsonData['team1']['name'])
            title = title.replace("<TEAM2>",self.matchData.jsonData['team2']['name'])
            msg = updateTwitchTitle(title)
        except Exception as e:
            msg = str(e)
            pass
        self.matchData.writeJsonFile()
        return msg
        
    def openURL(self,IDorURL):
        if(len(IDorURL)>0):
            try:
                self.matchData.setIDorURL(IDorURL)
                url="http://alpha.tl/match/"+str(self.matchData.getID())
            except:
                url="http://alpha.tl/match/"
        else:
            url="http://alpha.tl/match/"
        webbrowser.open(url)
    
    def runSC2ApiThread(self,task):
        if(not self.SC2ApiThread.isRunning()):
            self.SC2ApiThread.startTask(task)
        else:
            self.SC2ApiThread.cancelTerminationRequest(task)
          
       
    def stopSC2ApiThread(self,task):   
        self.SC2ApiThread.requestTermination(task)
        
    def cleanUp(self):
        self.SC2ApiThread.requestTermination("ALL")
        
    def requestScoreUpdate(self,newSC2MatchData):
        
        print("Trying to update the score")
        
        self.updateData()
        newscore = 0
        for i in range(5):
            found, newscore = newSC2MatchData.compare_returnScore(self.matchData.jsonData['lineup1'][i]['nickname'],\
                                                                  self.matchData.jsonData['lineup2'][i]['nickname'])
            if(found and newscore != 0):
                if(self.view.setScore(i,newscore)):
                    break
                else:
                    continue
                    
    def requestToggleScore(self,newSC2MatchData):
        
        self.updateData()
        newscore = 0
        for i in range(5):
            found, order = newSC2MatchData.compare_returnOrder(self.matchData.jsonData['lineup1'][i]['nickname'],\
                                                               self.matchData.jsonData['lineup2'][i]['nickname'])
            if(found):
                try:
                    score = [0, 0]
                    for winner in self.matchData.jsonData['games']:
                        if(winner!=0):
                            score[winner-1] += 1
                    
                except:
                    score = [0, 0]
                
                if(order):
                    ToggleScore(score[0],score[1])  
                else:
                    ToggleScore(score[1],score[0])
                
                break    
               
                
        
class SC2MatchData:
    
    def __init__(self, GAMEresponse = False, UIresponse = False):
        try:
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
        except:
            self.player1 = ""
            self.player2 = ""
            self.race1   = ""
            self.race2   = ""
            self.result  = 0
            self.time  = 0
            self.ingame = False
            
    def compare_returnScore(self, player1, player2):

        if(self.player1.upper()==player1.upper() and self.player2.upper()==player2.upper()):
            return True, self.result
        elif(self.player1.upper()==player2.upper() and self.player2.upper()==player1.upper()):
            return True, -self.result
        else:
            return False, 0
            
    def compare_returnOrder(self, player1, player2):

        if(self.player1.upper()==player1.upper() and self.player2.upper()==player2.upper()):
            return True, True
        elif(self.player1.upper()==player2.upper() and self.player2.upper()==player1.upper()):
            return True, False
        else:
            return False, False
            
    def getRace(self,str):
        for idx, race in enumerate(races):
            if(str[0].upper()==race[0].upper()):
                return races[idx]
        return ""
            
    def isDecidedGame(self):
        return (self.result!=0 and self.time > 60)  
        
    def isLive(self):
        return (self.ingame and self.result==99 and self.time < 30)      
        
    def __str__(self):
        return str(self.__dict__)

    def __eq__(self, other): 
        return (self.player1 == other.player1 and self.player2 == other.player2\
                and self.race1 == other.race1 and self.race2 == other.race2\
                and self.result == other.result and self.ingame == other.ingame)


        
class SC2ApiThread(QThread):
   
    def __init__(self, controller, parent = None):
        QThread.__init__(self, parent)
        self.exiting = False
        self.activeTask = {}
        self.activeTask['updateScore'] = False
        self.activeTask['toggleScore'] = False
        self.activeTask['toggleProduction'] = False
        self.currentData = SC2MatchData()
        self.controller = controller
        self.currentÍngameStatus = False
        
    def startTask(self,task):
        self.activeTask[task] = True
        self.start() 
      
    def requestTermination(self,task):
        if(task == 'ALL'):
            for task in self.activeTask:
                self.activeTask[task] = False
        else:
            self.activeTask[task] = False
            print('Requesting termination fo task "'+task+'"')
            
        if(not any(self.activeTask.values())):
            self.exiting = True
            print('Requesting termination of thread')  
   
    def cancelTerminationRequest(self,task):
        self.activeTask[task] = True
        self.exiting = False
        print('Termination request fo task "'+task+'" cancelled')  
      
    def run(self):
        print("Start")
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
                time.sleep(5)
            except ValueError:
                print("StarCraft 2 starting.")
                time.sleep(5)
            
            time.sleep(5)
      
        print('terminated')
        
    def parseMatchData(self,newData):
        if(self.exiting==False and (newData!=self.currentData or newData.time < self.currentData.time)):
            print("New data:")
            print(str(newData))
            if(self.activeTask['updateScore'] and newData.isDecidedGame()):
                self.controller.requestScoreUpdate(newData)
                   
            if(newData.isLive() and (self.activeTask['toggleScore'] or self.activeTask['toggleProduction'])):
                self.tryToggle(newData)
                
            self.currentData = newData    
    
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
            print("Toggle not working on this OS")

def isSC2onForeground():
    return GetWindowText(GetForegroundWindow())=="StarCraft II"
         
def main():
    
    app = QApplication(sys.argv)
    QApplication.setStyle(QStyleFactory.create('Fusion'))
    app.setWindowIcon(QIcon('alpha.ico'))
    controller = AlphaController()
    view = mainWindow(controller)
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()