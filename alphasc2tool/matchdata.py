#!/usr/bin/env python
import urllib.request
import requests
import alphasc2tool.settings
import json

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
        with open(alphasc2tool.settings.jsonFile) as json_file:  
            self.jsonData = json.load(json_file)

    def writeJsonFile(self):
        with open(alphasc2tool.settings.jsonFile, 'w') as outfile:  
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
            
        if(self.jsonData['team1']['name']==alphasc2tool.settings.myteam):
            self.jsonData['myteam']=-1
        elif(self.jsonData['team2']['name']==alphasc2tool.settings.myteam):
            self.jsonData['myteam']=1
        else:
            self.jsonData['myteam']=0
            
    def downloadMatchBanner(self, id=-1):
        
        self.getID(id)
        fname = alphasc2tool.settings.OBSdataDir+"/matchbanner.png"
        urllib.request.urlretrieve("http://alpha.tl/announcement/"+self.id+"?vs", fname) 
        
    def downloadLogos(self):
        
        for i in range(1,3):
            fname = alphasc2tool.settings.OBSdataDir+"/logo"+str(i)+".png"
            urllib.request.urlretrieve(self.jsonData['team'+str(i)]['logo'], fname) 
            
    def createOBStxtFiles(self):
       
        f = open(alphasc2tool.settings.OBSdataDir+"/lineup.txt", mode = 'w')
        f2 = open(alphasc2tool.settings.OBSdataDir+"/maps.txt", mode = 'w')
        for idx, map in enumerate(self.jsonData['maps']):
            f3 = open(alphasc2tool.settings.OBSdataDir+"/map"+str(idx+1)+".txt", mode = 'w')
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
      
        f = open(alphasc2tool.settings.OBSdataDir+"/teams_vs_long.txt", mode = 'w')
        f.write(self.jsonData['team1']['name']+' vs '+self.jsonData['team2']['name']+"\n")
        f.close()
        
        f = open(alphasc2tool.settings.OBSdataDir+"/teams_vs_short.txt", mode = 'w')
        f.write(self.jsonData['team1']['tag']+' vs '+self.jsonData['team2']['tag']+"\n")
        f.close()
      
        f = open(alphasc2tool.settings.OBSdataDir+"/team1.txt", mode = 'w')
        f.write(self.jsonData['team1']['name'])
        f.close()
      
        f = open(alphasc2tool.settings.OBSdataDir+"/team2.txt", mode = 'w')
        f.write(self.jsonData['team2']['name'])
        f.close()
      
        f = open(alphasc2tool.settings.OBSdataDir+"/tournament.txt", mode = 'w')
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
            
        f = open(alphasc2tool.settings.OBSdataDir+"/score.txt", mode = 'w')
        f.write(score_str)
        f.close()
        
    def updateMapIcons(self,team=0):
        team = int(team)
        score = [0,0]
        for i in range(1,6):
            filename=alphasc2tool.settings.OBSmapDirData+"/"+str(i)+".html"
         
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
                border_color=alphasc2tool.settings.notplayed_border_color
                opacity = alphasc2tool.settings.notplayed_opacity 
            elif(won==1):
                border_color=alphasc2tool.settings.win_border_color 
            elif(won==-1):
                border_color=alphasc2tool.settings.lose_border_color
            else:
                border_color=alphasc2tool.settings.default_border_color 
        
            if(winner==-1):
                player1='<font color="'+alphasc2tool.settings.win_font_color+'">'+player1+'</font>'
                score[0] +=  1
            elif(winner==1):
                player2='<font color="'+alphasc2tool.settings.win_font_color+'">'+player2+'</font>'
                score[1] +=  1
                
            mappng=map_name.replace(" ","_")+".jpg"
            race1png=race1+".png"
            race2png=race2+".png"

            with open(alphasc2tool.settings.OBSmapDir+"/data_template.html", "rt") as fin:
                with open(filename, "wt") as fout:
                    for line in fin:
                        line = line.replace('%PLAYER1%', player1).replace('%PLAYER2%', player2)
                        line = line.replace('%RACE1_PNG%', race1png).replace('%RACE2_PNG%', race2png)
                        line = line.replace('%MAP_PNG%', mappng).replace('%MAP_NAME%', map_name)
                        line = line.replace('%MAP_ID%',map_id)
                        line = line.replace('%BORDER_COLOR%',border_color).replace('%OPACITY%',opacity)
                        fout.write(line)