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
    import time

except Exception as e:
    module_logger.exception("message") 
    raise  
    
class mainWindow(QMainWindow):
    def __init__(self,controller):
        try:
            super(mainWindow, self).__init__()
        
            self.trigger = True
         
            self.createTabs()
            self.createFromMatchDataBox()
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
        
            self.size
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
                if(self.mySubwindow.isVisible()):
                    self.mySubwindow.close()
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
            apiAct = QAction('&FTP, Twitch, NightBot', self)  
            apiAct.setStatusTip('Edit FTP-Settings and API-Settings for Twitch and Nightbot')
            apiAct.triggered.connect(self.openApiDialog)
            settingsMenu.addAction(apiAct)
            
            infoMenu = menubar.addMenu('&Info') 
            
            websiteAct = QAction('&StarCraft Casting Tool', self) 
            websiteAct.triggered.connect(self.openWebsite)
            infoMenu.addAction(websiteAct)
            
            ixAct = QAction('&team pheeniX', self) 
            ixAct.triggered.connect(self.openIX)
            infoMenu.addAction(ixAct)
            
            alphaAct = QAction('&AlphaTL', self) 
            alphaAct.triggered.connect(self.openAlpha)
            infoMenu.addAction(alphaAct)
            
            rstlAct = QAction('&RSTL', self) 
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
        self.mySubwindow=subwindow()
        self.mySubwindow.createWindow(self)
        self.mySubwindow.show()
        
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
            
            self.pb_openBrowser = QPushButton("Open in Browser")
            self.pb_openBrowser.clicked.connect(self.openBrowser_click)
            
            container = QHBoxLayout()
            container.addWidget(QLabel("  "),0)
            label = QLabel("Match-URL:")
            label.setAlignment(Qt.AlignCenter)
            container.addWidget(label,6)
            container.addWidget(self.le_url,22)
            
            
            self.tab1.layout  = QFormLayout()
            self.tab1.layout .addRow(container)
            
            container = QHBoxLayout()
            
            #self.pb_download = QPushButton("Download Images from URL")
            #container.addWidget(self.pb_download)
            container.addWidget(QLabel("  "),0)
            container.addWidget(QLabel(""),6)
            self.pb_refresh = QPushButton("Load Data from URL")
            self.pb_refresh.clicked.connect(self.refresh_click)
            container.addWidget(self.pb_openBrowser,11)
            container.addWidget(self.pb_refresh,11)

            
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
            #self.cb_allkill.stateChanged.connect(self.autoToggleProduction_change)
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
            
            self.fromMatchDataBox = QGroupBox("Match Data")
            layout2 = QFormLayout()
            
            self.le_league  = QLineEdit()
            self.le_league.setText("League TBD")
            self.le_league.setAlignment(Qt.AlignCenter)
            self.le_league.setPlaceholderText("League TBD")

            container = QHBoxLayout()
            container.addWidget(QLabel("  "),0)
            label = QLabel("League:")
            label.setAlignment(Qt.AlignCenter)
            container.addWidget(label,3)
            container.addWidget(self.le_league,11)
            layout2.addRow(container)
            
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
                completer = QCompleter(scctool.settings.myteams + ["TBD"],self.le_team[team_idx])
                completer.setCaseSensitivity(Qt.CaseInsensitive)
                completer.setCompletionMode(QCompleter.InlineCompletion)
                completer.setWrapAround(True)
                self.le_team[team_idx].setCompleter(completer)
            
            
            #vslabel = QLabel("vs")
            #vslabel.setAlignment(Qt.AlignCenter)
            
            self.sl_team = QSlider(Qt.Horizontal)
            self.sl_team.setMinimum(-1)
            self.sl_team.setMaximum(1)
            self.sl_team.setValue(0)
            self.sl_team.setTickPosition( QSlider.TicksBothSides)
            self.sl_team.setTickInterval(1)
            self.sl_team.valueChanged.connect(self.sl_changed)
            self.sl_team.setToolTip('Choose your team') 
            
            container.addWidget(QLabel("   "),0)
            label = QLabel("Maps \ Teams:")
            label.setAlignment(Qt.AlignCenter)
            container.addWidget(label,3)
            container.addWidget(self.le_team[0],5)    
            container.addWidget(self.sl_team,1)
            container.addWidget(self.le_team[1],5) 
            
            layout2.addRow(container)
            
            for player_idx in range(self.max_no_sets):   
                for team_idx in range(2):
                    self.le_player[team_idx][player_idx].setText("TBD")
                    self.le_player[team_idx][player_idx].setAlignment(Qt.AlignCenter)
                    self.le_player[team_idx][player_idx].setPlaceholderText("Player "+str(player_idx+1)+" of Team "+str(team_idx+1))
                    completer = QCompleter(scctool.settings.commonplayers, self.le_player[team_idx][player_idx])
                    completer.setCaseSensitivity(Qt.CaseInsensitive)
                    completer.setCompletionMode(QCompleter.InlineCompletion)
                    completer.setWrapAround(True)
                    self.le_player[team_idx][player_idx].setCompleter(completer)
                
                    for i in range(4):
                        self.cb_race[team_idx][player_idx].addItem(QIcon("src/"+str(i)+".png"),"")
                    
                    
                self.sl_score[player_idx].setMinimum(-1)
                self.sl_score[player_idx].setMaximum(1)
                self.sl_score[player_idx].setValue(0)
                self.sl_score[player_idx].setTickPosition( QSlider.TicksBothSides)
                self.sl_score[player_idx].setTickInterval(1)
                self.sl_score[player_idx].valueChanged.connect(self.sl_changed)
                self.sl_score[player_idx].setToolTip('Set the score') 
            
                self.le_map[player_idx].setText("TBD")
                self.le_map[player_idx].setAlignment(Qt.AlignCenter)
                self.le_map[player_idx].setPlaceholderText("Map "+str(player_idx+1))
                completer = QCompleter(scctool.settings.maps,self.le_map[player_idx])
                completer.setCaseSensitivity(Qt.CaseInsensitive)
                completer.setCompletionMode(QCompleter.InlineCompletion)
                completer.setWrapAround(True)
                self.le_map[player_idx].setCompleter(completer)
 
                
                #self.le_map[player_idx].setReadOnly(True)
                
                container = QHBoxLayout()
                self.label_set[player_idx].setText("#"+str(player_idx+1))
                self.label_set[player_idx].setAlignment(Qt.AlignCenter)
                container.addWidget(self.label_set[player_idx],0)
                container.addWidget(self.le_map[player_idx],3)
                container.addWidget(self.cb_race[0][player_idx],1)
                container.addWidget(self.le_player[0][player_idx],4)
                container.addWidget(self.sl_score[player_idx],1)
                container.addWidget(self.le_player[1][player_idx],4)
                container.addWidget(self.cb_race[1][player_idx],1)
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
            self.SC2APIGroupBox = QGroupBox("Background Task")
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
            
            layout.addWidget(QLabel("Automatic:"),3)
            layout.addWidget(self.cb_autoFTP,3)
            layout.addWidget(self.cb_autoUpdate,3)
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
            
