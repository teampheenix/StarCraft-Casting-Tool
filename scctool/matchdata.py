#!/usr/bin/env python
import logging

# create logger
module_logger = logging.getLogger('scctool.matchdata')

try:
    import urllib.request
    import requests
    import scctool.settings
    import json
    import re
    import difflib
except Exception as e:
    module_logger.exception("message") 
    raise  

class matchData:

    def __init__(self):
        self.__VALID_PROVIDERS = ['Custom','AlphaSC2','RSTL']
        self.__rawData = None
        self.__initData()
        
    def readJsonFile(self):
        try:
            with open(scctool.settings.jsonFile) as json_file:  
                self.__data = json.load(json_file)
        except Exception as e:
            module_logger.exception("message") 

    def writeJsonFile(self):
        try:
            with open(scctool.settings.jsonFile, 'w') as outfile:  
                json.dump(self.__data, outfile)
        except Exception as e:
            module_logger.exception("message") 
            
    def __str__(self):
        return str(self.__data)
        
    def isValid(self):
        return not self.__data == None
        
    def parseURL(self, url):
        try:
            url = str(url).lower()
        
            if(url.find('alpha') != -1):
                self.setProvider("AlphaSC2")
            elif(url.find('hdgame') != -1):
                self.setProvider("RSTL")
            else:
                self.setProvider("Custom")
            
            self.setID(re.findall('\d+', url )[-1])
        except Exception as e:
            self.setProvider("Custom")
            self.setID(0)
            module_logger.exception("message") 
        
    def __initData(self):
        self.__data = {}
        self.__data['provider'] = self.__VALID_PROVIDERS[0]
        self.__data['league'] = "TBD"
        self.__data['id'] = 0
        self.__data['matchlink'] = ""
        self.__data['no_sets'] = 0
        self.__data['best_of'] = 0
        self.__data['allkill'] = False
        self.__data['my_team'] = 0
        self.__data['teams'] = []
        self.__data['teams'].append({'name':'TBD','tag': None})
        self.__data['teams'].append({'name':'TBD','tag': None})
        self.__data['sets'] = []
        self.__data['players'] = [[],[]]
    
    def setAllKill(self, allkill):
        self.__data['allkill'] = bool(allkill)
    
    def getAllKill(self):      
        return bool(self.__data['allkill'])
        
    def allkillUpdate(self):
        if(not self.getAllKill()):
            return False
            
        for set_idx in range(self.getNoSets()):
            if self.getMapScore(set_idx) == 0:
                if(set_idx == 0):
                    return False 
                team_idx = int((self.getMapScore(set_idx-1)+1)/2)
                if(self.getPlayer(team_idx,set_idx) != "TBD"):
                    return False
                self.setPlayer(team_idx,set_idx,self.getPlayer(team_idx,set_idx-1),\
                                                self.getRace(team_idx,set_idx-1))
                return True
            
        return False
    def setCustom(self, bestof, allkill):
        bestof = int(bestof)
        allkill = bool(allkill)
        no_sets =  bestof + 1 - bestof%2
        self.setNoSets(no_sets, bestof)
        self.resetLabels()
        self.setAllKill(allkill)
        self.setProvider("Custom")
        self.setID(0)
        self.setURL("")
        
    def resetData(self):
        
        for team_idx in range(2):
            for set_idx in range(self.getNoSets()):
                self.setPlayer(team_idx, set_idx, "TBD", "Random")
            self.setTeam(team_idx,"TBD", "TBD")
            
        for set_idx in range(self.getNoSets()):
            self.setMapScore(set_idx, 0)
            self.setMap(set_idx)
            
        self.setLeague("TBD")
        self.setMyTeam(0)
        
    def resetLabels(self):
        best_of = self.__data['best_of']
        no_sets = self.getNoSets()
        ace_start = no_sets-3+2*(best_of%2)
        skip_one = (ace_start+1 == no_sets)
        
        for set_idx in range(ace_start):  
            self.setLabel(set_idx,"Map "+str(set_idx+1))
            
        for set_idx in range(ace_start,no_sets):
            if(skip_one):
                self.setLabel(set_idx,"Ace Map")
            else:
                self.setLabel(set_idx,"Ace Map "+str(set_idx-ace_start+1))
    
    def setNoSets(self,no_sets = 5, bestof = False, resetPlayers = False):
        try:
            no_sets = int(no_sets)
              
            if(no_sets < 0):
                no_sets = 0 
            elif(no_sets > 9):
                no_sets = 9
                
            if((not bestof) or bestof <= 0 or bestof > no_sets):
                self.__data['best_of'] = no_sets
            else:
                self.__data['best_of'] = int(bestof)
                
            
            sets = []
            players = [[],[]]
        
            for i in range(no_sets):
                try:
                    map = self.__data['sets'][i]['map']
                except:
                    map = "TBD"
                try:
                    score = self.__data['sets'][i]['score']
                except:
                    score = 0
                try:
                    label = self.__data['sets'][i]['label']
                except:
                    label = 'Map '+str(i+1)
                for j in range(2):
                    if(not resetPlayers):
                        try:
                            player_name = self.__data['players'][j][i]['name']
                        except:
                            player_name = 'TBD'
                        try:
                            player_race = getRace(self.__data['players'][j][i]['race'])
                        except:
                            player_race = 'Random'
                    else:
                        player_name = 'TBD'
                        player_race = 'Random'
                        
                    players[j].append({'name':player_name,'race':player_race})
                    
                sets.append({'label':label,'map':map,'score':score})
    
            self.__data['no_sets'] = no_sets
            self.__data['sets'] = sets
            self.__data['players'] = players
            
        except Exception as e:
            module_logger.exception("message") 
            
    def setMyTeam(self, myteam):
        if(isinstance(myteam, str)):
            self.__data['my_team'] = self.__selectMyTeam(myteam)
        elif(myteam in [-1,0,1]):
            self.__data['my_team'] = myteam
            return True
        else:
            return False
            
    def getMyTeam(self):
        try:
            return int(self.__data['my_team'])
        except:
            return 0
            
    def __selectMyTeam(self, string):
        teams = [self.getTeam(0).lower(), self.getTeam(1).lower()]
        matches = difflib.get_close_matches(string.lower(),teams,1) 
        if(len(matches) == 0):
            return 0
        elif(matches[0] == teams[0]):
            return -1
        else:
            return 1
            
    def getNoSets(self):
        try:
            return int(self.__data['no_sets'])
        except:
            return 0

    def setMap(self, set_idx, map = "TBD"):
        try:
            if(not (set_idx >= 0 and set_idx < self.__data['no_sets'])):
                return False
                
            self.__data['sets'][set_idx]['map'], _ = autoCorrectMap(map)
            return True
        except:
            return False
            
    def getMap(self, set_idx):
        try:
            if(not (set_idx >= 0 and set_idx < self.__data['no_sets'])):
                return False
                
            return str(self.__data['sets'][set_idx]['map'])
        except:
            return False
         

    def getScore(self):
        score = [0,0]
        
        for set_idx in range(self.getNoSets()):
            map_score = self.getMapScore(set_idx)
            if(map_score < 0):
                score[0] += 1
            elif(map_score > 0):
                score[1] += 1
            else:
                continue
        return score
           
    def getBestOfRaw(self):
        try:
            return int(self.__data['best_of'])
        except:
            return False  
            
    def getBestOf(self):
        try:
            best_of = self.__data['best_of']
            if(best_of % 2): #odd, okay
                return best_of
            else: #even
                score = self.getScore()
                if(min(score) < best_of/2-1):
                    return best_of - 1
                else:
                    return best_of + 1      
            return 
        except:
            return False  
            
    def setMapScore(self, set_idx, score, overwrite = False):
        try:
            if(not (set_idx >= 0 and set_idx < self.__data['no_sets'])):
                return False
            if(score in [-1,0,1]):
                if(overwrite or self.__data['sets'][set_idx]['score'] == 0):
                    self.__data['sets'][set_idx]['score'] = score 
                return True
            else:
                return False
        except:
            return False
            
    def getMapScore(self, set_idx):
        try:
            if(not (set_idx >= 0 and set_idx < self.__data['no_sets'])):
                return False
                
            return int(self.__data['sets'][set_idx]['score'])
        except:
            return False

    def getNextPlayer(self, team_idx):
        
        player = "TBD"
        for set_idx in range(self.getNoSets()):
            if self.getMapScore(set_idx) == 0:
                player = self.getPlayer(team_idx, set_idx)
                break
        
        return player
        
    def getNextRace(self, team_idx):
        
        player = "Random"
        for set_idx in range(self.getNoSets()):
            if self.getMapScore(set_idx) == 0:
                player = self.getRace(team_idx, set_idx)
                break
        
        return player
            
    def setPlayer(self, team_idx, set_idx, name = "TBD", race = False):
        try:
            if(not (set_idx >= 0 and set_idx < self.__data['no_sets']\
                and team_idx in range(2))):
                return False
                
            self.__data['players'][team_idx][set_idx]['name'] = name
            
            if(race):
                self.setRace(team_idx, set_idx, race)
                
            return True    
        except:
            return False
            
    def getPlayer(self, team_idx, set_idx):
        try:
            if(not (set_idx >= 0 and set_idx < self.__data['no_sets']\
                and team_idx in range(2))):
                return False
                
            return self.__data['players'][team_idx][set_idx]['name']
            
        except:
            return False
            
    def setRace(self, team_idx, set_idx, race = "Random"):
        try:
            if(not (set_idx >= 0 and set_idx < self.__data['no_sets']\
                and team_idx in range(2))):
                return False
            
            self.__data['players'][team_idx][set_idx]['race'] = getRace(race)
            return True
        except:
            return False
            
    def getRace(self, team_idx, set_idx):
        try:
            if(not (set_idx >= 0 and set_idx < self.__data['no_sets']\
                and team_idx in range(2))):
                return False
                
            return getRace(self.__data['players'][team_idx][set_idx]['race'])
            
        except:
            return False
    
    def setLabel(self, set_idx, label):
        try:
            if(not (set_idx >= 0 and set_idx < self.__data['no_sets'])):
                return False
            self.__data['sets'][set_idx]['label'] = label
            return True
        except:
            return False
            
    def getLabel(self, set_idx):
        try:
            if(not (set_idx >= 0 and set_idx < self.__data['no_sets'])):
                return False
            return str(self.__data['sets'][set_idx]['label'])
        except:
            return False    
            
    def setTeam(self, team_idx, name, tag = False):
        if( not team_idx in range(2)):
            return False

        self.__data['teams'][team_idx]['name'] = str(name)
        
        if(tag):
            self.setTeamTag(team_idx, tag)
            
        return True    
            
    def getTeam(self, team_idx):
        if( not team_idx in range(2)):
            return False

        return str(self.__data['teams'][team_idx]['name'])
        
    def setTeamTag(self, team_idx, tag):
        if( not team_idx in range(2)):
            return False

        self.__data['teams'][team_idx]['tag'] = str(tag)
        return True
            
    def getTeamTag(self, team_idx):
        if( not team_idx in range(2)):
            return False
        name = str(self.__data['teams'][team_idx]['tag'])
        if(name):
            return str(name)
        else:
            return self.getTeam(team_idx)
            
    def setID(self,id):
        self.__data['id'] = int(id)
        return True
        
    def getID(self):
        return int(self.__data['id'])

    def setLeague(self,league):
        self.__data['league'] = str(league)
        return True
        
    def getLeague(self):
        return self.__data['league']
        
    def setURL(self,url):
        self.__data['matchlink'] = str(url)
        return True
        
    def getURL(self):
        return str(self.__data['matchlink'])        
        
    def setProvider(self,provider):
        if(provider):
            matches = difflib.get_close_matches(provider,self.__VALID_PROVIDERS,1) 
            if(len(matches) == 0):
                self.__data['provider'] = self.__VALID_PROVIDERS[0]
            else:
                self.__data['provider'] = matches[0]
        else:
            self.__data['provider'] = self.__VALID_PROVIDERS[0]
            
        return True    
            
    def getProvider(self):
        return str(self.__data['provider'])
        
     
    def grabData(self, id = False, provider  = False):
        
        if(id):
            self.setID(id)

        if(provider):
            self.setProvider(provider)
            
        provider = self.getProvider()
        grabData = getattr(self, 'grabData'+provider)
        
        try:
            return grabData()
        except:
            raise
        

    def grabDataAlphaSC2(self):
        
        self.setProvider("AlphaSC2")
        url = "http://alpha.tl/api?match="+str(self.getID())
        data = requests.get(url=url).json()
            
        if(data['code']!=200):
            msg = 'API-Error: '+data['error']
            raise ValueError(msg)
        else:
            self.__rawData = data
            self.setURL("http://alpha.tl/match/"+str(self.getID()))
            self.setNoSets(5, resetPlayers = True)
            self.setLeague(data['tournament'])
            
            for idx, map in enumerate(data['maps']):
                self.setMap(idx,map)
            
            self.setLabel(4,"Ace Map")  
            
            for team_idx in range(2):
                for set_idx, player in enumerate(data['lineup'+str(team_idx+1)]):
                    self.setPlayer(team_idx, set_idx, player['nickname'], player['race'])  
                    
                team = data['team'+str(team_idx+1)]
                self.setTeam(team_idx, team['name'], team['tag'])
            
            totalScore = [0,0]    
            
            
            for set_idx in range(5):
                try:
                    score = int(data['games'][set_idx])*2-3
                except: 
                    score = 0
                    
                self.setMapScore(set_idx, score)


    def grabDataRSTL(self):
        self.setProvider("RSTL") 
        url = "http://hdgame.net/index.php?ajax=1&do=tournament&act=api&data_type=json&lang=en&service=match&match_id="+str(self.getID())
        data = requests.get(url=url).json()
        
        if(data['code']!="200"):
            msg = 'API-Error: '+data['code']
            raise ValueError(msg)
        else:
            data = data['data']
            self.__rawData = data
            self.setURL("http://hdgame.net/en/tournaments/list/tournament/rstl-12/tmenu/tmatches/?match="+str(self.getID()))
            self.setNoSets(7,6, resetPlayers = True)
            self.setLeague(data['tournament']['name'])
            
            for set_idx in range(7):
                self.setMap(set_idx, data['start_maps'][str(set_idx)]['name'])
                
            for team_idx in range(2): 
                for set_idx in range(4):
                    try:
                        self.setPlayer(team_idx, set_idx, data['lu'+str(team_idx+1)][str(set_idx)]['member_name'],\
                                                          data['lu'+str(team_idx+1)][str(set_idx)]['r_name'])
                    except:
                        pass
                        
                for set_idx in range(4,7):
                    try:
                        if(not data['result'][str(4+set_idx)]['r_name'+str(team_idx+1)]):
                            try:
                                race = data['result'][str(4+set_idx+1)]['r_name'+str(team_idx+1)]
                            except:
                                race = "Random"
                        self.setPlayer(team_idx, set_idx, data['result'][str(4+set_idx)]['tu_name'+str(team_idx+1)], race)
                    except:
                        pass
                    
                team = data['member'+str(team_idx+1)]
                self.setTeam(team_idx, team['name'], team['tag'])
                
            self.setLabel(4,"Ace Map 1")  
            self.setLabel(5,"Ace Map 2") 
            self.setLabel(6,"Ace Map 3") 
            
            totalScore = [0,0]    
                
            for set_idx in range(4):
                try:
                    score1 = int(data['result'][str(set_idx*2)]['score1'])
                    score2 = int(data['result'][str(set_idx*2)]['score2'])
                except:
                    score1 = 0
                    score2 = 0
                    
                if(score1 > score2):
                    score = -1
                elif(score1 < score2):
                    score = 1
                else:
                    score = 0
                self.setMapScore(set_idx, score)
                if(score<0):
                    totalScore[0] += 1
                elif(score>0):
                    totalScore[1] += 1
                    
            for set_idx in range(4,7):
                try:
                    score1 = int(data['result'][str(4+set_idx)]['score1'])
                    score2 = int(data['result'][str(4+set_idx)]['score2'])
                except:
                    score1 = 0
                    score2 = 0
                    
                if(score1 > score2):
                    score = -1
                elif(score1 < score2):
                    score = 1
                else:
                    score = 0
                self.setMapScore(set_idx, score)

        
    def grabDataCustom(self):
        raise ValueError("Error: You cannot grab data from a custom provider")
        
    def downloadMatchBanner(self):
        downloadMatchBanner = getattr(self, 'downloadMatchBanner'+self.getProvider())
        return downloadMatchBanner()
        
    def downloadMatchBannerAlphaSC2(self):
        try:
            fname = scctool.settings.OBSdataDir+"/matchbanner.png"
            urllib.request.urlretrieve("http://alpha.tl/announcement/"+str(self.getID())+"?vs", fname) 
        except Exception as e:
            module_logger.exception("message") 
        
    def downloadMatchBannerRSTL(self):
        raise UserWarning("Error: You cannot download a match banner from RSTL")
        
    def downloadMatchBannerCustom(self):
        raise UserWarning("Error: You cannot download a match banner from a custom provider")
        
    def downloadLogos(self):
        downloadLogos = getattr(self, 'downloadLogos'+self.getProvider())
        return downloadLogos()
        
    def downloadLogosAlphaSC2(self):
        try:
            for i in range(1,3):
                fname = scctool.settings.OBSdataDir+"/logo"+str(i)+".png"
                urllib.request.urlretrieve(self.__rawData['team'+str(i)]['logo'], fname) 
        except Exception as e:
            module_logger.exception("message") 
        
    def downloadLogosRSTL(self):
        try:
            for i in range(1,3):
                fname = scctool.settings.OBSdataDir+"/logo"+str(i)+".png"
                urllib.request.urlretrieve("http://hdgame.net"+self.__rawData['member'+str(i)]['img_m'], fname) 
        except Exception as e:
            module_logger.exception("message") 
        
    def downloadLogosCustom(self):
        raise UserWarning("Error: You cannot download a logos from a custom provider")
        
    def createOBStxtFiles(self):
        try:
            f = open(scctool.settings.OBSdataDir+"/lineup.txt", mode = 'w')
            f2 = open(scctool.settings.OBSdataDir+"/maps.txt", mode = 'w')
            for idx in range(self.getNoSets()):
                map = self.getMap(idx)
                f3 = open(scctool.settings.OBSdataDir+"/map"+str(idx+1)+".txt", mode = 'w')
                f.write(map+"\n")
                f2.write(map+"\n")
                f3.write(map+"\n")
                try:
                    string = self.getPlayer(0,idx)+' vs '+self.getPlayer(1,idx)
                    f.write(string+"\n\n")
                    f3.write(string+"\n")
                except IndexError:
                    f.write("\n\n")
                    f3.write("\n")
                    pass 
                f3.close()    
            f.close()
            f2.close()

            f = open(scctool.settings.OBSdataDir+"/teams_vs_long.txt", mode = 'w')
            f.write(self.getTeam(0)+' vs '+self.getTeam(1)+"\n")
            f.close()
            
            f = open(scctool.settings.OBSdataDir+"/teams_vs_short.txt", mode = 'w')
            f.write(self.getTeamTag(0)+' vs '+self.getTeamTag(1)+"\n")
            f.close()
        
            f = open(scctool.settings.OBSdataDir+"/team1.txt", mode = 'w')
            f.write(self.getTeam(0))
            f.close()
        
            f = open(scctool.settings.OBSdataDir+"/team2.txt", mode = 'w')
            f.write(self.getTeam(1))
            f.close()
        
            f = open(scctool.settings.OBSdataDir+"/tournament.txt", mode = 'w')
            f.write(self.getLeague())
            f.close()
    
            try:
                score = self.getScore()
                score_str = str(score[0])+" - "+str(score[1])
            except:
                score_str = "0 - 0"
                
            f = open(scctool.settings.OBSdataDir+"/score.txt", mode = 'w')
            f.write(score_str)
            f.close()
            
            f = open(scctool.settings.OBSdataDir+"/nextplayer1.txt", mode = 'w')
            f.write(self.getNextPlayer(0))
            f.close()
            
            f = open(scctool.settings.OBSdataDir+"/nextplayer2.txt", mode = 'w')
            f.write(self.getNextPlayer(1))
            f.close()
            
            f = open(scctool.settings.OBSdataDir+"/nextrace1.txt", mode = 'w')
            f.write(self.getNextRace(0))
            f.close()
            
            f = open(scctool.settings.OBSdataDir+"/nextrace2.txt", mode = 'w')
            f.write(self.getNextRace(1))
            f.close()
            
        except Exception as e:
            module_logger.exception("message") 
            
            
    def updateMapIcons(self):
        try:
            team = self.getMyTeam()
            score = [0,0]
            for i in range(self.getNoSets()):
                filename=scctool.settings.OBSmapDirData+"/"+str(i+1)+".html"
   
                winner = self.getMapScore(i)
                player1 = self.getPlayer(0,i)
                player2 = self.getPlayer(1,i)
                    
                won=winner*team
                opacity = "0.0"
                
                threshold = int(self.getBestOf()/2)
                
                if(score[0]>threshold or score[1] >threshold):
                    border_color=scctool.settings.notplayed_border_color
                    opacity = scctool.settings.notplayed_opacity 
                    winner = 0
                elif(won==1):
                    border_color=scctool.settings.win_border_color 
                elif(won==-1):
                    border_color=scctool.settings.lose_border_color
                else:
                    border_color=scctool.settings.default_border_color 
            
                if(winner==-1):
                    player1='<font color="'+scctool.settings.win_font_color+'">'+player1+'</font>'
                    score[0] +=  1
                elif(winner==1):
                    player2='<font color="'+scctool.settings.win_font_color+'">'+player2+'</font>'
                    score[1] +=  1
                    
                map=self.getMap(i)
                mappng=map.replace(" ","_")+".jpg"
                race1png=self.getRace(0,i)+".png"
                race2png=self.getRace(1,i)+".png"
                hidden = ""
    
                with open(scctool.settings.OBSmapDir+"/data_template.html", "rt") as fin:
                    with open(filename, "wt") as fout:
                        for line in fin:
                            line = line.replace('%PLAYER1%', player1).replace('%PLAYER2%', player2)
                            line = line.replace('%RACE1_PNG%', race1png).replace('%RACE2_PNG%', race2png)
                            line = line.replace('%MAP_PNG%', mappng).replace('%MAP_NAME%', map)
                            line = line.replace('%MAP_ID%',self.getLabel(i))
                            line = line.replace('%BORDER_COLOR%',border_color).replace('%OPACITY%',opacity)
                            line = line.replace('%HIDDEN%',hidden)
                            fout.write(line)
                            
            for i in range(self.getNoSets(),7): 
                filename=scctool.settings.OBSmapDirData+"/"+str(i+1)+".html"             
                hidden = "visibility: hidden;"
                with open(scctool.settings.OBSmapDir+"/data_template.html", "rt") as fin:
                    with open(filename, "wt") as fout:
                        for line in fin:
                            line = line.replace('%HIDDEN%',hidden)
                            fout.write(line)
                            
        except Exception as e:
            module_logger.exception("message") 
      
def autoCorrectMap(map):
    try:
        matches = difflib.get_close_matches(map.lower(),scctool.settings.maps,1) 
        if(len(matches) == 0):
            return map, False
        else:
            return matches[0], True
            
    except Exception as e:
        module_logger.exception("message") 
        
def getRace(str):
    try: 
        for idx, race in enumerate(scctool.settings.races):
            if(str[0].upper()==race[0].upper()):
                return scctool.settings.races[idx]
    except:
        pass
    
    return "Random"
            
             
if __name__ == '__main__':
    testData = matchData()
    testData.grabData(1806,"RSTL")
    testData.setMyTeam("Mixed mind")
    testData.writeJsonFile()
    testData.updateMapIcons()
