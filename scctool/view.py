#!/usr/bin/env python
import logging

# create logger
module_logger = logging.getLogger('scctool.view')

try:
    import platform
    import base64
    from PyQt5.QtWidgets import *
    from PyQt5.QtCore import *
    from PyQt5.QtGui import *
    from PyQt5.QtQml import *

    import scctool.settings
    import scctool.obs
    import time
    import shutil
    import os
    import re

except Exception as e:
    module_logger.exception("message") 
    raise  
    
class mainWindow(QMainWindow):
    def __init__(self,controller):
        try:
            super(mainWindow, self).__init__()
        
            self.trigger = True
         
            self.createFromMatchDataBox()
            self.createTabs()
            self.createHorizontalGroupBox()
            self.createSC2APIGroupBox()
            
            self.createMenuBar()

            mainLayout = QVBoxLayout()
            mainLayout.addWidget(self.tabs,2)
            mainLayout.addWidget(self.fromMatchDataBox,7)
            mainLayout.addWidget(self.SC2APIGroupBox,1)
            mainLayout.addWidget(self.horizontalGroupBox,1)

            self.setWindowTitle("StarCraft Casting Tool " + scctool.settings.versioncontrol.current)
            
            self.window = QWidget()
            self.window.setLayout(mainLayout)
            self.setCentralWidget(self.window)
        
            #self.size
            self.statusBar()
            
            self.progressBar = BusyProgressBar()

            #self.progressBar.setMaximumHeight(20)
            self.progressBar.setMaximumWidth(160)
            self.progressBar.setMinimumWidth(160)
            self.progressBar.setText("FTP Transfer in progress...")
            self.progressBar.setVisible(False)
            self.statusBar().addPermanentWidget(self.progressBar)

            self.controller = controller
            self.controller.setView(self)
            self.controller.refreshButtonStatus()

            self.show()
            self.controller.testVersion()
        except Exception as e:
            module_logger.exception("message")    


    def closeEvent(self, event):
        try:
            try:
                if(self.mysubwindow1.isVisible()):
                    self.mysubwindow1.close()
            except:
                pass
            self.controller.cleanUp()
            event.accept()
        except Exception as e:
            module_logger.exception("message")    
            
    def createMenuBar(self):
        try:
            menubar = self.menuBar()
            settingsMenu = menubar.addMenu('&Settings') 
            apiAct = QAction(QIcon('src/connection.png'), '&Connections', self)  
            apiAct.setStatusTip('Edit FTP-Settings and API-Settings for Twitch and Nightbot')
            apiAct.triggered.connect(self.openApiDialog)
            settingsMenu.addAction(apiAct)
            styleAct = QAction(QIcon('src/pantone.png'),'&Styles', self)  
            styleAct.setStatusTip('')
            styleAct.triggered.connect(self.openStyleDialog)
            settingsMenu.addAction(styleAct)
            miscAct = QAction(QIcon('src/settings.png'),'&Misc', self)  
            miscAct.setStatusTip('')
            miscAct.triggered.connect(self.openMiscDialog)
            settingsMenu.addAction(miscAct)
            
            
            infoMenu = menubar.addMenu('&Info && Links') 
            
            websiteAct = QAction(QIcon('src/github.ico'),'&StarCraft Casting Tool', self) 
            websiteAct.triggered.connect(self.openWebsite)
            infoMenu.addAction(websiteAct)
            
            ixAct = QAction(QIcon('src/icon.png'), '&team pheeniX', self) 
            ixAct.triggered.connect(self.openIX)
            infoMenu.addAction(ixAct)
            
            alphaAct = QAction(QIcon('src/alphatl.ico'), '&AlphaTL', self) 
            alphaAct.triggered.connect(self.openAlpha)
            infoMenu.addAction(alphaAct)
            
            rstlAct = QAction(QIcon('src/rstl.png'),'&RSTL', self) 
            rstlAct.triggered.connect(self.openRSTL)
            infoMenu.addAction(rstlAct)

        except Exception as e:
            module_logger.exception("message")   
        
    def openWebsite(self):
        self.controller.openURL("https://github.com/teampheenix/StarCraft-Casting-Tool")
        
    def openIX(self):
        self.controller.openURL("http://team-pheenix.de")
        
    def openAlpha(self):
        self.controller.openURL("http://alpha.tl")
        
    def openRSTL(self):
        self.controller.openURL("http://hdgame.net/en/")            
             
    def openApiDialog(self):
        self.mysubwindow1=subwindow1()
        self.mysubwindow1.createWindow(self)
        self.mysubwindow1.show()
        
    def openStyleDialog(self):
        self.mysubwindow2=subwindow2()
        self.mysubwindow2.createWindow(self)
        self.mysubwindow2.show()
        
    def openMiscDialog(self):
        self.mysubwindow3=subwindow3()
        self.mysubwindow3.createWindow(self)
        self.mysubwindow3.show()
        
    def createTabs(self):
        try:
            # Initialize tab screen
            self.tabs = QTabWidget()
            self.tab1 = QWidget()	
            self.tab2 = QWidget()
            #self.tabs.resize(300,200) 
    
            # Add tabs
            self.tabs.addTab(self.tab1,"Match Grabber for AlphaTL && RSTL")
            self.tabs.addTab(self.tab2,"Custom Match")
    
            # Create first tab
            self.tab1.layout = QVBoxLayout()

            self.le_url =  QLineEdit()
            self.le_url.setAlignment(Qt.AlignCenter)
            
            self.le_url.setPlaceholderText("http://alpha.tl/match/2392")
            
            completer = QCompleter(["http://alpha.tl/match/","http://hdgame.net/en/tournaments/list/tournament/rstl-12/"], self.le_url)
            completer.setCaseSensitivity(Qt.CaseInsensitive)
            completer.setCompletionMode(QCompleter.UnfilteredPopupCompletion)
            completer.setWrapAround(True)
            self.le_url.setCompleter(completer)
            self.le_url.setMinimumWidth(self.scoreWidth+2*self.raceWidth+2*self.mimumLineEditWidth+4*6)

            self.pb_openBrowser = QPushButton("Open in Browser")
            self.pb_openBrowser.clicked.connect(self.openBrowser_click)
            self.pb_openBrowser.setMinimumWidth((self.scoreWidth+2*self.raceWidth+2*self.mimumLineEditWidth+4*6)/2-2)
            
            container = QHBoxLayout()
            label = QLabel()
            label.setFixedWidth(self.labelWidth)
            container.addWidget(label,0)
            label = QLabel("Match-URL:")
            label.setMinimumWidth(self.mimumLineEditWidth)
            label.setAlignment(Qt.AlignCenter)
            container.addWidget(label,1)
            container.addWidget(self.le_url,3)
            
            
            self.tab1.layout  = QFormLayout()
            self.tab1.layout.addRow(container)
            
            container = QHBoxLayout()
            
            #self.pb_download = QPushButton("Download Images from URL")
            #container.addWidget(self.pb_download)
            label = QLabel()
            label.setFixedWidth(self.labelWidth)
            container.addWidget(label,0)
            label = QLabel()
            label.setMinimumWidth(self.mimumLineEditWidth)
            container.addWidget(label, 2)
            self.pb_refresh = QPushButton("Load Data from URL")
            self.pb_refresh.clicked.connect(self.refresh_click)
            self.pb_refresh.setMinimumWidth((self.scoreWidth+2*self.raceWidth+2*self.mimumLineEditWidth+4*6)/2-2)
            container.addWidget(self.pb_openBrowser,3)
            container.addWidget(self.pb_refresh,3)

            
            self.tab1.layout.addRow(container)
            self.tab1.setLayout(self.tab1.layout)
            
            # Create second tab
            
            self.tab2.layout = QHBoxLayout()
            self.tab2.layout.addWidget(QLabel("  "),2)
            self.tab2.layout.addWidget(QLabel("Best of"),2)
            
            self.cb_bestof = QComboBox()
            for idx in range(0,7):
                if(idx==1):
                    continue
                self.cb_bestof.addItem(str(idx+1))
            self.cb_bestof.setCurrentIndex(3)
            
            self.cb_bestof.setToolTip('"Best of 6/4": First, a Bo5/3 is played and the ace map gets '+\
                                       'extended to a Bo3 if needed.') 
            self.tab2.layout.addWidget(self.cb_bestof,1)
            
            self.tab2.layout.addWidget(QLabel(" but at least"),3)
            
            self.cb_minSets = QComboBox()
            for idx in range(0,7):
                self.cb_minSets.addItem(str(idx+1))
            self.cb_minSets.setCurrentIndex(0)
            
            self.cb_minSets.setToolTip('Minimum number of maps played (even if the match is decided already)') 
            self.tab2.layout.addWidget(self.cb_minSets,1)
            self.tab2.layout.addWidget(QLabel(" maps"),2)
            
            self.tab2.layout.addWidget(QLabel(""),1)
            self.cb_allkill = QCheckBox("All-Kill Format")
            self.cb_allkill.setChecked(False)
            self.cb_allkill.setToolTip('Winner stays and is automatically placed into the next set') 
            self.tab2.layout.addWidget(self.cb_allkill,3)
            
            self.tab2.layout.addWidget(QLabel(""),0)
            self.pb_resetdata = QPushButton("Reset")
            self.pb_resetdata.clicked.connect(self.resetdata_click)
            self.tab2.layout.addWidget(self.pb_resetdata,4)
            self.pb_applycustom = QPushButton("Apply")
            self.pb_applycustom.clicked.connect(self.applycustom_click)
            self.tab2.layout.addWidget(self.pb_applycustom,4)
            
            self.tab2.setLayout(self.tab2.layout)
            
        except Exception as e:
            module_logger.exception("message")          
        
    def createFromMatchDataBox(self):
        try:
            
            self.max_no_sets = 7
            self.scoreWidth = 35
            self.raceWidth = 45
            self.labelWidth = 13
            self.mimumLineEditWidth = 130
            
            self.fromMatchDataBox = QGroupBox("Match Data")
            layout2 = QFormLayout()
            
            self.le_league  = QLineEdit()
            self.le_league.setText("League TBD")
            self.le_league.setAlignment(Qt.AlignCenter)
            self.le_league.setPlaceholderText("League TBD")
            policy = QSizePolicy()
            policy.setHorizontalStretch(3)
            policy.setHorizontalPolicy(QSizePolicy.Expanding)
            policy.setVerticalStretch(1)
            policy.setVerticalPolicy(QSizePolicy.Preferred)
            self.le_league.setSizePolicy(policy)
            
            self.le_team = [QLineEdit() for y in range(2)]
            self.le_player = [[QLineEdit() for x in range(self.max_no_sets)] for y in range(2)] 
            self.cb_race   = [[QComboBox() for x in range(self.max_no_sets)] for y in range(2)] 
            self.sl_score  = [QSlider(Qt.Horizontal)  for y in range(self.max_no_sets)]  
            self.le_map    = [MapLineEdit()  for y in range(self.max_no_sets)]  
            self.label_set = [QLabel()  for y in range(self.max_no_sets)]  
            
            container = QHBoxLayout()
            for team_idx in range(2):
                self.le_team[team_idx].setText("TBD")
                self.le_team[team_idx].setAlignment(Qt.AlignCenter)
                self.le_team[team_idx].setPlaceholderText("Team "+str(team_idx+1))
                completer = QCompleter(scctool.settings.getMyTeams() + ["TBD"],self.le_team[team_idx])
                completer.setCaseSensitivity(Qt.CaseInsensitive)
                completer.setCompletionMode(QCompleter.InlineCompletion)
                completer.setWrapAround(True)
                self.le_team[team_idx].setCompleter(completer)
                policy = QSizePolicy()
                policy.setHorizontalStretch(4)
                policy.setHorizontalPolicy(QSizePolicy.Expanding)
                policy.setVerticalStretch(1)
                policy.setVerticalPolicy(QSizePolicy.Preferred)
                self.le_team[team_idx].setSizePolicy(policy)
                self.le_team[team_idx].setMinimumWidth(self.mimumLineEditWidth)
            
            self.qb_logo1 = IconPushButton()
            self.qb_logo1.setFixedWidth(self.raceWidth)
            self.qb_logo1.clicked.connect(lambda:self.logoDialog(1))
            pixmap = QIcon(scctool.settings.OBSdataDir+'/logo1.png')
            self.qb_logo1.setIcon(pixmap)
            
            self.qb_logo2 = IconPushButton()
            self.qb_logo2.setFixedWidth(self.raceWidth)
            self.qb_logo2.clicked.connect(lambda:self.logoDialog(2))
            pixmap = QIcon(scctool.settings.OBSdataDir+'/logo2.png')
            self.qb_logo2.setIcon(pixmap)
            
            self.sl_team = QSlider(Qt.Horizontal)
            self.sl_team.setMinimum(-1)
            self.sl_team.setMaximum(1)
            self.sl_team.setValue(0)
            self.sl_team.setTickPosition(QSlider.TicksBothSides)
            self.sl_team.setTickInterval(1)
            self.sl_team.valueChanged.connect(self.sl_changed)
            self.sl_team.setToolTip('Choose your team') 
            self.sl_team.setMinimumHeight(5)
            self.sl_team.setFixedWidth(self.scoreWidth)
            policy = QSizePolicy()
            policy.setHorizontalStretch(0)
            policy.setHorizontalPolicy(QSizePolicy.Fixed)
            policy.setVerticalStretch(1)
            policy.setVerticalPolicy(QSizePolicy.Minimum)
            self.sl_team.setSizePolicy(policy)
            
            
            container = QGridLayout()
            
            label = QLabel("")
            label.setFixedWidth(self.labelWidth)
            container.addWidget(label,0,0,2,1)
            
            label = QLabel("League:")
            label.setAlignment(Qt.AlignCenter)
            policy = QSizePolicy()
            policy.setHorizontalStretch(4)
            policy.setHorizontalPolicy(QSizePolicy.Expanding)
            policy.setVerticalStretch(1)
            policy.setVerticalPolicy(QSizePolicy.Preferred)
            label.setSizePolicy(policy)
            container.addWidget(label,0,1,1,1)
            
            label = QLabel("Maps \ Teams:")
            label.setAlignment(Qt.AlignCenter)
            policy = QSizePolicy()
            policy.setHorizontalStretch(4)
            policy.setHorizontalPolicy(QSizePolicy.Expanding)
            policy.setVerticalStretch(1)
            policy.setVerticalPolicy(QSizePolicy.Preferred)
            label.setSizePolicy(policy)
            container.addWidget(label,1,1,1,1)
            
            container.addWidget(self.qb_logo1,0,2,2,1)
            container.addWidget(self.le_league,0,3,1,3)
            container.addWidget(self.le_team[0],1,3,1,1)
            container.addWidget(self.sl_team,1,4,1,1)
            container.addWidget(self.le_team[1],1,5,1,1)
            container.addWidget(self.qb_logo2,0,6,2,1)
            
            layout2.addRow(container)
            
            for player_idx in range(self.max_no_sets):   
                for team_idx in range(2):
                    self.le_player[team_idx][player_idx].setText("TBD")
                    self.le_player[team_idx][player_idx].setAlignment(Qt.AlignCenter)
                    self.le_player[team_idx][player_idx].setPlaceholderText("Player "+str(player_idx+1)+" of Team "+str(team_idx+1))
                    completer = QCompleter(scctool.settings.getMyPlayers(True), self.le_player[team_idx][player_idx])
                    completer.setCaseSensitivity(Qt.CaseInsensitive)
                    completer.setCompletionMode(QCompleter.InlineCompletion)
                    completer.setWrapAround(True)
                    self.le_player[team_idx][player_idx].setCompleter(completer)
                    self.le_player[team_idx][player_idx].setMinimumWidth(self.mimumLineEditWidth)
                
                    for i in range(4):
                        self.cb_race[team_idx][player_idx].addItem(QIcon("src/"+str(i)+".png"),"")

                    self.cb_race[team_idx][player_idx].setFixedWidth(self.raceWidth)
                    
                    
                self.sl_score[player_idx].setMinimum(-1)
                self.sl_score[player_idx].setMaximum(1)
                self.sl_score[player_idx].setValue(0)
                self.sl_score[player_idx].setTickPosition( QSlider.TicksBothSides)
                self.sl_score[player_idx].setTickInterval(1)
                self.sl_score[player_idx].valueChanged.connect(self.sl_changed)
                self.sl_score[player_idx].setToolTip('Set the score') 
                self.sl_score[player_idx].setFixedWidth(self.scoreWidth)
            
                self.le_map[player_idx].setText("TBD")
                self.le_map[player_idx].setAlignment(Qt.AlignCenter)
                self.le_map[player_idx].setPlaceholderText("Map "+str(player_idx+1))
                self.le_map[player_idx].setMinimumWidth(self.mimumLineEditWidth)
                completer = QCompleter(scctool.settings.maps,self.le_map[player_idx])
                completer.setCaseSensitivity(Qt.CaseInsensitive)
                completer.setCompletionMode(QCompleter.InlineCompletion)
                completer.setWrapAround(True)
                self.le_map[player_idx].setCompleter(completer)
 
                
                #self.le_map[player_idx].setReadOnly(True)
                
                container = QHBoxLayout()
                self.label_set[player_idx].setText("#"+str(player_idx+1))
                self.label_set[player_idx].setAlignment(Qt.AlignCenter)
                self.label_set[player_idx].setFixedWidth(self.labelWidth)
                container.addWidget(self.label_set[player_idx],0)
                container.addWidget(self.le_map[player_idx],4)
                container.addWidget(self.cb_race[0][player_idx],0)
                container.addWidget(self.le_player[0][player_idx],4)
                container.addWidget(self.sl_score[player_idx],0)
                container.addWidget(self.le_player[1][player_idx],4)
                container.addWidget(self.cb_race[1][player_idx],0)
                layout2.addRow(container)
                self.fromMatchDataBox.setLayout(layout2)
                
        except Exception as e:
            module_logger.exception("message")    
        
    def createHorizontalGroupBox(self):
        try:
            self.horizontalGroupBox = QGroupBox("Tasks")
            layout = QHBoxLayout()
           
            self.pb_twitchupdate = QPushButton("Update Twitch Title")
            self.pb_twitchupdate.clicked.connect(self.updatetwitch_click)
            
            self.pb_nightbotupdate = QPushButton("Update NightBot")
            self.pb_nightbotupdate.clicked.connect(self.updatenightbot_click)

            self.pb_resetscore = QPushButton("Reset Score")
            self.pb_resetscore.clicked.connect(self.resetscore_click)
            
            self.pb_obsupdate = QPushButton("Update OBS Data")
            self.pb_obsupdate.clicked.connect(self.updateobs_click)
            
            layout.addWidget(self.pb_twitchupdate)
            layout.addWidget(self.pb_nightbotupdate)
            layout.addWidget(self.pb_resetscore)
            layout.addWidget(self.pb_obsupdate)
            
            self.horizontalGroupBox.setLayout(layout)
        except Exception as e:
            module_logger.exception("message")
        
    def createSC2APIGroupBox(self):
        try:
            self.SC2APIGroupBox = QGroupBox("Automatic Background Tasks")
            layout = QHBoxLayout()
            
            self.cb_autoFTP = QCheckBox("FTP Upload")
            self.cb_autoFTP.setChecked(False)
            self.cb_autoFTP.setToolTip('Automatically uploads all streaming data in the background to a specified FTP server.') 
            self.cb_autoFTP.stateChanged.connect(self.autoFTP_change)

            self.cb_autoUpdate = QCheckBox("Score Update")
            self.cb_autoUpdate.setChecked(False)
            self.cb_autoUpdate.setToolTip('Automatically detects the outcome of SC2 matches that are played/observed'\
                                          ' in your SC2-client and updates the score accordingly.') 
            self.cb_autoUpdate.stateChanged.connect(self.autoUpdate_change)
            
            self.cb_playerIntros = QCheckBox("Player Intros")
            self.cb_playerIntros.setChecked(False)
            self.cb_playerIntros.setToolTip('Update player intros files via SC2-Client-API') 
            self.cb_playerIntros.stateChanged.connect(self.playerIntros_change)
            
            self.cb_autoToggleScore = QCheckBox("Ingame Score")
            self.cb_autoToggleScore.setChecked(False)
            self.cb_autoToggleScore.setToolTip('Automatically sets the score of your ingame UI-interface at the begining of a game.') 
            self.cb_autoToggleScore.stateChanged.connect(self.autoToggleScore_change)
            
            self.cb_autoToggleProduction = QCheckBox("Production Tab")
            self.cb_autoToggleProduction.setChecked(False)
            self.cb_autoToggleProduction.setToolTip('Automatically toogles the production tab of your ingame UI-interface at the begining of a game.') 
            self.cb_autoToggleProduction.stateChanged.connect(self.autoToggleProduction_change)
            
            if(platform.system()!="Windows"):
                self.cb_autoToggleScore.setEnabled(False)
                self.cb_autoToggleScore.setAttribute(Qt.WA_AlwaysShowToolTips)
                self.cb_autoToggleScore.setToolTip('Only Windows') 
                self.cb_autoToggleProduction.setEnabled(False)
                self.cb_autoToggleProduction.setAttribute(Qt.WA_AlwaysShowToolTips)
                self.cb_autoToggleProduction.setToolTip('Only Windows') 
            
            layout.addWidget(self.cb_autoFTP,3)
            layout.addWidget(self.cb_autoUpdate,3)
            layout.addWidget(self.cb_playerIntros,3)
            layout.addWidget(self.cb_autoToggleScore,3)
            layout.addWidget(self.cb_autoToggleProduction,3)
            
            self.SC2APIGroupBox.setLayout(layout)
        except Exception as e:
            module_logger.exception("message")

    def autoFTP_change(self):
        try:
            scctool.settings.Config.set("FTP","upload",str(self.cb_autoFTP.isChecked()))
            if(self.cb_autoFTP.isChecked()):
                signal = self.controller.ftpUploader.connect()
                signal.connect(self.ftpSignal)
                self.controller.matchData.allChanged()
            else:
                self.controller.ftpUploader.disconnect()
        except Exception as e:
            module_logger.exception("message")
            
    def ftpSignal(self, signal):
        
        if(signal == -2):
            QMessageBox.warning(self, "Login error", 'FTP server login incorrect!')
            self.cb_autoFTP.setChecked(False)
        elif(signal == -3):
            self.progressBar.setVisible(False)
        else:
            self.progressBar.setVisible(True)
         
    def autoUpdate_change(self):
        try:
            if(self.cb_autoUpdate.isChecked()):
                self.controller.runSC2ApiThread("updateScore")
            else:
                self.controller.stopSC2ApiThread("updateScore")
        except Exception as e:
            module_logger.exception("message")
            
    def playerIntros_change(self):
        try:
            if(self.cb_playerIntros.isChecked()):
                self.controller.runSC2ApiThread("playerIntros")
                self.controller.runWebsocketThread()
            else:
                self.controller.stopSC2ApiThread("playerIntros")
                self.controller.stopWebsocketThread()
        except Exception as e:
            module_logger.exception("message")    
           
    def autoToggleScore_change(self):
        try:
            if(self.cb_autoToggleScore.isChecked()):
                self.controller.runSC2ApiThread("toggleScore")
            else:
                self.controller.stopSC2ApiThread("toggleScore")
        except Exception as e:
            module_logger.exception("message")
           
                  
    def autoToggleProduction_change(self):
        try:
            if(self.cb_autoToggleProduction.isChecked()):
                self.controller.runSC2ApiThread("toggleProduction")
            else:
                self.controller.stopSC2ApiThread("toggleProduction")
        except Exception as e:
            module_logger.exception("message")
            
    def applycustom_click(self):
        try:
            url = self.le_url.text()
            self.trigger = False
            self.statusBar().showMessage('Applying Custom Match...')
            msg = self.controller.applyCustom(int(self.cb_bestof.currentText()),self.cb_allkill.isChecked(),int(self.cb_minSets.currentText()))
            self.statusBar().showMessage(msg)
            self.trigger = True
        except Exception as e:
            module_logger.exception("message")
            
    def resetdata_click(self):
        try:
            url = self.le_url.text()
            self.trigger = False
            self.statusBar().showMessage('Reading '+url+'...')
            msg = self.controller.resetData()
            self.statusBar().showMessage(msg)
            self.trigger = True
        except Exception as e:
            module_logger.exception("message")
            
    def refresh_click(self):
        try:
            url = self.le_url.text()
            self.trigger = False
            self.statusBar().showMessage('Reading '+url+'...')
            msg = self.controller.refreshData(url)
            self.statusBar().showMessage(msg)
            self.trigger = True
        except Exception as e:
            module_logger.exception("message")
        
    def openBrowser_click(self):
        try:
            url = self.le_url.text()
            self.controller.openURL(url)
        except Exception as e:
            module_logger.exception("message")

    def updatenightbot_click(self):
        try:
            self.statusBar().showMessage('Updating NightBot Command...')
            msg = self.controller.updateNightbotCommand()
            self.statusBar().showMessage(msg)
        except Exception as e:
            module_logger.exception("message")
            
    def updatetwitch_click(self):
        try:
            url = self.le_url.text()
            self.statusBar().showMessage('Updating Twitch Title...')
            msg = self.controller.updateTwitchTitle()
            self.statusBar().showMessage(msg)
        except Exception as e:
            module_logger.exception("message")
        
    def updateobs_click(self):
        try:
            url = self.le_url.text()
            self.statusBar().showMessage('Updating OBS Data...')
            self.controller.updateOBS()
            self.statusBar().showMessage('')
        except Exception as e:
            module_logger.exception("message")
        
    def resetscore_click(self):
        try:
            self.statusBar().showMessage('Resetting Score...')
            self.trigger = False
            for player_idx in range(self.max_no_sets): 
                self.sl_score[player_idx].setValue(0)
            self.controller.updateOBS()
            self.statusBar().showMessage('')
            self.trigger = True
        except Exception as e:
            module_logger.exception("message")
        
    def setScore(self,idx,score):
        try:
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
        except Exception as e:
            module_logger.exception("message")
       
    def sl_changed(self):
        try:
            if(self.trigger):
                self.controller.allkillUpdate()
                self.controller.updateOBS()
        except Exception as e:
            module_logger.exception("message")
            
    def logoDialog(self, button):
        
        #options = QFileDialog.Options()
        #options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,"Select Team Logo", "","PNG images (*.png)")
        if fileName:
            fname = scctool.settings.OBSdataDir+'/logo'+str(button)+'.png'
            shutil.copy(fileName, fname)
            self.controller.updateLogos()
            self.controller.ftpUploader.cwd(scctool.settings.OBSdataDir)
            self.controller.ftpUploader.upload(fname, "logo"+str(button)+".png")
            self.controller.ftpUploader.cwd("..")
            self.controller.matchData.metaChanged()
            self.controller.matchData.updateScoreIcon(self.controller)
            
        
        
