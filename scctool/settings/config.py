import logging
import configparser

from scctool.settings import cfgFile

# create logger
module_logger = logging.getLogger('scctool.settings.config')

parser = None

def init():
    global parser, scoreUpdate, toggleScore, toggleProd, playerIntros, fuzzymatch
    # Reading the configuration from file
    parser = configparser.ConfigParser()
    try:
        parser.read(cfgFile)
    except:
        parser.defaults()

    setDefaultConfigAll()

    scoreUpdate = parser.getboolean("Form", "scoreupdate")
    toggleScore = parser.getboolean("Form", "togglescore")
    toggleProd = parser.getboolean("Form", "toggleprod")
    playerIntros = parser.getboolean("Form", "playerintros")

    fuzzymatch = parser.getboolean("SCT", "fuzzymatch")

# Setting default values for config file
def setDefaultConfig(sec, opt, value):
    if(not parser.has_section(sec)):
        parser.add_section(sec)
    if(not parser.has_option(sec, opt)):
        parser.set(sec, opt, value)


def setDefaultConfigAll():
    setDefaultConfig("Twitch", "channel", "")
    setDefaultConfig("Twitch", "oauth", "")
    setDefaultConfig("Twitch", "title_template",
                     "(League) – (Team1) vs (Team2)")

    setDefaultConfig("NightBot", "token", "")
    setDefaultConfig("NightBot", "command", "!matchlink")
    setDefaultConfig("NightBot", "message", "(URL)")

    setDefaultConfig("FTP", "upload", "False")
    setDefaultConfig("FTP", "server", "")
    setDefaultConfig("FTP", "user", "")
    setDefaultConfig("FTP", "passwd", "")
    setDefaultConfig("FTP", "dir", "")

    setDefaultConfig("SCT", "myteams", "MiXed Minds, team pheeniX")
    setDefaultConfig("SCT", "commonplayers", "Shakyor, pressure, MarineKing, Moash, Ostseedude, spaz, DERASTAT, FanTasY," +
                     "chrismaverik, holden, Desolation, RiseOfDeath, TuneTrigger, MoFuJones, Fenix, Hyvaa, snoozle," +
                     " CptWobbles, dreign, Sly, Sonarwolf, Unknown, Xoneon")

    setDefaultConfig("SCT", "fuzzymatch", "True")

    setDefaultConfig("SCT", "use_ocr", "False")
    setDefaultConfig("SCT", "tesseract",
                     'C:\\Program Files (x86)\\Tesseract-OCR\\tesseract')

    setDefaultConfig("Form", "scoreupdate", "False")
    setDefaultConfig("Form", "togglescore", "False")
    setDefaultConfig("Form", "toggleprod", "False")
    setDefaultConfig("Form", "playerintros", "False")

    setDefaultConfig("MapIcons", "default_border_color", "#f29b00")
    setDefaultConfig("MapIcons", "undecided_color", "#f29b00")
    setDefaultConfig("MapIcons", "win_color", "#008000")
    setDefaultConfig("MapIcons", "lose_color", "#f22200")
    setDefaultConfig("MapIcons", "notplayed_color", "#c0c0c0")
    setDefaultConfig("MapIcons", "notplayed_opacity", "0.4")

    setDefaultConfig("Style", "mapicon_box", "Default")
    setDefaultConfig("Style", "mapicon_landscape", "Default")
    setDefaultConfig("Style", "score", "Default")
    setDefaultConfig("Style", "intro", "Default")

    setDefaultConfig("OBS", "port", "4444")
    setDefaultConfig("OBS", "active", "False")
    setDefaultConfig("OBS", "passwd", "")
    setDefaultConfig("OBS", "sources", "Intro1, Intro2")


def ftpIsValid():
    return len(parser.get("FTP", "server")) > 0


def nightbotIsValid():
    return (len(parser.get("NightBot", "token")) > 0 and len(parser.get("NightBot", "command")) > 0)


def twitchIsValid():
    twitchChannel = parser.get("Twitch", "Channel")
    oauth = parser.get("Twitch", "oauth")
    return (len(oauth) > 0 and len(twitchChannel) > 0)


def getMyTeams():
    return list(map(str.strip, str(parser.get("SCT", "myteams")).split(',')))

def getMyPlayers(append=False):
    players = list(
        map(str.strip, str(parser.get("SCT", "commonplayers")).split(',')))
    if(append):
        players.append("TBD")
    return players

init()
