#!/usr/bin/env python
import logging

# create logger
module_logger = logging.getLogger('alphasc2tool.controller')

try:
    from alphasc2tool.matchdata import *
    from alphasc2tool.apithread import *
    import alphasc2tool.settings
    import alphasc2tool.twitch
    import webbrowser
except Exception as e:
    module_logger.exception("message") 
    raise  

class AlphaController:
    
    def __init__(self):
        try:
            self.matchData = AlphaMatchData()
            self.SC2ApiThread = SC2ApiThread(self)
        except Exception as e:
            module_logger.exception("message")
    def setView(self,view):
        self.view = view
        try:
            self.matchData.readJsonFile()
            self.view.trigger = False
            self.updateForms()
            self.view.trigger = True
            self.view.le_url.selectAll()
            self.setCBs()
        except Exception as e:
            module_logger.exception("message")    

    def updateForms(self):
        try:
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
                    self.view.le_map[i].setText(self.matchData.jsonData['maps'][i])
                except:
                    self.view.le_map[i].setText("TBD")
                
                try:
                    value = int(self.matchData.jsonData['games'][i])
                    if(value == 0):
                        value = 0
                    else:
                        value = self.matchData.jsonData['games'][i]*2-3
                        
                    self.view.sl_score[i].setValue(value)
                except:
                    pass
        except Exception as e:
            module_logger.exception("message")    
                
    def updateData(self):     
        try:
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
            if(not('maps' in self.matchData.jsonData)):
                self.matchData.jsonData['maps'] = []  
                
                
            for i in range(2):
                self.matchData.jsonData['team'+str(i+1)]['name'] = self.view.le_team[i].text()
                if(not('tag' in self.matchData.jsonData['team'+str(i+1)])):
                    self.matchData.jsonData['team'+str(i+1)]['tag'] = 'TBD'
                
            for i in range(5):
                for j in range(2):
                    try:
                        self.matchData.jsonData['lineup'+str(j+1)][i]['nickname'] = self.view.le_player[j][i].text()
                        self.matchData.jsonData['lineup'+str(j+1)][i]['race'] = self.view.cb_race[j][i].currentText()
                    except:
                        self.matchData.jsonData['lineup'+str(j+1)].insert(i,\
                            {'nickname': self.view.le_player[j][i].text(),'race': self.view.cb_race[j][i].currentText()})
                
                try:
                    self.matchData.jsonData['maps'][i] = self.view.le_map[i].text()
                except:
                    self.matchData.jsonData['maps'].insert(i,self.view.le_map[i].text())
    
    
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
        except Exception as e:
            module_logger.exception("message")    
                    
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
            module_logger.info("message")    
            pass
          
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
            self.matchData.updateMapIcons(self.view.sl_team.value())
            self.matchData.writeJsonFile()
        except Exception as e:
            module_logger.exception("message")    
        
    def updateTitle(self):
        try:
            msg = ''
            self.updateData()
            try:
                title = alphasc2tool.settings.twitchTitleTemplate
                title = title.replace("<TOUR>",self.matchData.jsonData['tournament'])
                title = title.replace("<TEAM1>",self.matchData.jsonData['team1']['name'])
                title = title.replace("<TEAM2>",self.matchData.jsonData['team2']['name'])
                msg = alphasc2tool.twitch.updateTitle(title)
            except Exception as e:
                msg = str(e)
                module_logger.info("message") 
                pass
            self.matchData.writeJsonFile()
        except Exception as e:
            module_logger.exception("message")    
            
        return msg
        
    def openURL(self,IDorURL):
        try:
            if(len(IDorURL)>0):
                try:
                    self.matchData.setIDorURL(IDorURL)
                    url="http://alpha.tl/match/"+str(self.matchData.getID())
                except:
                    url="http://alpha.tl/match/"
            else:
                url="http://alpha.tl/match/"
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
               
    def NightBotDialog(self):
        pass