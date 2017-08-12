#!/usr/bin/env python
import logging

# create logger
module_logger = logging.getLogger('alphasc2tool.view')

try:
    import platform
    from PyQt5.QtWidgets import *
    from PyQt5.QtCore import *
    from PyQt5.QtGui import *
    from PyQt5.QtQml import *

    import alphasc2tool.settings

except Exception as e:
    module_logger.exception("message") 
    raise  
    
class mainWindow(QMainWindow):
    def __init__(self,controller):
        try:
            super(mainWindow, self).__init__()
        
            self.trigger = True
         
            self.createFormGroupBox()
            self.createFromMatchDataBox()
            self.createHorizontalGroupBox()
            self.createSC2APIGroupBox()
            
            self.createMenuBar()

            mainLayout = QVBoxLayout()
            mainLayout.addWidget(self.formGroupBox,2)
            mainLayout.addWidget(self.fromMatchDataBox,7)
            mainLayout.addWidget(self.SC2APIGroupBox,1)
            mainLayout.addWidget(self.horizontalGroupBox,1)

            self.setWindowTitle("Starcraft 2 Streaming Tool " + alphasc2tool.settings.version)
            
            self.window = QWidget()
            self.window.setLayout(mainLayout)
            self.setCentralWidget(self.window)
        
            self.size
            self.statusBar()

            self.controller = controller
            self.controller.setView(self)
            self.controller.refreshButtonStatus()
            
            self.show()
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
            settingsMenu = menubar.addMenu('Settings') 
            apiAct = QAction('&API-Integration', self)  
            apiAct.setStatusTip('Edit API-Settings for Twitch and Nightbot')
            apiAct.triggered.connect(self.openApiDialog)
            settingsMenu.addAction(apiAct)

        except Exception as e:
            module_logger.exception("message")   
        
             
    def openApiDialog(self):
        self.mySubwindow=subwindow()
        self.mySubwindow.createWindow(self)
        self.mySubwindow.show()
        
    def createFormGroupBox(self):
        try:
            self.formGroupBox = QGroupBox("Match Grabber for AlphaTL && RSTL")
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
            label = QLabel("Match-URL:")
            label.setAlignment(Qt.AlignCenter)
            container.addWidget(label,6)
            container.addWidget(self.le_url,26)
            
            
            layout = QFormLayout()
            layout.addRow(container)
            
            container = QHBoxLayout()
            #self.pb_download = QPushButton("Download Images from URL")
            #container.addWidget(self.pb_download)
            container.addWidget(QLabel(""),6)
            self.pb_refresh = QPushButton("Load Data from URL")
            self.pb_refresh.clicked.connect(self.refresh_click)
            container.addWidget(self.pb_openBrowser,13)
            container.addWidget(self.pb_refresh,13)

            
            layout.addRow(container)
            
            self.formGroupBox.setLayout(layout)
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

            container = QHBoxLayout()
            label = QLabel("League:")
            label.setAlignment(Qt.AlignCenter)
            container.addWidget(label,3)
            container.addWidget(self.le_league,13)
            layout2.addRow(container)
            
            self.le_team = [QLineEdit() for y in range(2)]
            self.le_player = [[QLineEdit() for x in range(self.max_no_sets)] for y in range(2)] 
            self.cb_race   = [[QComboBox() for x in range(self.max_no_sets)] for y in range(2)] 
            self.sl_score  = [QSlider(Qt.Horizontal)  for y in range(self.max_no_sets)]  
            self.le_map    = [MapLineEdit()  for y in range(self.max_no_sets)]  
            
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
            
            for player_idx in range(self.max_no_sets):   
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
                completer = QCompleter(alphasc2tool.settings.maps,self.le_map[player_idx])
                completer.setCaseSensitivity(Qt.CaseInsensitive)
                completer.setCompletionMode(QCompleter.InlineCompletion)
                completer.setWrapAround(True)
                self.le_map[player_idx].setCompleter(completer)
 
                
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
        except Exception as e:
            module_logger.exception("message")

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
            for player_idx in range(5): 
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
                self.controller.updateOBS()
        except Exception as e:
            module_logger.exception("message")
            
