#!/usr/bin/python
import logging

# create logger
module_logger = logging.getLogger('scctool.settings')

try:
    import configparser
    import os
    import re
    import urllib.request
    from PyQt5.QtCore import *
except Exception as e:
    module_logger.exception("message") 
    raise  

class VersionControl:
    def __init__(self):
         self.__version_file = "src/version"
         self.__url = "https://raw.githubusercontent.com/teampheenix/StarCraft-Casting-Tool/master/src/version"
         self.current, self.major, self.minor, self.patch = self.__get_from_file(self.__version_file)
         
         self.latest = self.current

    def __parse(self,string):
        string = str(string)
        string = string.strip()
        m = re.search("^v([0-9]+)\.([0-9]+)\.([0-9]+)$",string)
        major = int(m.group(1))
        minor = int(m.group(2))
        patch = int(m.group(3))
        
        return major, minor, patch
        
    def __get_from_file(self,version_file):
        try:
            f = open(version_file, 'r')
            version = f.readline().strip()
            f.close()
            major, minor, patch = self.__parse(version)
        except:
            return 'v0.0.0', 0, 0, 0
        
        return version, major, minor, patch

    def __latest(self):
        try:
            with urllib.request.urlopen(self.__url) as response:
                latest_version = response.read().decode("utf8").strip()
                
            major, minor, patch = self.__parse(latest_version)
            return latest_version,  major, minor, patch
            
        except:
            version = 'v0.0.0', 0, 0, 0
            
    def new_version_avaiable(self):
        self.latest, lmajor, lminor, lpatch  = self.__latest()
        if(lmajor > self.major or\
            (lmajor == self.major and (lminor > self.minor \
                or (lminor == self.minor and lpatch > self.patch)))):
            return True
        return False
    
class CheckVersionThread(QThread):
    
    def __init__(self, controller,versionc, parent = None):
        QThread.__init__(self, parent)
        self.controller = controller
        self.versionc = versionc
        
    def run(self):
        if(self.versionc.new_version_avaiable()):
            self.controller.newVersionTrigger(self.versionc.latest)
            
class PlaceholderList:
    
    def __init__(self):
         self.__ls  = "("
         self.__rs  = ")"
         self.__data = {}
         self.__type = {}
         
    def addConnection(self, placeholder, connection):
        self.__data[placeholder] = connection
        self.__type[placeholder] = "connection"
        
    def addString(self, placeholder, string):
        self.__data[placeholder] = string
        self.__type[placeholder] = "string"
        
    def replace(self, string):
        for placeholder in self.__data:
            if(self.__type[placeholder] == "string"):
                replacement = self.__data[placeholder]
            elif(self.__type[placeholder] == "connection"):
                replacement = self.__data[placeholder]()
            else:
                replacement = ""
                
            string = string.replace(self.__ls+placeholder+self.__rs, replacement)

        return string
        
    def available(self):
        
        placeholders = []
        
        for placeholder in self.__data.keys():
            placeholders.append(self.__ls+placeholder+self.__rs)
            
        placeholders.sort()
        
        return placeholders
    
