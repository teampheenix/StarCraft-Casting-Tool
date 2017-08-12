#!/usr/bin/python
import logging

# create logger
module_logger = logging.getLogger('scctool.settings')

try:
    import configparser
    import os
except Exception as e:
    module_logger.exception("message") 
    raise  

try:
    version    = 'v0.8.3'
    configFile = "config.ini"
    jsonFile   = "src/data.json"
    OBSdataDir = "OBS_data"
    OBSmapDir  = "OBS_mapicons"
    OBSmapDirData  = "OBS_mapicons/data"
    
    races = ("Random","Protoss","Zerg","Terran")
    
    maps = ("Abyssal Reef","Acolyte","Ascension to Aiur","Bel'Shir Vestige",\
            "Blood Boil","Cactus Valley","Catallena","Defenders Landing",\
            "Honorgrounds", "Interloper","Mech Depot", "Newkirk Precinct",\
            "Odyssey","Paladino Terminal","Proxima Station",\
            "Sequencer","TBD")
    
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
    setDefaultConfig("Twitch","clientid","")
    setDefaultConfig("Twitch","oauth","")
    setDefaultConfig("Twitch","title_template","")
    
    setDefaultConfig("NightBot","token","")
    setDefaultConfig("NightBot","command","!matchlink")
    
    setDefaultConfig("SCT","myteam","MiXed Minds")
    setDefaultConfig("SCT","fuzzymatch","True")
    
    setDefaultConfig("Form","scoreupdate","False")
    setDefaultConfig("Form","togglescore","False")
    setDefaultConfig("Form","toggleprod", "False")

    setDefaultConfig("MapIcons","win_font_color","#f29b00")
    setDefaultConfig("MapIcons","default_border_color","#f29b00")
    setDefaultConfig("MapIcons","win_border_color","#008000")
    setDefaultConfig("MapIcons","lose_border_color","#f22200")
    setDefaultConfig("MapIcons","notplayed_border_color","#c0c0c0")
    setDefaultConfig("MapIcons","notplayed_opacity","0.4")
    

    def nightbotIsValid():
        return (len(Config.get("NightBot", "token"))>0 and len(Config.get("NightBot", "command"))>0)
    
    def twitchIsValid():
        twitchChannel = Config.get("Twitch", "Channel")
        clientID  = Config.get("Twitch", "clientID")
        oauth = Config.get("Twitch", "oauth")
    
        
        return (len(clientID)>0 and len(oauth)>0 and len(twitchChannel)>0)
    
        
    
    
    win_font_color         = Config.get("MapIcons", "win_font_color")
    default_border_color   = Config.get("MapIcons", "default_border_color")
    win_border_color       = Config.get("MapIcons", "win_border_color")
    lose_border_color      = Config.get("MapIcons", "lose_border_color")
    notplayed_border_color = Config.get("MapIcons", "notplayed_border_color")
    notplayed_opacity      = Config.get("MapIcons", "notplayed_opacity")
    
    CB_ScoreUpdate = Config.getboolean("Form","ScoreUpdate")
    CB_ToggleScore = Config.getboolean("Form","ToggleScore")
    CB_ToggleProd  = Config.getboolean("Form","ToggleProd")
    
    
    myteam =  Config.get("SCT","myteam")
    fuzzymatch = Config.get("SCT","fuzzymatch")

except Exception as e:
    module_logger.exception("message") 
    raise