class subwindow(QWidget):
    def createWindow(self,mainWindow):
        
        try:
            parent=None
            super(subwindow,self).__init__(parent)
            #self.setWindowFlags(Qt.WindowStaysOnTopHint)
            
            self.mainWindow = mainWindow
            self.passEvent = False
            self.controller = mainWindow.controller
            
            self.createFormGroupFTP()
            self.createFormGroupTwitch()
            self.createFormGroupNightbot()
            self.createButtonGroup()
            
            mainLayout = QVBoxLayout()
            mainLayout.addWidget(self.formGroupFTP)
            mainLayout.addWidget(self.formGroupTwitch)
            mainLayout.addWidget(self.formGroupNightbot)
            mainLayout.addLayout(self.buttonGroup)
            self.setLayout(mainLayout)
            
            self.resize(QSize(mainWindow.size().width()*.80,self.sizeHint().height()))
            self.move(mainWindow.pos() + QPoint(mainWindow.size().width()/2,mainWindow.size().height()/3)\
                                    - QPoint(self.size().width()/2,self.size().height()/3))
        
            self.setWindowTitle("FTP, Twitch and Nightbot Settings")
            
        except Exception as e:
            module_logger.exception("message")
            
    def createFormGroupFTP(self):
        self.formGroupFTP = QGroupBox("FTP")
        layout = QFormLayout()
        
        self.ftpServer = QLineEdit()
        self.ftpServer.setText(scctool.settings.Config.get("FTP","server").strip())
        self.ftpServer.setAlignment(Qt.AlignCenter)
        self.ftpServer.setPlaceholderText("")
        self.ftpServer.setToolTip('')
        layout.addRow(QLabel("Server:"),self.ftpServer)
        
        self.ftpUser = QLineEdit()
        self.ftpUser.setText(scctool.settings.Config.get("FTP","user").strip())
        self.ftpUser.setAlignment(Qt.AlignCenter)
        self.ftpUser.setPlaceholderText("")
        self.ftpUser.setToolTip('')
        layout.addRow(QLabel("User:"),self.ftpUser)
        
        self.ftpPwd = QLineEdit()
        self.ftpPwd.setText(base64.b64decode(scctool.settings.Config.get("FTP","passwd").strip().encode()).decode("utf8"))
        self.ftpPwd.setAlignment(Qt.AlignCenter)
        self.ftpPwd.setPlaceholderText("")
        self.ftpPwd.setToolTip('')
        self.ftpPwd.setEchoMode(QLineEdit.PasswordEchoOnEdit)
        label = QLabel("Password:")
        label.setFixedWidth(100)
        layout.addRow(label,self.ftpPwd)
        
        self.ftpDir = QLineEdit()
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

    
    def createFormGroupTwitch(self):
        self.formGroupTwitch = QGroupBox("Twitch")
        layout = QFormLayout()

        self.twitchChannel = QLineEdit()
        self.twitchChannel.setText(scctool.settings.Config.get("Twitch", "channel"))
        self.twitchChannel.setAlignment(Qt.AlignCenter)
        self.twitchChannel.setPlaceholderText("Name of the Twitch channel that should be updated")
        self.twitchChannel.setToolTip('The connected twitch user needs to have editor rights for this channel.')
        layout.addRow(QLabel("Twitch-Channel:"),self.twitchChannel)
 
        
        container = QHBoxLayout()
        
        self.twitchToken = QLineEdit()
        self.twitchToken.setText(scctool.settings.Config.get("Twitch", "oauth"))
        self.twitchToken.setAlignment(Qt.AlignCenter)
        self.twitchToken.setPlaceholderText("Press 'Get' to generate a token")
        self.twitchToken.setEchoMode(QLineEdit.PasswordEchoOnEdit)
        self.twitchToken.setToolTip("Press 'Get' to generate a new token.")

        container.addWidget(self.twitchToken);
        self.pb_getTwitch = QPushButton('Get')
        container.addWidget(self.pb_getTwitch);
        self.pb_getTwitch.clicked.connect(self.controller.getTwitchToken)
        layout.addRow(QLabel("Access-Token:"),container)
        
        self.twitchTemplate = QLineEdit()
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

        self.nightbotToken = QLineEdit()
        self.nightbotToken.setText(scctool.settings.Config.get("NightBot", "token"))
        self.nightbotToken.setAlignment(Qt.AlignCenter)
        self.nightbotToken.setEchoMode(QLineEdit.PasswordEchoOnEdit)
        self.nightbotToken.setPlaceholderText("Press 'Get' to generate a token")
        self.nightbotToken.setToolTip("Press 'Get' to generate a new token.")
        
        self.nightbotCommand = QLineEdit()
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
      
    def saveData(self):
        self.saveFtpData()
        scctool.settings.Config.set("Twitch", "channel", self.twitchChannel.text().strip())
        scctool.settings.Config.set("Twitch", "oauth", self.twitchToken.text().strip())
        scctool.settings.Config.set("Twitch", "title_template", self.twitchTemplate.text().strip())
        scctool.settings.Config.set("NightBot", "token", self.nightbotToken.text().strip())
        scctool.settings.Config.set("NightBot", "command", self.nightbotCommand.text().strip())
        
        self.controller.refreshButtonStatus()

    def saveFtpData(self):
        scctool.settings.Config.set("FTP", "server", self.ftpServer.text().strip())
        scctool.settings.Config.set("FTP", "user", self.ftpUser.text().strip())
        scctool.settings.Config.set("FTP", "passwd", base64.b64encode(self.ftpPwd.text().strip().encode()).decode("utf8"))
        scctool.settings.Config.set("FTP", "dir", self.ftpDir.text().strip())
      
    def saveCloseWindow(self):
        self.saveData()
        self.passEvent = True
        self.close()   
        
    def closeWindow(self):
        self.passEvent = True
        self.close()    
        
    def closeEvent(self, event):
        try:
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

