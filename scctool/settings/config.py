"""Provide config for SCCTool."""
import logging
import configparser

import os.path

from scctool.settings import configFile, windows

module_logger = logging.getLogger('scctool.settings.config')  # create logger

parser = None


def init():
    """Init config."""
    global parser, scoreUpdate
    # Reading the configuration from file
    parser = configparser.ConfigParser()
    try:
        parser.read(configFile, encoding='utf-8-sig')
    except Exception:
        parser.defaults()

    setDefaultConfigAll()
    renameConfigOptions()


def representsInt(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


def representsFloat(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


# Setting default values for config file
def setDefaultConfig(sec, opt, value, func=None):
    """Set default value in config."""
    if(not parser.has_section(sec)):
        parser.add_section(sec)

    if(not parser.has_option(sec, opt)):
        if(func):
            try:
                value = func()
            except Exception:
                pass
        parser.set(sec, opt, value)
    elif(value in ["True", "False"]):
        try:
            parser.getboolean(sec, opt)
        except Exception:
            if(func):
                try:
                    value = func()
                except Exception:
                    pass
            parser.set(sec, opt, value)
    elif(representsInt(value)):
        try:
            parser.getint(sec, opt)
        except Exception:
            if(func):
                try:
                    value = func()
                except Exception:
                    pass
            parser.set(sec, opt, value)
    elif(representsFloat(value)):
        try:
            parser.getfloat(sec, opt)
        except Exception:
            if(func):
                try:
                    value = func()
                except Exception:
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
    except Exception:
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

    setDefaultConfig("SCT", "myteams", "MiXed Minds, team pheeniX")
    setDefaultConfig("SCT", "commonplayers", "pressure")

    setDefaultConfig("SCT", "fuzzymatch", "True")
    setDefaultConfig("SCT", "new_version_prompt", "True")
    setDefaultConfig("SCT", "use_ocr", "False")
    setDefaultConfig("SCT", "CtrlShiftS", "False")
    setDefaultConfig("SCT", "CtrlShiftC", "False")
    setDefaultConfig("SCT", "CtrlShiftR", "0")
    setDefaultConfig("SCT", "CtrlN", "False")
    setDefaultConfig("SCT", "CtrlX", "False")
    setDefaultConfig("SCT", "language", "en_US")
    setDefaultConfig("SCT", "transparent_match_banner", "False")

    tesseract = "C:\\Program Files (x86)\\Tesseract-OCR\\tesseract.exe"
    setDefaultConfig("SCT", "tesseract", tesseract, findTesserAct)

    setDefaultConfig("Form", "scoreupdate", "False")
    setDefaultConfig("Form", "togglescore", "False")
    setDefaultConfig("Form", "toggleprod", "False")
    setDefaultConfig("Form", "playerintros", "False")
    setDefaultConfig("Form", "autotwitch", "False")
    setDefaultConfig("Form", "autonightbot", "False")

    setDefaultConfig("MapIcons", "default_border_color", "#f29b00")
    setDefaultConfig("MapIcons", "win_color", "#008000")
    setDefaultConfig("MapIcons", "lose_color", "#f22200")
    setDefaultConfig("MapIcons", "winner_highlight_color", "#f29b00")
    setDefaultConfig("MapIcons", "undecided_color", "#aaaaaa")
    setDefaultConfig("MapIcons", "notplayed_color", "#aaaaaa")
    setDefaultConfig("MapIcons", "notplayed_opacity", "0.4")

    setDefaultConfig("Style", "mapicon_box", "Default")
    setDefaultConfig("Style", "mapicon_landscape", "Default")
    setDefaultConfig("Style", "score", "Default")
    setDefaultConfig("Style", "intro", "Default")
    setDefaultConfig("Style", "use_custom_font", "False")
    setDefaultConfig("Style", "custom_font", "Verdana")

    setDefaultConfig("Intros", "hotkey_player1", "")
    setDefaultConfig("Intros", "hotkey_player2", "")
    setDefaultConfig("Intros", "hotkey_debug", "")
    setDefaultConfig("Intros", "sound_volume", "5")
    setDefaultConfig("Intros", "display_time", "3.0")
    setDefaultConfig("Intros", "animation", "Fly-In")


def renameConfigOptions():
    """Delete and rename old config options."""
    from scctool.settings import nightbot_commands
    try:
        value = parser.getboolean("SCT", "StrgShiftS")
        parser.set("SCT", "CtrlShiftS", str(value))
        parser.remove_option("SCT", "StrgShiftS")
    except Exception:
        pass

    parser.remove_section("OBS")
    parser.remove_section("FTP")

    try:
        command = parser.get("Nightbot", "command")
        message = parser.get("Nightbot", "message")
        nightbot_commands[command] = message
    except Exception:
        pass

    try:
        parser.remove_option("Nightbot", "command")
        parser.remove_option("Nightbot", "message")
    except Exception:
        pass


def nightbotIsValid():
    """Check if nightbot data is valid."""
    from scctool.settings import nightbot_commands
    return (len(parser.get("Nightbot", "token")) > 0 and len(nightbot_commands) > 0)


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


def loadHotkey(string):
    try:
        name, scan_code, is_keypad = str(string).split(',')
        data = dict()
        data['name'] = name.strip().upper()
        data['scan_code'] = int(scan_code.strip())
        data['is_keypad'] = is_keypad.strip().lower() == "true"
        return data
    except Exception:
        return {'name': '', 'scan_code': 0, 'is_keypad': False}


def dumpHotkey(data):
    try:
        return "{name}, {scan_code}, {is_keypad}".format(**data)
    except Exception:
        return ""


init()