try:
    versioncontrol = VersionControl()
    configFile = "config.ini"
    jsonFile   = "src/data.json"
    OBSdataDir = "OBS_data"
    OBShtmlDir = "OBS_html"
    OBSmapDir  = "OBS_mapicons"
    
    races = ("Random","Terran","Protoss","Zerg")
    
    def race2idx(str):
        for idx, race in enumerate(races):
            if(race.lower() == str.lower()):
               return idx
        return 0
     
    def idx2race(idx):
        try:
            return races[idx]
        except:
            return races[0]
            
    max_no_sets = 9
    
    #Creating directories if not exisiting 
    if not os.path.exists(OBSdataDir):
        os.makedirs(OBSdataDir)
        
    #Reading the configuration from file
    Config = configparser.ConfigParser()
    try:
        Config.read(configFile)
    except:
        Config.defaults()
        
    #Setting default values for config file
    
    def setDefaultConfig(sec,opt,value):
        if(not Config.has_section(sec)):
            Config.add_section(sec)
        if(not Config.has_option(sec,opt)):
            Config.set(sec,opt,value)
    
    setDefaultConfig("Twitch","channel","")
    setDefaultConfig("Twitch","oauth","")
    setDefaultConfig("Twitch","title_template","(League) – (Team1) vs (Team2)")
    
    setDefaultConfig("NightBot","token","")
    setDefaultConfig("NightBot","command","!matchlink")
    setDefaultConfig("NightBot","message","(URL)")
    
    setDefaultConfig("FTP","upload","False")
    setDefaultConfig("FTP","server","")
    setDefaultConfig("FTP","user","")
    setDefaultConfig("FTP","passwd","")
    setDefaultConfig("FTP","dir","")
    
    setDefaultConfig("SCT","myteams","MiXed Minds, team pheeniX")
    setDefaultConfig("SCT","commonplayers","Shakyor, pressure, MarineKing, Moash, Ostseedude, spaz, DERASTAT, FanTasY,"+\
                           "chrismaverik, holden, Desolation, RiseOfDeath, TuneTrigger, MoFuJones, Fenix, Hyvaa, snoozle,"+\
                           " CptWobbles, dreign, Sly, Sonarwolf, Unknown, Xoneon")
    setDefaultConfig("SCT","fuzzymatch","True")
    
    setDefaultConfig("Form","scoreupdate","False")
    setDefaultConfig("Form","togglescore","False")
    setDefaultConfig("Form","toggleprod", "False")
    setDefaultConfig("Form","playerintros", "False")

    setDefaultConfig("MapIcons","default_border_color","#f29b00")
    setDefaultConfig("MapIcons","undecided_color","#f29b00")
    setDefaultConfig("MapIcons","win_color","#008000")
    setDefaultConfig("MapIcons","lose_color","#f22200")
    setDefaultConfig("MapIcons","notplayed_color","#c0c0c0")
    setDefaultConfig("MapIcons","notplayed_opacity","0.4")
    
    setDefaultConfig("Style", "mapicon_box", "Default")
    setDefaultConfig("Style", "mapicon_landscape", "Default")
    setDefaultConfig("Style", "score", "Default")
    setDefaultConfig("Style", "intro", "Default")
    
    setDefaultConfig("OBS","port", "4444")
    setDefaultConfig("OBS","active", "False")
    setDefaultConfig("OBS","passwd","")
    setDefaultConfig("OBS","sources","Intro1, Intro2")
    

    def ftpIsValid():
         return len(Config.get("FTP", "server"))>0

    def nightbotIsValid():
        return (len(Config.get("NightBot", "token"))>0 and len(Config.get("NightBot", "command"))>0)
    
    def twitchIsValid():
        twitchChannel = Config.get("Twitch", "Channel")
        oauth = Config.get("Twitch", "oauth")
    
        
        return (len(oauth)>0 and len(twitchChannel)>0)
    
        
    
    CB_ScoreUpdate = Config.getboolean("Form","scoreupdate")
    CB_ToggleScore = Config.getboolean("Form","togglescore")
    CB_ToggleProd  = Config.getboolean("Form","toggleprod")
    CB_PlayerIntros  = Config.getboolean("Form","playerintros")
    
    
    def getMyTeams():
        return list(map(str.strip, str(Config.get("SCT","myteams")).split(',')))
        
    def getMyPlayers(append=False):
        players = list(map(str.strip, str(Config.get("SCT","commonplayers")).split(',')))
        if(append):
            players.append("TBD")
        return players
        
    fuzzymatch = Config.getboolean("SCT","fuzzymatch")
    
    def loadMapList():
        maps = []
        dir = os.path.normpath(os.path.join(OBSmapDir,"src/maps"))
        for fname in os.listdir(dir):
            full_fname = os.path.join(dir, fname)
            name, ext = os.path.splitext(fname)
            if os.path.isfile(full_fname) and ext in ['.png', '.jpg']:
                maps.append(name.replace('_'," "))
                
        return maps
        
    maps = loadMapList()

except Exception as e:
    module_logger.exception("message") 
    raise
