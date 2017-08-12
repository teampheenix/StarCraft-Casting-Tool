#!/usr/bin/env python
import logging

# create logger
module_logger = logging.getLogger('alphasc2tool.controller')

try:
    from alphasc2tool.matchdata import *
    from alphasc2tool.apithread import *
    from alphasc2tool.webapp import *
    import alphasc2tool.settings
    import alphasc2tool.twitch
    import alphasc2tool.nightbot
    import webbrowser
except Exception as e:
    module_logger.exception("message") 
    raise  

class AlphaController:
    
    def __init__(self):
        try:
            self.matchData = matchData()
            self.SC2ApiThread = SC2ApiThread(self)
            self.webApp = FlaskThread()
            self.webApp.signal.connect(self.webAppDone)
            
        except Exception as e:
            module_logger.exception("message")
    def setView(self,view):
        self.view = view
        try:
            self.matchData.readJsonFile()
            self.view.trigger = False
            self.updateForms()
            self.view.trigger = True
            self.setCBs()
        except Exception as e:
            module_logger.exception("message")    

    def updateForms(self):
        try:
            self.view.le_url.setText(self.matchData.getURL())
            self.view.le_league.setText(self.matchData.getLeague())
            self.view.sl_team.setValue(self.matchData.getMyTeam())
            for i in range(2):
                self.view.le_team[i].setText(self.matchData.getTeam(i))
                
            for i in range(min(self.view.max_no_sets,self.matchData.getNoSets())):
                for j in range(2):
                    self.view.le_player[j][i].setText(self.matchData.getPlayer(j,i))
                    index = self.view.cb_race[j][i].findText(self.matchData.getRace(j,i),\
                                                                Qt.MatchFixedString)
                    if index >= 0:
                        self.view.cb_race[j][i].setCurrentIndex(index)

                self.view.le_map[i].setText(self.matchData.getMap(i))

                self.view.sl_score[i].setValue(self.matchData.getMapScore(i))
                
            for i in range(self.matchData.getNoSets(),self.view.max_no_sets): 
                for j in range(2):
                    self.view.le_player[j][i].hide()
                    self.view.cb_race[j][i].hide()
                self.view.le_map[i].hide()    
                self.view.sl_score[i].hide()
                
            for i in range(min(self.view.max_no_sets,self.matchData.getNoSets())):
                for j in range(2):
                    self.view.le_player[j][i].show()
                    self.view.cb_race[j][i].show()
                self.view.le_map[i].show()    
                self.view.sl_score[i].show()
                    

        except Exception as e:
            module_logger.exception("message")  
            raise  
                
    def updateData(self):     
        try:
            self.matchData.setMyTeam(self.view.sl_team.value())
            self.matchData.setLeague(self.view.le_league.text())

            for i in range(2):
                 self.matchData.setTeam(i,self.view.le_team[i].text())
                
            for i in range(5):
                for j in range(2):
                     self.matchData.setPlayer(j,i,self.view.le_player[j][i].text())
                     self.matchData.setRace(j,i,self.view.cb_race[j][i].currentText())
                
                self.matchData.setMap(i,self.view.le_map[i].text())
                self.matchData.setMapScore(i,self.view.sl_score[i].value(),True)
            
        except Exception as e:
            module_logger.exception("message")    
                    
    def refreshData(self,url):      
        msg = ''
        try:
            self.matchData.parseURL(url)
            self.matchData.grabData()
            self.matchData.writeJsonFile()
            try:
                self.matchData.downloadLogos()
                self.matchData.downloadMatchBanner()
            except:
                pass
            self.updateForms()  
        except Exception as e:
            msg = str(e)
            module_logger.exception("message")    
          
        return msg
        
    def setCBs(self):
        try:
            if(alphasc2tool.settings.CB_ScoreUpdate):
                self.view.cb_autoUpdate.setChecked(True)
                
            if(alphasc2tool.settings.CB_ToggleScore):
                self.view.cb_autoToggleScore.setChecked(True)
                
            if(alphasc2tool.settings.CB_ToggleProd):
                self.view.cb_autoToggleProduction.setChecked(True)
        except Exception as e:
            module_logger.exception("message")    

    def updateOBS(self):
        try:
            self.updateData()
            self.matchData.createOBStxtFiles()
            self.matchData.updateMapIcons()
            self.matchData.writeJsonFile()
        except Exception as e:
            module_logger.exception("message")  
      
            
    def webAppDone(self):
        try:
            self.view.mySubwindow.nightbotToken.setText(FlaskThread._single.token)
            
            self.view.raise_()
            self.view.show()
            self.view.activateWindow()
            
            
            self.view.mySubwindow.raise_()
            self.view.mySubwindow.show()
            self.view.mySubwindow.activateWindow()
            
        except Exception as e:
            module_logger.exception("message")  
            
    def getNightbotToken(self):
        try:
            self.webApp.start()
            webbrowser.open("http://localhost:65010/nightbot")
        except Exception as e:
            module_logger.exception("message")  
       
              
        
    def updateNightbotCommand(self):
        try:
            msg = alphasc2tool.nightbot.updateCommand("http://alpha.tl/match/"+str(self.matchData.jsonData['matchid']))
        except Exception as e:
            msg = str(e)
            module_logger.exception("message") 
            pass 
            
        return msg    
            
        
    def updateTwitchTitle(self):
        try:
            msg = ''
            self.updateData()
            try:
                title = alphasc2tool.settings.Config.get("Twitch","title_template")
                title = title.replace("(TOUR)",self.matchData.jsonData['tournament'])
                title = title.replace("(TEAM1)",self.matchData.jsonData['team1']['name'])
                title = title.replace("(TEAM2)",self.matchData.jsonData['team2']['name'])
                msg = alphasc2tool.twitch.updateTitle(title)
            except Exception as e:
                msg = str(e)
                module_logger.exception("message") 
                pass
            self.matchData.writeJsonFile()
        except Exception as e:
            module_logger.exception("message")    
            
        return msg
        
    def openURL(self,url):
        if(len(url) < 5):
            url = "http://alpha.tl/match/2392"
        try:
            webbrowser.open(url)
        except Exception as e:
            module_logger.exception("message")    
    
    def runSC2ApiThread(self,task):
        try:
            if(not self.SC2ApiThread.isRunning()):
                self.SC2ApiThread.startTask(task)
            else:
                self.SC2ApiThread.cancelTerminationRequest(task)
        except Exception as e:
            module_logger.exception("message")    
          
       
    def stopSC2ApiThread(self,task): 
        try:
            self.SC2ApiThread.requestTermination(task)
        except Exception as e:
            module_logger.exception("message")    
        
    def cleanUp(self):
        try:
            self.SC2ApiThread.requestTermination("ALL")
            self.webApp.terminate()
            self.saveConfig()
            module_logger.info("cleanUp called")   
        except Exception as e:
            module_logger.exception("message")    

    def saveConfig(self):
        try:
            alphasc2tool.settings.Config.set("Form","scoreupdate",str(self.view.cb_autoUpdate.isChecked()))
            alphasc2tool.settings.Config.set("Form","togglescore",str(self.view.cb_autoToggleScore.isChecked()))
            alphasc2tool.settings.Config.set("Form","toggleprod",str(self.view.cb_autoToggleProduction.isChecked()))
            
            cfgfile = open(alphasc2tool.settings.configFile,'w')
            alphasc2tool.settings.Config.write(cfgfile)    
            cfgfile.close()
        except Exception as e:
            module_logger.exception("message")    
        
   
    def requestScoreUpdate(self,newSC2MatchData):
        
        try:
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
        except Exception as e:
            module_logger.exception("message")
            
            
    def refreshButtonStatus(self):
        
        if(not alphasc2tool.settings.twitchIsValid()):
            self.view.pb_twitchupdate.setEnabled(False)
            self.view.pb_twitchupdate.setAttribute(Qt.WA_AlwaysShowToolTips)
            self.view.pb_twitchupdate.setToolTip('Specify your Twitch Settings to use this feature')   
        else:
            self.view.pb_twitchupdate.setEnabled(True)
            self.view.pb_twitchupdate.setAttribute(Qt.WA_AlwaysShowToolTips)
            self.view.pb_twitchupdate.setToolTip('')  
            
        if(not alphasc2tool.settings.nightbotIsValid()):
            self.view.pb_nightbotupdate.setEnabled(False)
            self.view.pb_nightbotupdate.setAttribute(Qt.WA_AlwaysShowToolTips)
            self.view.pb_nightbotupdate.setToolTip('Specify your NightBot Settings to use this feature')   
        else:
            self.view.pb_nightbotupdate.setEnabled(True)
            self.view.pb_nightbotupdate.setAttribute(Qt.WA_AlwaysShowToolTips)
            self.view.pb_nightbotupdate.setToolTip('')  
            
                    
    def requestToggleScore(self,newSC2MatchData):
        
        try:
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
        except Exception as e:
            module_logger.exception("message")    
               