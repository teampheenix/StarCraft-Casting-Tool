"""Provide config for SCCTool."""
import logging
import configparser

import os.path

from scctool.settings import configFile, windows

module_logger = logging.getLogger('scctool.settings.config')  # create logger

parser = None


def init():
    """Init config."""
    global parser, scoreUpdate, toggleScore, toggleProd, playerIntros, fuzzymatch
    # Reading the configuration from file
    parser = configparser.ConfigParser()
    try:
        parser.read(configFile)
    except:
        parser.defaults()

    setDefaultConfigAll()

    scoreUpdate = parser.getboolean("Form", "scoreupdate")
    toggleScore = parser.getboolean("Form", "togglescore")
    toggleProd = parser.getboolean("Form", "toggleprod")
    playerIntros = parser.getboolean("Form", "playerintros")

    fuzzymatch = parser.getboolean("SCT", "fuzzymatch")

# Setting default values for config file


def setDefaultConfig(sec, opt, value, func=None):
    """Set default value in config."""
    if(not parser.has_section(sec)):
        parser.add_section(sec)

    if(not parser.has_option(sec, opt)):
        if(func):
            try:
                value = func()
            except:
                pass
        parser.set(sec, opt, value)
    elif(value in ["True", "False"]):
        try:
            parser.getboolean(sec, opt)
        except:
            if(func):
                try:
                    value = func()
                except:
                    pass
            parser.set(sec, opt, value)


def findTesserAct(default="C:\\Program Files (x86)\\Tesseract-OCR\\tesseract.exe"):
    """Search for Tesseract exceutable via registry."""
    if(not windows):
        return default
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                             "SOFTWARE\\WOW6432Node\\Tesseract-OCR")
        return winreg.QueryValueEx(key, "Path")[0] + '\\tesseract.exe'
    except:
        return default


def getTesserAct():
    """Get Tesseract exceutable via config or registry."""
    tesseract = parser.get("SCT", "tesseract")
    if(os.path.isfile(tesseract)):
        return tesseract
    else:
        new = findTesserAct(tesseract)
        if(new != tesseract):
            parser.set("SCT", "tesseract", new)
        return new



def setDefaultConfigAll():
    """Define default values and set them."""
    setDefaultConfig("Twitch", "channel", "")
    setDefaultConfig("Twitch", "oauth", "")
    setDefaultConfig("Twitch", "title_template",
                     "(League) – (Team1) vs (Team2)")

    setDefaultConfig("Nightbot", "token", "")
    setDefaultConfig("Nightbot", "command", "!matchlink")
    setDefaultConfig("Nightbot", "message", "(URL)")

    setDefaultConfig("FTP", "upload", "False")
    setDefaultConfig("FTP", "server", "")
    setDefaultConfig("FTP", "user", "")
    setDefaultConfig("FTP", "passwd", "")
    setDefaultConfig("FTP", "dir", "")

    setDefaultConfig("SCT", "myteams", "MiXed Minds, team pheeniX")
    setDefaultConfig("SCT", "commonplayers", "Shakyor, pressure, MarineKing, Moash," +
                     "Ostseedude, spaz, DERASTAT, FanTasY," +
                     "chrismaverik, holden, Desolation, RiseOfDeath," +
                     "TuneTrigger, MoFuJones, Fenix, Hyvaa, snoozle," +
                     "CptWobbles, dreign, Sly, Sonarwolf, Unknown, Xoneon")

    setDefaultConfig("SCT", "fuzzymatch", "True")
    setDefaultConfig("SCT", "new_version_prompt", "True")
    setDefaultConfig("SCT", "use_ocr", "False")

    tesseract = "C:\\Program Files (x86)\\Tesseract-OCR\\tesseract.exe"
    setDefaultConfig("SCT", "tesseract", tesseract, findTesserAct)

    setDefaultConfig("Form", "scoreupdate", "False")
    setDefaultConfig("Form", "togglescore", "False")
    setDefaultConfig("Form", "toggleprod", "False")
    setDefaultConfig("Form", "playerintros", "False")
    setDefaultConfig("Form", "autotwitch", "False")
    setDefaultConfig("Form", "autonightbot", "False")

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
    """Check if FTP data is valid."""
    return len(parser.get("FTP", "server")) > 0


def nightbotIsValid():
    """Check if nightbot data is valid."""
    return (len(parser.get("Nightbot", "token")) > 0
            and len(parser.get("Nightbot", "command")) > 0)


def twitchIsValid():
    """Check if twitch data is valid."""
    twitchChannel = parser.get("Twitch", "Channel")
    oauth = parser.get("Twitch", "oauth")
    return (len(oauth) > 0 and len(twitchChannel) > 0)


def getMyTeams():
    """Enpack my teams."""
    return list(map(str.strip, str(parser.get("SCT", "myteams")).split(',')))


def getMyPlayers(append=False):
    """Enpack my players."""
    players = list(
        map(str.strip, str(parser.get("SCT", "commonplayers")).split(',')))
    if(append):
        players.append("TBD")
    return players


init()