class subwindow1(QWidget):
    def createWindow(self,mainWindow):
        
        try:
            parent=None
            super(subwindow1,self).__init__(parent)
            #self.setWindowFlags(Qt.WindowStaysOnTopHint)
            
            self.setWindowIcon(QIcon('src/connection.png'))
            self.mainWindow = mainWindow
            self.passEvent = False
            self.controller = mainWindow.controller
            self.__dataChanged = False
            
            self.createFormGroupFTP()
            self.createFormGroupOBS()
            self.createFormGroupTwitch()
            self.createFormGroupNightbot()
            self.createButtonGroup()
            
            mainLayout = QVBoxLayout()
            mainLayout.addWidget(self.formGroupFTP)
            mainLayout.addWidget(self.formGroupOBS)
            mainLayout.addWidget(self.formGroupTwitch)
            mainLayout.addWidget(self.formGroupNightbot)
            mainLayout.addLayout(self.buttonGroup)
            self.setLayout(mainLayout)
            
            self.resize(QSize(mainWindow.size().width()*.80,self.sizeHint().height()))
            self.move(mainWindow.pos() + QPoint(mainWindow.size().width()/2,mainWindow.size().height()/3)\
                                    - QPoint(self.size().width()/2,self.size().height()/3))
        
            self.setWindowTitle("Connections")
            
        except Exception as e:
            module_logger.exception("message")
            
    def createFormGroupFTP(self):
        self.formGroupFTP = QGroupBox("FTP")
        layout = QFormLayout()
        
        self.ftpServer = MonitoredLineEdit()
        self.ftpServer.textModified.connect(self.changed)
        self.ftpServer.setText(scctool.settings.Config.get("FTP","server").strip())
        self.ftpServer.setAlignment(Qt.AlignCenter)
        self.ftpServer.setPlaceholderText("")
        self.ftpServer.setToolTip('')
        layout.addRow(QLabel("Server:"),self.ftpServer)
        
        self.ftpUser = MonitoredLineEdit()
        self.ftpUser.textModified.connect(self.changed)
        self.ftpUser.setText(scctool.settings.Config.get("FTP","user").strip())
        self.ftpUser.setAlignment(Qt.AlignCenter)
        self.ftpUser.setPlaceholderText("")
        self.ftpUser.setToolTip('')
        layout.addRow(QLabel("User:"),self.ftpUser)
        
        self.ftpPwd = MonitoredLineEdit()
        self.ftpPwd.textModified.connect(self.changed)
        self.ftpPwd.setText(base64.b64decode(scctool.settings.Config.get("FTP","passwd").strip().encode()).decode("utf8"))
        self.ftpPwd.setAlignment(Qt.AlignCenter)
        self.ftpPwd.setPlaceholderText("")
        self.ftpPwd.setToolTip('')
        self.ftpPwd.setEchoMode(QLineEdit.Password)
        label = QLabel("Password:")
        label.setFixedWidth(100)
        layout.addRow(label,self.ftpPwd)
        
        self.ftpDir = MonitoredLineEdit()
        self.ftpDir.textModified.connect(self.changed)
        self.ftpDir.setText(scctool.settings.Config.get("FTP","dir").strip())
        self.ftpDir.setAlignment(Qt.AlignCenter)
        self.ftpDir.setPlaceholderText("currently using root directory")
        self.ftpDir.setToolTip('')
        layout.addRow(QLabel("Directory:"),self.ftpDir)
        
        container = QHBoxLayout()
        self.pb_testFTP = QPushButton('Test && Setup')
        self.pb_testFTP.clicked.connect(self.testFTP)
        container.addWidget(self.pb_testFTP);
        
        layout.addRow(QLabel(""),container)
        
        
        self.formGroupFTP.setLayout(layout)
        
    def testFTP(self):

        self.saveFtpData()
        window = FTPsetup(self.controller, self)
        
    def testOBS(self):
        self.saveOBSdata()
        msg = scctool.obs.testConnection()
        QMessageBox.warning(self, "OBS Websocket Connection Test", msg)

    def createFormGroupOBS(self):
        self.formGroupOBS = QGroupBox("OBS via Websocket Plugin")
        layout = QFormLayout()
        
        self.obsPort = MonitoredLineEdit()
        self.obsPort.textModified.connect(self.changed)
        self.obsPort.setText(scctool.settings.Config.get("OBS", "port"))
        self.obsPort.setAlignment(Qt.AlignCenter)
        self.obsPort.setPlaceholderText("Server Port (Default: 4444)")
        self.obsPort.setToolTip('')
        layout.addRow(QLabel("Server Port:"),self.obsPort)
        
        self.obsPasswd = MonitoredLineEdit()
        self.obsPasswd.textModified.connect(self.changed)
        self.obsPasswd.setText(base64.b64decode(scctool.settings.Config.get("OBS","passwd").strip().encode()).decode("utf8"))
        self.obsPasswd.setEchoMode(QLineEdit.Password)
        self.obsPasswd.setAlignment(Qt.AlignCenter)
        self.obsPasswd.setPlaceholderText("recommended")
        self.obsPasswd.setToolTip('')
        label = QLabel("Password:")
        label.setFixedWidth(100)
        layout.addRow(label, self.obsPasswd)
        
        self.obsSources = MonitoredLineEdit()
        self.obsSources.textModified.connect(self.changed)
        self.obsSources.setText(scctool.settings.Config.get("OBS", "sources"))
        self.obsSources.setAlignment(Qt.AlignCenter)
        self.obsSources.setPlaceholderText("Intro1, Intro2")
        self.obsSources.setToolTip('Name of the OBS-sources that should automatically be hidden 4.5 sec after they become visible.')
        layout.addRow(QLabel("Sources:"),self.obsSources)
        
        container = QHBoxLayout()
        
        self.obsActive = QCheckBox("")
        self.obsActive.setChecked(scctool.settings.Config.getboolean("OBS","active"))
        self.obsActive.setToolTip('') 
        self.obsActive.stateChanged.connect(self.changed)
            
        self.pb_testOBS = QPushButton('Test Connection to OBS')
        self.pb_testOBS.clicked.connect(self.testOBS)
        
        container.addWidget(self.obsActive,1)
        container.addWidget(self.pb_testOBS,3)
        
        
        layout.addRow(QLabel("Active:"),container)
        
        self.formGroupOBS.setLayout(layout)
        
        
    def createFormGroupTwitch(self):
        self.formGroupTwitch = QGroupBox("Twitch")
        layout = QFormLayout()

        self.twitchChannel = MonitoredLineEdit()
        self.twitchChannel.textModified.connect(self.changed)
        self.twitchChannel.setText(scctool.settings.Config.get("Twitch", "channel"))
        self.twitchChannel.setAlignment(Qt.AlignCenter)
        self.twitchChannel.setPlaceholderText("Name of the Twitch channel that should be updated")
        self.twitchChannel.setToolTip('The connected twitch user needs to have editor rights for this channel.')
        layout.addRow(QLabel("Twitch-Channel:"),self.twitchChannel)
 
        
        container = QHBoxLayout()
        
        self.twitchToken = MonitoredLineEdit()
        self.twitchToken.textModified.connect(self.changed)
        self.twitchToken.setText(scctool.settings.Config.get("Twitch", "oauth"))
        self.twitchToken.setAlignment(Qt.AlignCenter)
        self.twitchToken.setPlaceholderText("Press 'Get' to generate a token")
        self.twitchToken.setEchoMode(QLineEdit.Password)
        self.twitchToken.setToolTip("Press 'Get' to generate a new token.")

        container.addWidget(self.twitchToken);
        self.pb_getTwitch = QPushButton('Get')
        container.addWidget(self.pb_getTwitch);
        self.pb_getTwitch.clicked.connect(self.controller.getTwitchToken)
        layout.addRow(QLabel("Access-Token:"),container)
        
        self.twitchTemplate = MonitoredLineEdit()
        self.twitchTemplate.textModified.connect(self.changed)
        self.twitchTemplate.setText(scctool.settings.Config.get("Twitch", "title_template"))
        self.twitchTemplate.setAlignment(Qt.AlignCenter)
        self.twitchTemplate.setPlaceholderText("(TOUR) – (TEAM1) vs (TEAM2)")
        self.twitchTemplate.setToolTip('Placeholders: (TOUR), (TEAM1), (TEAM2)') 
        
        label = QLabel("Title-Template:")
        label.setFixedWidth(100)
        layout.addRow(label, self.twitchTemplate)
        
        self.formGroupTwitch.setLayout(layout)
        
    def createFormGroupNightbot(self):
        self.formGroupNightbot = QGroupBox("Nightbot")
        layout = QFormLayout()
        container = QHBoxLayout()

        self.nightbotToken = MonitoredLineEdit()
        self.nightbotToken.textModified.connect(self.changed)
        self.nightbotToken.setText(scctool.settings.Config.get("NightBot", "token"))
        self.nightbotToken.setAlignment(Qt.AlignCenter)
        self.nightbotToken.setEchoMode(QLineEdit.Password)
        self.nightbotToken.setPlaceholderText("Press 'Get' to generate a token")
        self.nightbotToken.setToolTip("Press 'Get' to generate a new token.")
        
        self.nightbotCommand = MonitoredLineEdit()
        self.nightbotCommand.textModified.connect(self.changed)
        self.nightbotCommand.setText(scctool.settings.Config.get("NightBot", "command"))
        self.nightbotCommand.setPlaceholderText("!matchlink")
        self.nightbotCommand.setAlignment(Qt.AlignCenter)
        
        container.addWidget(self.nightbotToken);
        self.pb_getNightbot = QPushButton('Get')
        self.pb_getNightbot.clicked.connect(self.controller.getNightbotToken)
        #self.pb_getNightbot.setEnabled(False)
        container.addWidget(self.pb_getNightbot);

        layout.addRow(QLabel("Access-Token:"),container)
        label = QLabel("Matchlink command:")
        label.setFixedWidth(100)
        layout.addRow(label, self.nightbotCommand)
        
        self.formGroupNightbot.setLayout(layout)
    
    def createButtonGroup(self):
        try:
            layout = QHBoxLayout()
            
            layout.addWidget(QLabel(""))
            
            buttonCancel = QPushButton('Cancel')
            buttonCancel.clicked.connect(self.closeWindow)
            layout.addWidget(buttonCancel) 
    
            buttonSave = QPushButton('Save && Close')
            buttonSave.clicked.connect(self.saveCloseWindow)
            layout.addWidget(buttonSave) 
            
            self.buttonGroup = layout
        except Exception as e:
            module_logger.exception("message")
            
    def changed(self):
        self.__dataChanged = True
        
    def saveData(self):
        if(self.__dataChanged):
            
            self.saveFtpData()
            
            scctool.settings.Config.set("Twitch", "channel", self.twitchChannel.text().strip())
            scctool.settings.Config.set("Twitch", "oauth", self.twitchToken.text().strip())
            scctool.settings.Config.set("Twitch", "title_template", self.twitchTemplate.text().strip())
            scctool.settings.Config.set("NightBot", "token", self.nightbotToken.text().strip())
            scctool.settings.Config.set("NightBot", "command", self.nightbotCommand.text().strip())
            
            self.saveOBSdata()
            
            self.controller.refreshButtonStatus()

    def saveFtpData(self):
        scctool.settings.Config.set("FTP", "server", self.ftpServer.text().strip())
        scctool.settings.Config.set("FTP", "user", self.ftpUser.text().strip())
        scctool.settings.Config.set("FTP", "passwd", base64.b64encode(self.ftpPwd.text().strip().encode()).decode("utf8"))
        scctool.settings.Config.set("FTP", "dir", self.ftpDir.text().strip())
        
    def saveOBSdata(self):
        scctool.settings.Config.set("OBS", "port", self.obsPort.text().strip())
        scctool.settings.Config.set("OBS", "passwd", base64.b64encode(self.obsPasswd.text().strip().encode()).decode("utf8"))
        scctool.settings.Config.set("OBS", "active", str(self.obsActive.isChecked()))
        scctool.settings.Config.set("OBS", "sources", self.obsSources.text().strip())
      
    def saveCloseWindow(self):
        self.saveData()
        self.passEvent = True
        self.close()   
        
    def closeWindow(self):
        self.passEvent = True
        self.close()    
        
    def closeEvent(self, event):
        try:
            if(not self.__dataChanged):
                event.accept()
                return
            if(not self.passEvent):
                if(self.isMinimized()):
                    self.showNormal()
                buttonReply = QMessageBox.question(self, 'Save data?', "Save data?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if buttonReply == QMessageBox.Yes:
                    self.saveData()
            event.accept()
        except Exception as e:
            module_logger.exception("message")  
            
class subwindow2(QWidget):
    def createWindow(self,mainWindow):
        
        try:
            parent=None
            super(subwindow2,self).__init__(parent)
            #self.setWindowFlags(Qt.WindowStaysOnTopHint)
            
            self.setWindowIcon(QIcon('src/pantone.png'))
            self.mainWindow = mainWindow
            self.passEvent = False
            self.controller = mainWindow.controller
            self.__dataChanged = False
            
            self.createButtonGroup()
            self.createColorBox()
            self.createStyleBox()
            
            mainLayout = QVBoxLayout()
            mainLayout.addWidget(self.styleBox)
            mainLayout.addWidget(self.colorBox)
            mainLayout.addLayout(self.buttonGroup)
            self.setLayout(mainLayout)
            
            self.resize(QSize(mainWindow.size().width()*.80,self.sizeHint().height()))
            self.move(mainWindow.pos() + QPoint(mainWindow.size().width()/2,mainWindow.size().height()/3)\
                                    - QPoint(self.size().width()/2,self.size().height()/3))
        
            self.setWindowTitle("Style Settings")
            
        except Exception as e:
            module_logger.exception("message")
            
    def changed(self):
        self.__dataChanged = True
        
    def createButtonGroup(self):
        try:
            layout = QHBoxLayout()
            
            layout.addWidget(QLabel(""))
            
            buttonCancel = QPushButton('Cancel')
            buttonCancel.clicked.connect(self.closeWindow)
            layout.addWidget(buttonCancel) 
    
            buttonSave = QPushButton('Save && Close')
            buttonSave.clicked.connect(self.saveCloseWindow)
            layout.addWidget(buttonSave) 
            
            self.buttonGroup = layout
        except Exception as e:
            module_logger.exception("message")
            
    def createStyleBox(self):
        self.styleBox = QGroupBox("Styles")
        layout = QFormLayout()
        
        self.qb_boxStyle = StyleComboBox(scctool.settings.OBSmapDir+"/src/css/box_styles", scctool.settings.Config.get("Style", "mapicon_box"))
        self.qb_boxStyle.currentIndexChanged.connect(self.changed)
        label = QLabel("Box Map Icons:")
        label.setMinimumWidth(110)
        layout.addRow(label, self.qb_boxStyle)
        
        self.qb_landscapeStyle = StyleComboBox(scctool.settings.OBSmapDir+"/src/css/landscape_styles", scctool.settings.Config.get("Style", "mapicon_landscape"))
        self.qb_landscapeStyle.currentIndexChanged.connect(self.changed)
        layout.addRow(QLabel("Landscape Map Icons:"),self.qb_landscapeStyle)
        
        self.qb_scoreStyle = StyleComboBox(scctool.settings.OBShtmlDir+"/src/css/score_styles", scctool.settings.Config.get("Style", "score"))
        self.qb_scoreStyle.currentIndexChanged.connect(self.changed)
        layout.addRow(QLabel("Score:"), self.qb_scoreStyle)
        
        self.qb_introStyle = StyleComboBox(scctool.settings.OBShtmlDir+"/src/css/intro_styles", scctool.settings.Config.get("Style", "intro"))
        self.qb_introStyle.currentIndexChanged.connect(self.changed)
        layout.addRow(QLabel("Intros:"), self.qb_introStyle)
        
        self.pb_applyStyles = QPushButton("Apply")
        self.pb_applyStyles.clicked.connect(self.applyStyles)
        layout.addRow(QLabel(), self.pb_applyStyles)
        
        self.styleBox.setLayout(layout)
            
    def applyStyles(self):
        self.qb_boxStyle.apply(self.controller, scctool.settings.OBSmapDir+"/src/css/box.css")
        self.qb_landscapeStyle.apply(self.controller, scctool.settings.OBSmapDir+"/src/css/landscape.css")
        self.qb_scoreStyle.apply(self.controller, scctool.settings.OBShtmlDir+"/src/css/score.css")
        self.qb_introStyle.apply(self.controller, scctool.settings.OBShtmlDir+"/src/css/intro.css")
        
    def createColorBox(self):
        self.colorBox = QGroupBox("Colors")
        layout = QVBoxLayout()
        
        self.default_color = ColorLayout(self, "Default Border:", scctool.settings.Config.get("MapIcons", "default_border_color"), "#f29b00")
        layout.addLayout(self.default_color)
        self. win_color = ColorLayout(self, "Win:", scctool.settings.Config.get("MapIcons", "win_color"), "#008000")
        layout.addLayout(self.win_color)
        self.lose_color = ColorLayout(self, "Lose:", scctool.settings.Config.get("MapIcons", "lose_color"), "#f22200")
        layout.addLayout(self.lose_color)
        self.undecided_color = ColorLayout(self, "Undecided:", scctool.settings.Config.get("MapIcons", "undecided_color"), "#f29b00")
        layout.addLayout(self.undecided_color)
        self.notplayed_color = ColorLayout(self, "Not played:", scctool.settings.Config.get("MapIcons", "notplayed_color"), "#c0c0c0")
        layout.addLayout(self.notplayed_color)
        
        self.colorBox.setLayout(layout)
        
    def saveData(self):
        if(self.__dataChanged):
            scctool.settings.Config.set("MapIcons", "default_border_color", self.default_color.getColor())
            scctool.settings.Config.set("MapIcons", "undecided_color", self.undecided_color.getColor())
            scctool.settings.Config.set("MapIcons", "win_color", self.win_color.getColor())
            scctool.settings.Config.set("MapIcons", "lose_color", self.lose_color.getColor())
            scctool.settings.Config.set("MapIcons", "notplayed_color", self.notplayed_color.getColor())
            
            scctool.settings.Config.set("Style", "mapicon_landscape", self.qb_landscapeStyle.currentText())
            scctool.settings.Config.set("Style", "mapicon_box", self.qb_boxStyle.currentText())
            scctool.settings.Config.set("Style", "score", self.qb_scoreStyle.currentText())
            scctool.settings.Config.set("Style", "intro", self.qb_introStyle.currentText())
            
            self.controller.matchData.allChanged()

    def saveCloseWindow(self):
        self.saveData()
        self.passEvent = True
        self.close()   
        
    def closeWindow(self):
        self.passEvent = True
        self.close()    
        
    def closeEvent(self, event):
        try:
            if(not self.__dataChanged):
                event.accept()
                return
            if(not self.passEvent):
                if(self.isMinimized()):
                    self.showNormal()
                buttonReply = QMessageBox.question(self, 'Save data?', "Save data?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if buttonReply == QMessageBox.Yes:
                    self.saveData()
            event.accept()
        except Exception as e:
            module_logger.exception("message") 
             
class subwindow3(QWidget):
    def createWindow(self,mainWindow):
        
        try:
            parent=None
            super(subwindow3,self).__init__(parent)
            #self.setWindowFlags(Qt.WindowStaysOnTopHint)
            
            self.setWindowIcon(QIcon('src/settings.png'))
            self.mainWindow = mainWindow
            self.passEvent = False
            self.controller = mainWindow.controller
            self.__dataChanged = False
            
            self.createButtonGroup()
            self.createFavBox()

            
            mainLayout = QVBoxLayout()

            mainLayout.addWidget(self.favBox)
            mainLayout.addLayout(self.buttonGroup)
            self.setLayout(mainLayout)
            
            self.resize(QSize(mainWindow.size().width()*.80,self.sizeHint().height()))
            self.move(mainWindow.pos() + QPoint(mainWindow.size().width()/2,mainWindow.size().height()/3)\
                                    - QPoint(self.size().width()/2,self.size().height()/3))
        
            self.setWindowTitle("Miscellaneous Settings")
            
        except Exception as e:
            module_logger.exception("message")
            
    def changed(self):
        self.__dataChanged = True
        
    def createFavBox(self):
        self.favBox = QGroupBox("Favorites")
        layout = QFormLayout()
        
        self.list_favPlayers = ListTable(3, scctool.settings.getMyPlayers())
        self.list_favPlayers.dataModified.connect(self.changed)
        self.list_favPlayers.setFixedHeight(180)
        layout.addRow(QLabel("Players:"),self.list_favPlayers)
        

        self.list_favTeams = ListTable(2, scctool.settings.getMyTeams())
        self.list_favTeams.dataModified.connect(self.changed)
        self.list_favTeams.setFixedHeight(90)
        
        label = QLabel("Teams:")
        label.setFixedWidth(100)
        layout.addRow(label, self.list_favTeams)
        
        self.favBox.setLayout(layout)
        

        
    def createButtonGroup(self):
        try:
            layout = QHBoxLayout()
            
            layout.addWidget(QLabel(""))
            
            buttonCancel = QPushButton('Cancel')
            buttonCancel.clicked.connect(self.closeWindow)
            layout.addWidget(buttonCancel) 
    
            buttonSave = QPushButton('Save && Close')
            buttonSave.clicked.connect(self.saveCloseWindow)
            layout.addWidget(buttonSave) 
            
            self.buttonGroup = layout
        except Exception as e:
            module_logger.exception("message")
            
    def saveData(self):
        if(self.__dataChanged):
            scctool.settings.Config.set("SCT","myteams", ", ".join(self.list_favTeams.getData()))
            scctool.settings.Config.set("SCT","commonplayers", ", ".join(self.list_favPlayers.getData()))

    def saveCloseWindow(self):
        self.saveData()
        self.passEvent = True
        self.close()   
        
    def closeWindow(self):
        self.passEvent = True
        self.close()    
        
    def closeEvent(self, event):
        try:
            if(not self.__dataChanged):
                event.accept()
                return
            if(not self.passEvent):
                if(self.isMinimized()):
                    self.showNormal()
                buttonReply = QMessageBox.question(self, 'Save data?', "Save data?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if buttonReply == QMessageBox.Yes:
                    self.saveData()
            event.accept()
        except Exception as e:
            module_logger.exception("message") 
            
class MapLineEdit(QLineEdit):
    textModified = pyqtSignal(str, str) # (before, after)

    def __init__(self, contents='', parent=None):
        super(MapLineEdit, self).__init__(contents, parent)
        self.editingFinished.connect(self.__handleEditingFinished)
        self.textChanged.connect(self.__handleTextChanged)
        self._before = contents

    def __handleTextChanged(self, text):
        if not self.hasFocus():
            self._before = text

    def __handleEditingFinished(self):
        before, after = self._before, self.text()
        if before != after:
            after, known = scctool.matchdata.autoCorrectMap(after)
            self.setText(after)
            self._before = after
            self.textModified.emit(before, after)
            
class MonitoredLineEdit(QLineEdit):
    
    textModified = pyqtSignal()
    def __init__(self, contents='', parent=None):
        super(MonitoredLineEdit, self).__init__(contents, parent)
        self.editingFinished.connect(self.__handleEditingFinished)
        self.textChanged.connect(self.__handleTextChanged)
        self._before = contents

    def __handleTextChanged(self, text):
        if not self.hasFocus():
            self._before = text
            
    def setTextMonitored(self, after):
        if self._before != after:
            self.textModified.emit()
            
        self.setText(after)

    def __handleEditingFinished(self):
        before, after = self._before, self.text()
        if before != after:
            #after, known = scctool.matchdata.autoCorrectMap(after)
            self.setText(after)
            self._before = after
            self.textModified.emit()
        
class StyleComboBox(QComboBox):
    
    def __init__(self, style_dir, default = "Default"):
        super(StyleComboBox, self).__init__()
        
        self.__style_dir = style_dir
        
        for fname in os.listdir(style_dir):
            full_fname = os.path.join(style_dir, fname)
            if os.path.isfile(full_fname):
                label = re.search('^(.+)\.css$', fname).group(1)
                self.addItem(label)
                
        index = self.findText(default, Qt.MatchFixedString)
        if index >= 0:                                   
            self.setCurrentIndex(index)
        else:
            index = self.findText("Default", Qt.MatchFixedString)
            if index >= 0:                                   
                self.setCurrentIndex(index)
                
    def apply(self, controller, file):
         newfile = os.path.join(self.__style_dir, self.currentText()+".css")
         shutil.copy(newfile, file)
         
         fname = os.path.basename(file)
         dirs = os.path.dirname(file)
         back = dirs.split("/")
         for i in range(len(back)):
            back[i] = ".."
         back = "/".join(back)
         
         controller.ftpUploader.cwd(dirs)
         controller.ftpUploader.upload(file, fname)
         controller.ftpUploader.cwd(back)

         
class FTPsetup(QProgressDialog):
    

    def __init__(self, controller, mainWindow):
        QProgressDialog.__init__(self)
        self.progress = 0
        self.setWindowTitle("FTP Server Setup")
        self.setLabelText("Setting up the required file structure on the FTP server...")
        self.canceled.connect(self.close)
        self.setRange(0, 100)
        self.setValue(self.minimum())
        
        self.resize(QSize(self.sizeHint().width(),self.sizeHint().height()))
        self.move(mainWindow.pos() + QPoint(mainWindow.size().width()/2,mainWindow.size().height()/3)\
                                    - QPoint(self.size().width()/2,self.size().height()/3))
        self.show()
        
        old_bool = mainWindow.mainWindow.cb_autoFTP.isChecked()
        mainWindow.mainWindow.cb_autoFTP.setChecked(False)
        controller.ftpUploader.empty_queque()
        mainWindow.mainWindow.cb_autoFTP.setChecked(True)
        
        signal, range = controller.ftpUploader.setup()
        signal.connect(self.setProgress)
        self.setRange(0, range)
        
        while not self.wasCanceled():
            QApplication.processEvents()
            time.sleep(0.05)
            
        mainWindow.mainWindow.cb_autoFTP.setChecked(False)
        
        if(self.progress != -2):
            controller.ftpUploader.empty_queque()
            mainWindow.mainWindow.cb_autoFTP.setChecked(old_bool)
        else:
            QMessageBox.warning(self, "Login error", 'FTP server login incorrect!')

        print("Done...")
        
    def setProgress(self, progress):
        self.progress = progress
        if(progress == -1):
            self.cancel()
        elif(progress == -2):
            print("Wrong login data")
            self.cancel()
        else:
            self.setValue(progress)
            
            
class BusyProgressBar(QProgressBar):

    def __init__(self):
        super().__init__()
        self.setRange(0, 0)
        self.setAlignment(Qt.AlignCenter)
        self._text = None

    def setText(self, text):
        self._text = text

    def text(self):
        return self._text
        
class ColorLayout(QHBoxLayout):
    def __init__(self, parent, label = "Color:", color = "#ffffff", default_color = "#ffffff"):
        super(QHBoxLayout, self).__init__()
        self.__parent = parent
        self.__defaultColor = default_color
        label = QLabel(label)
        label.setMinimumWidth(110)
        self.addWidget(label, 1)
        self.__preview = QLineEdit()
        self.__preview.setReadOnly(True)
        self.__preview.setAlignment(Qt.AlignCenter)
        self.setColor(color, False)
        self.addWidget(self.__preview, 2)
        self.__pb_selectColor = QPushButton('Select')
        self.__pb_selectColor.clicked.connect(self.__openColorDialog)
        self.addWidget(self.__pb_selectColor, 0)
        self.__pb_default = QPushButton('Default')
        self.__pb_default.clicked.connect(self.reset)
        self.addWidget(self.__pb_default, 0)
        
    def __openColorDialog(self):
        color = QColorDialog.getColor(self.__currentColor)
 
        if color.isValid():
            self.setColor(color.name())
            
    def setColor(self, color, trigger = True):
        new_color = QColor(color)
        if(trigger and self.__currentColor != new_color):
            self.__parent.changed()
        self.__currentColor = new_color
        self.__preview.setText(color)
        self.__preview.setStyleSheet('background: '+color)
        
        if(self.__currentColor.lightnessF() >= 0.5):
            self.__preview.setStyleSheet('background: '+color+';color: black')
        else:
            self.__preview.setStyleSheet('background: '+color+';color: white')
        
    def reset(self):
        self.setColor(self.__defaultColor)
        
    def getColor(self):
        return self.__currentColor.name()
        

class IconPushButton(QPushButton):
    def __init__(self, label=None, parent=None):
        super(IconPushButton, self).__init__(label, parent)

        self.pad = 4     # padding between the icon and the button frame
        self.minSize = 8 # minimum size of the icon

        sizePolicy = QSizePolicy(QSizePolicy.Expanding,
                                       QSizePolicy.Expanding)
        self.setSizePolicy(sizePolicy)

    def paintEvent(self, event):

        qp = QPainter()
        qp.begin(self)

        #---- get default style ----

        opt = QStyleOptionButton()
        self.initStyleOption(opt)

        #---- scale icon to button size ----

        Rect = opt.rect

        h = Rect.height()
        w = Rect.width()
        iconSize = max(min(h, w) - 2 * self.pad, self.minSize)

        opt.iconSize = QSize(iconSize, iconSize)

        #---- draw button ----

        self.style().drawControl(QStyle.CE_PushButton, opt, qp, self)

        qp.end()
        
        
class ListTable(QTableWidget):
    dataModified = pyqtSignal()
    
    def __init__(self, noColumns = 1, data = []):
        super(ListTable, self).__init__()
        
        data = self.__processData(data)
        self.__noColumns = noColumns
        
        self.setCornerButtonEnabled(False)
        self.horizontalHeader().hide()
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.verticalHeader().hide()
        self.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.setData(data)

        
    def __handleDataChanged(self, item):
        self.setData(self.getData())
        self.dataModified.emit()
            
    def __processData(self, data):
        seen = set()
        uniq = [x for x in data if x not in seen and not seen.add(x)] 
        uniq.sort() 
        return uniq
            
    def setData(self, data):
        try:
            self.itemChanged.disconnect()
        except:
            pass
        
        self.setColumnCount(self.__noColumns)
        self.setRowCount(int(len(data)/self.__noColumns)+1)
        for idx, entry in enumerate(data):
            row, column = divmod(idx, self.__noColumns)
            self.setItem(row ,column, QTableWidgetItem(entry))
    
        row = int(len(data)/self.__noColumns)
        for col in range(len(data)%self.__noColumns, self.__noColumns):
            self.setItem(row ,col, QTableWidgetItem(""))
            
        row = int(len(data)/self.__noColumns)+1
        for col in range(self.__noColumns):
            self.setItem(row ,col, QTableWidgetItem(""))
            
        self.itemChanged.connect(self.__handleDataChanged)
            
    def getData(self):
        data = []
        for row in range(self.rowCount()):
            for col in range(self.columnCount()):
                try:
                    element = self.item(row, col).text().strip()
                    if(element == ""):
                        continue
                    data.append(element)
                except:
                    pass
        return self.__processData(data)