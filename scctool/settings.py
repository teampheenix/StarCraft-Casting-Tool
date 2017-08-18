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
    
try:
    versioncontrol = VersionControl()
    configFile = "config.ini"
    jsonFile   = "src/data.json"
    OBSdataDir = "OBS_data"
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
    
    maps = ("Abyssal Reef","Acolyte","Ascension to Aiur","Bel'Shir Vestige",\
            "Blood Boil","Cactus Valley","Catallena","Defenders Landing",\
            "Honorgrounds", "Interloper","Mech Depot", "Newkirk Precinct",\
            "Odyssey","Paladino Terminal","Proxima Station",\
            "Sequencer","TBD")
    
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
    setDefaultConfig("Twitch","title_template","(TOUR) – (TEAM1) vs (TEAM2)")
    
    setDefaultConfig("NightBot","token","")
    setDefaultConfig("NightBot","command","!matchlink")
    
    setDefaultConfig("SCT","myteams","MiXed Minds, team pheeniX")
    setDefaultConfig("SCT","commonplayers","Shakyor, pressure, MarineKing, Moash, Ostseedude, spaz, DERASTAT, FanTasY,"+\
                           "chrismaverik, holden, Desolation, RiseOfDeath, TuneTrigger, MoFuJones, Fenix, Hyvaa, snoozle,"+\
                           " CptWobbles, dreign, Sly, Sonarwolf, Unknown, Xoneon")
    setDefaultConfig("SCT","fuzzymatch","True")
    
    setDefaultConfig("Form","scoreupdate","False")
    setDefaultConfig("Form","togglescore","False")
    setDefaultConfig("Form","toggleprod", "False")

    setDefaultConfig("MapIcons","default_border_color","#f29b00")
    setDefaultConfig("MapIcons","win_border_color","#008000")
    setDefaultConfig("MapIcons","lose_border_color","#f22200")
    setDefaultConfig("MapIcons","notplayed_border_color","#c0c0c0")
    setDefaultConfig("MapIcons","notplayed_opacity","0.4")
    
    setDefaultConfig("FTP","upload","False")
    setDefaultConfig("FTP","server","")
    setDefaultConfig("FTP","user","")
    setDefaultConfig("FTP","passwd","")


    def nightbotIsValid():
        return (len(Config.get("NightBot", "token"))>0 and len(Config.get("NightBot", "command"))>0)
    
    def twitchIsValid():
        twitchChannel = Config.get("Twitch", "Channel")
        oauth = Config.get("Twitch", "oauth")
    
        
        return (len(oauth)>0 and len(twitchChannel)>0)
    
        
    
    default_border_color   = Config.get("MapIcons", "default_border_color")
    win_border_color       = Config.get("MapIcons", "win_border_color")
    lose_border_color      = Config.get("MapIcons", "lose_border_color")
    notplayed_border_color = Config.get("MapIcons", "notplayed_border_color")
    notplayed_opacity      = Config.get("MapIcons", "notplayed_opacity")
    
    CB_ScoreUpdate = Config.getboolean("Form","ScoreUpdate")
    CB_ToggleScore = Config.getboolean("Form","ToggleScore")
    CB_ToggleProd  = Config.getboolean("Form","ToggleProd")
    
    
    myteams =  list(map(str.strip, str(Config.get("SCT","myteams")).split(',')))
    commonplayers = list(map(str.strip, str(Config.get("SCT","commonplayers")).split(',')))
    commonplayers.append("TBD")
    fuzzymatch = Config.get("SCT","fuzzymatch")

except Exception as e:
    module_logger.exception("message") 
    raise
