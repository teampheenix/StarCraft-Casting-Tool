#!/usr/bin/python
import configparser
import os
import logging

# create logger
module_logger = logging.getLogger('alphasc2tool.settings')

try:
    version    = 'v0.7.1'
    configFile = "config.ini"
    jsonFile   = "src/data.json"
    OBSdataDir = "OBS_data"
    OBSmapDir  = "OBS_mapicons"
    OBSmapDirData  = "OBS_mapicons/data"
    
    races = ("Random","Protoss","Zerg","Terran")
    
    #Creating directories if not exisiting 
    if not os.path.exists(OBSdataDir):
        os.makedirs(OBSdataDir)
        
    #Creating directories if not exisiting 
    if not os.path.exists(OBSmapDir):
        os.makedirs(OBSmapDir)
        
    #Creating directories if not exisiting 
    if not os.path.exists(OBSmapDirData):
        os.makedirs(OBSmapDirData)
    
    #Reading the configuration from file
    Config = configparser.ConfigParser()
    Config.read(configFile)
    
    twitchChannel = Config.get("Twitch", "Channel")
    clientID  = Config.get("Twitch", "clientID")
    oauth = Config.get("Twitch", "oauth")
    
    twitch_valid = (len(clientID)>0 and len(oauth)>0 and len(twitchChannel)>0)
    
    twitchTitleTemplate = Config.get("Twitch", "title_template")
    
    
    win_font_color         = Config.get("MapIcons", "win_font_color")
    default_border_color   = Config.get("MapIcons", "default_border_color")
    win_border_color       = Config.get("MapIcons", "win_border_color")
    lose_border_color      = Config.get("MapIcons", "lose_border_color")
    notplayed_border_color = Config.get("MapIcons", "notplayed_border_color")
    notplayed_opacity      = Config.get("MapIcons", "notplayed_opacity")
    
    CB_ScoreUpdate = Config.getboolean("Form","ScoreUpdate")
    CB_ToggleScore = Config.getboolean("Form","ToggleScore")
    CB_ToggleProd  = Config.getboolean("Form","ToggleProd")
    
    
    myteam =  Config.get("AlphaSC2","myteam")
    fuzzymatch = Config.get("AlphaSC2","fuzzymatch")

except Exception as e:
    module_logger.exception("message") 