class subwindow(QWidget):
    def createWindow(self,mainWindow):
        
        try:
            parent=None
            super(subwindow,self).__init__(parent)
            #self.setWindowFlags(Qt.WindowStaysOnTopHint)
            
            self.passEvent = False
            self.controller = mainWindow.controller
            
            self.createFormGroupTwitch()
            self.createFormGroupNightbot()
            self.createButtonGroup()
            
            mainLayout = QVBoxLayout()
            mainLayout.addWidget(self.formGroupTwitch)
            mainLayout.addWidget(self.formGroupNightbot)
            mainLayout.addLayout(self.buttonGroup)
            self.setLayout(mainLayout)
            
            self.resize(QSize(mainWindow.size().width()*.80,self.sizeHint().height()))
            self.move(mainWindow.pos() + QPoint(mainWindow.size().width()/2,mainWindow.size().height()/3)\
                                    - QPoint(self.size().width()/2,self.size().height()/3))
        
            self.setWindowTitle("API-Integration Settings")
            
        except Exception as e:
            module_logger.exception("message")
            
        
    def createFormGroupTwitch(self):
        self.formGroupTwitch = QGroupBox("Twitch")
        layout = QFormLayout()

        self.twitchChannel = QLineEdit()
        self.twitchChannel.setText(alphasc2tool.settings.Config.get("Twitch", "channel"))
        self.twitchChannel.setAlignment(Qt.AlignCenter)
        layout.addRow(QLabel("Channel:"),self.twitchChannel)
        
        container = QHBoxLayout()
        
        self.twitchToken = QLineEdit()
        self.twitchToken.setText(alphasc2tool.settings.Config.get("Twitch", "oauth"))
        self.twitchToken.setAlignment(Qt.AlignCenter)

        container.addWidget(self.twitchToken);
        self.pb_getTwitch = QPushButton('Get', self)
        self.pb_getTwitch.setEnabled(False)
        container.addWidget(self.pb_getTwitch );

        layout.addRow(QLabel("Access-Token:"),container)
        self.twitchTemplate = QLineEdit()
        
        self.twitchTemplate.setText(alphasc2tool.settings.Config.get("Twitch", "title_template"))
        self.twitchTemplate.setAlignment(Qt.AlignCenter)
        self.twitchTemplate.setToolTip('Placeholder: (TOUR), (TEAM1), (TEAM2)') 
        layout.addRow(QLabel("Title-Template:"), self.twitchTemplate)
        
        self.formGroupTwitch.setLayout(layout)
        
    def createFormGroupNightbot(self):
        self.formGroupNightbot = QGroupBox("Nightbot")
        layout = QFormLayout()
        container = QHBoxLayout()

        self.nightbotToken = QLineEdit()
        self.nightbotToken.setText(alphasc2tool.settings.Config.get("NightBot", "token"))
        self.nightbotToken.setAlignment(Qt.AlignCenter)
        
        self.nightbotCommand = QLineEdit()
        self.nightbotCommand.setText(alphasc2tool.settings.Config.get("NightBot", "command"))
        self.nightbotCommand.setAlignment(Qt.AlignCenter)
        
        container.addWidget(self.nightbotToken);
        self.pb_getNightbot = QPushButton('Get', self)
        self.pb_getNightbot.clicked.connect(self.controller.getNightbotToken)
        #self.pb_getNightbot.setEnabled(False)
        container.addWidget(self.pb_getNightbot);

        layout.addRow(QLabel("Access-Token:"),container)
        layout.addRow(QLabel("Matchlink command:"), self.nightbotCommand)
        
        self.formGroupNightbot.setLayout(layout)
    
    def createButtonGroup(self):
        try:
            layout = QHBoxLayout()
            
            layout.addWidget(QLabel(""))
            
            buttonCancel = QPushButton('Cancel', self)
            buttonCancel.clicked.connect(self.closeWindow)
            layout.addWidget(buttonCancel) 
    
            buttonSave = QPushButton('Save && Close', self)
            buttonSave.clicked.connect(self.saveCloseWindow)
            layout.addWidget(buttonSave) 
            
            self.buttonGroup = layout
        except Exception as e:
            module_logger.exception("message")
      
    def saveData(self):
        alphasc2tool.settings.Config.set("Twitch", "channel", self.twitchChannel.text())
        alphasc2tool.settings.Config.set("Twitch", "oauth", self.twitchToken.text())
        alphasc2tool.settings.Config.set("Twitch", "title_template", self.twitchTemplate.text())
        alphasc2tool.settings.Config.set("NightBot", "token", self.nightbotToken.text())
        alphasc2tool.settings.Config.set("NightBot", "command", self.nightbotCommand.text())
        
        self.controller.refreshButtonStatus()

      
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
            after, known = alphasc2tool.matchdata.autoCorrectMap(after)
            self.setText(after)
            self._before = after
            self.textModified.emit(before, after)
                