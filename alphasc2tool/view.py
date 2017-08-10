#!/usr/bin/env python
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtQml import *

import alphasc2tool.settings
import platform

class mainWindow(QMainWindow):
    def __init__(self,controller):
        super(mainWindow, self).__init__()
        
        self.trigger = True
         
        self.createFormGroupBox()
        self.createFromMatchDataBox()
        self.createHorizontalGroupBox()
        self.createSC2APIGroupBox()

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.formGroupBox,2)
        mainLayout.addWidget(self.fromMatchDataBox,7)
        mainLayout.addWidget(self.SC2APIGroupBox,1)
        mainLayout.addWidget(self.horizontalGroupBox,1)

        self.setWindowTitle("Alpha SC2 Tool " + alphasc2tool.settings.version)
        
        self.window = QWidget()
        self.window.setLayout(mainLayout)
        self.setCentralWidget(self.window)
        
        self.statusBar()
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
        
        
    def createFromMatchDataBox(self):
       
        self.fromMatchDataBox = QGroupBox("Match Data")
        layout2 = QFormLayout()
        
        self.le_league  = QLineEdit()
        self.le_league.setText("League TBD")
        self.le_league.setAlignment(Qt.AlignCenter)
        
        container = QHBoxLayout()
        label = QLabel("League:")
        label.setAlignment(Qt.AlignCenter)
        container.addWidget(label,3)
        container.addWidget(self.le_league,13)
        layout2.addRow(container)
        
        self.le_team = [QLineEdit() for y in range(2)]
        self.le_player = [[QLineEdit() for x in range(5)] for y in range(2)] 
        self.cb_race   = [[QComboBox() for x in range(5)] for y in range(2)] 
        self.sl_score  = [QSlider(Qt.Horizontal)  for y in range(5)]  
        self.le_map    = [QLineEdit()  for y in range(5)]  
         
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
          
        label = QLabel("Maps \ Teams:")
        label.setAlignment(Qt.AlignCenter)
        container.addWidget(label,3)
        container.addWidget(self.le_team[0],6)    
        container.addWidget(self.sl_team,1)
        container.addWidget(self.le_team[1],6) 
        
        layout2.addRow(container)
           
        for player_idx in range(5):   
           for team_idx in range(2):
              self.le_player[team_idx][player_idx].setText("TBD")
              self.le_player[team_idx][player_idx].setAlignment(Qt.AlignCenter)
              
              for race in alphasc2tool.settings.races:
                 self.cb_race[team_idx][player_idx].addItem(race)
                 
           self.sl_score[player_idx].setMinimum(-1)
           self.sl_score[player_idx].setMaximum(1)
           self.sl_score[player_idx].setValue(0)
           self.sl_score[player_idx].setTickPosition( QSlider.TicksBothSides)
           self.sl_score[player_idx].setTickInterval(1)
           self.sl_score[player_idx].valueChanged.connect(self.sl_changed)
           
           self.le_map[player_idx].setText("TBD")
           self.le_map[player_idx].setAlignment(Qt.AlignCenter)
           #self.le_map[player_idx].setReadOnly(True)
            
           container = QHBoxLayout()
           container.addWidget(self.le_map[player_idx],3)
           container.addWidget(self.cb_race[0][player_idx],2)
           container.addWidget(self.le_player[0][player_idx],4)
           container.addWidget(self.sl_score[player_idx],1)
           container.addWidget(self.le_player[1][player_idx],4)
           container.addWidget(self.cb_race[1][player_idx],2)
           layout2.addRow(container)
           
        
        self.fromMatchDataBox.setLayout(layout2)
        
    def createHorizontalGroupBox(self):
        self.horizontalGroupBox = QGroupBox("Tasks")
        layout = QHBoxLayout()
        
        self.pb_settings = QPushButton("Settings")
        self.pb_settings.clicked.connect(self.settings_click)
        
        self.pb_twitchupdate = QPushButton("Update Twitch Title")
        self.pb_twitchupdate.clicked.connect(self.updatetwitch_click)
        
        if(not alphasc2tool.settings.twitch_valid):
            self.pb_twitchupdate.setEnabled(False)
            self.pb_twitchupdate.setAttribute(Qt.WA_AlwaysShowToolTips)
            self.pb_twitchupdate.setToolTip('Specify your twitch account to use this feature') 
        
        self.pb_resetscore = QPushButton("Reset Score")
        self.pb_resetscore.clicked.connect(self.resetscore_click)
        
        self.pb_obsupdate = QPushButton("Update OBS Data")
        self.pb_obsupdate.clicked.connect(self.updateobs_click)
           
        #layout.addWidget(self.pb_settings)
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
        
        if(platform.system()!="Windows"):
            self.cb_autoToggleScore.setEnabled(False)
            self.cb_autoToggleScore.setAttribute(Qt.WA_AlwaysShowToolTips)
            self.cb_autoToggleScore.setToolTip('Only Windows') 
            self.cb_autoToggleProduction.setEnabled(False)
            self.cb_autoToggleProduction.setAttribute(Qt.WA_AlwaysShowToolTips)
            self.cb_autoToggleProduction.setToolTip('Only Windows') 
        
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
        
    def settings_click(self):
        self.controller.NightBotDialog()

    
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