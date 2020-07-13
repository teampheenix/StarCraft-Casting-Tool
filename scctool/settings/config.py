"""Provide config for SCCTool."""
import configparser
import logging
import os.path
import platform
import sys

module_logger = logging.getLogger(__name__)  # create logger

this = sys.modules[__name__]

this.parser = None


def init(file):
    """Init config."""
    # Reading the configuration from file
    module_logger.info(file)
    this.parser = configparser.ConfigParser()
    try:
        this.parser.read(file, encoding='utf-8-sig')
    except Exception:
        this.parser.defaults()

    setDefaultConfigAll()
    renameConfigOptions()


def representsInt(s):
    """Test if the value can be casted to an integer."""
    try:
        int(s)
        return True
    except ValueError:
        return False


def representsFloat(s):
    """Test if the value can be casted to a float."""
    try:
        float(s)
        return True
    except ValueError:
        return False


# Setting default values for config file
def setDefaultConfig(sec, opt, value):
    """Set default value in config."""
    if not this.parser.has_section(sec):
        this.parser.add_section(sec)

    if callable(value):
        value = value()
    try:
        if not this.parser.has_option(sec, opt):
            pass
        elif value in ["True", "False"]:
            this.parser.getboolean(sec, opt)
            return
        elif representsInt(value):
            this.parser.getint(sec, opt)
            return
        elif representsFloat(value):
            this.parser.getfloat(sec, opt)
            return
        else:
            return
    except ValueError:
        pass

    this.parser.set(sec, opt, value)


def findTesserAct(
        default="C:\\Program Files (x86)\\Tesseract-OCR\\tesseract.exe"):
    """Search for Tesseract exceutable via registry."""
    try:
        if (platform.system().lower() != "windows"):
            return default
        else:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                 "SOFTWARE\\WOW6432Node\\Tesseract-OCR")
            return os.path.normpath(
                winreg.QueryValueEx(key, "Path")[0] + '\\tesseract.exe')
    except Exception:
        return default


def getTesserAct():
    """Get Tesseract exceutable via config or registry."""
    tesseract = this.parser.get("SCT", "tesseract")
    if (os.path.isfile(tesseract)):
        return os.path.normpath(tesseract)
    else:
        new = findTesserAct(tesseract)
        if (new != tesseract):
            this.parser.set("SCT", "tesseract", new)
        return os.path.normpath(new)


def setDefaultConfigAll():
    """Define default values and set them."""
    setDefaultConfig("Twitch", "channel", "")
    setDefaultConfig("Twitch", "oauth", "")
    setDefaultConfig("Twitch", "title_template",
                     "(League) – (Team1) vs (Team2)")
    setDefaultConfig("Twitch", "set_game", "True")

    setDefaultConfig("Nightbot", "token", "")

    setDefaultConfig("SCT", "myteams", "MiXed Minds, team pheeniX")
    setDefaultConfig("SCT", "commonplayers", "pressure")
    setDefaultConfig("SCT", "swap_myteam", "False")

    setDefaultConfig("SCT", "fuzzymatch", "True")
    setDefaultConfig("SCT", "new_version_prompt", "True")
    setDefaultConfig("SCT", "new_maps_prompt", "True")
    setDefaultConfig("SCT", "use_ocr", "False")
    setDefaultConfig("SCT", "sc2_network_listener_enabled", "False")
    setDefaultConfig("SCT", "sc2_network_listener_address", "127.0.0.1:6119")
    setDefaultConfig("SCT", "CtrlShiftS", "False")
    setDefaultConfig("SCT", "CtrlShiftC", "False")
    setDefaultConfig("SCT", "CtrlShiftR", "0")
    setDefaultConfig("SCT", "CtrlN", "False")
    setDefaultConfig("SCT", "CtrlX", "False")
    setDefaultConfig("SCT", "language", "en_US")
    setDefaultConfig("SCT", "transparent_match_banner", "False")

    setDefaultConfig("SCT", "blacklist_on", "False")
    setDefaultConfig("SCT", "blacklist", "")

    setDefaultConfig("SCT", "tesseract", findTesserAct)

    setDefaultConfig("Form", "scoreupdate", "False")
    setDefaultConfig("Form", "togglescore", "False")
    setDefaultConfig("Form", "toggleprod", "False")
    setDefaultConfig("Form", "autotwitch", "False")
    setDefaultConfig("Form", "autonightbot", "False")

    setDefaultConfig("MapIcons", "default_border_color", "#f29b00")
    setDefaultConfig("MapIcons", "win_color", "#008000")
    setDefaultConfig("MapIcons", "lose_color", "#f22200")
    setDefaultConfig("MapIcons", "winner_highlight_color", "#f29b00")
    setDefaultConfig("MapIcons", "undecided_color", "#aaaaaa")
    setDefaultConfig("MapIcons", "notplayed_color", "#aaaaaa")
    setDefaultConfig("MapIcons", "notplayed_opacity", "0.4")
    setDefaultConfig("MapIcons", "padding_landscape", "2.0")
    setDefaultConfig("MapIcons", "padding_box", "2.0")
    setDefaultConfig("MapIcons", "scope_box_1", "all")
    setDefaultConfig("MapIcons", "scope_box_2", "not-ace")
    setDefaultConfig("MapIcons", "scope_box_3", "ace")
    setDefaultConfig("MapIcons", "scope_landscape_1", "all")
    setDefaultConfig("MapIcons", "scope_landscape_2", "not-ace")
    setDefaultConfig("MapIcons", "scope_landscape_3", "ace")
    setDefaultConfig("MapIcons", "separate_style_box_1", "False")
    setDefaultConfig("MapIcons", "separate_style_box_2", "False")
    setDefaultConfig("MapIcons", "separate_style_box_3", "False")
    setDefaultConfig("MapIcons", "separate_style_landscape_1", "False")
    setDefaultConfig("MapIcons", "separate_style_landscape_2", "False")
    setDefaultConfig("MapIcons", "separate_style_landscape_3", "False")

    setDefaultConfig("Style", "mapicons_box", "Default")
    setDefaultConfig("Style", "mapicons_box_1", "Default")
    setDefaultConfig("Style", "mapicons_box_2", "Default")
    setDefaultConfig("Style", "mapicons_box_3", "Default")
    setDefaultConfig("Style", "mapicons_landscape", "Default")
    setDefaultConfig("Style", "mapicons_landscape_1", "Default")
    setDefaultConfig("Style", "mapicons_landscape_2", "Default")
    setDefaultConfig("Style", "mapicons_landscape_3", "Default")
    setDefaultConfig("Style", "score", "Default")
    setDefaultConfig("Style", "intro", "Default")
    setDefaultConfig("Style", "mapstats", "Default")
    setDefaultConfig("Style", "aligulac", "Default")
    setDefaultConfig("Style", "use_custom_font", "False")
    setDefaultConfig("Style", "custom_font", "Verdana")
    setDefaultConfig("Style", "countdown", "Minimal")
    setDefaultConfig("Style", "vetoes", "Default")

    setDefaultConfig("Intros", "hotkey_player1", "")
    setDefaultConfig("Intros", "hotkey_player2", "")
    setDefaultConfig("Intros", "hotkey_debug", "")
    setDefaultConfig("Intros", "sound_volume", "5")
    setDefaultConfig("Intros", "display_time", "3.0")
    setDefaultConfig("Intros", "animation", "Fly-In")
    setDefaultConfig("Intros", "tts_active", "False")
    setDefaultConfig("Intros", "tts_voice", "en-US-Standard-B")
    setDefaultConfig("Intros", 'tts_scope', "team_player")
    setDefaultConfig("Intros", "tts_volume", "5")
    setDefaultConfig("Intros", "tts_pitch", "0.0")
    setDefaultConfig("Intros", "tts_rate", "1.0")

    setDefaultConfig("Mapstats", "color1", "#6495ed")
    setDefaultConfig("Mapstats", "color2", "#000000")
    setDefaultConfig("Mapstats", "autoset_next_map", "True")
    setDefaultConfig("Mapstats", "mark_played", "False")
    setDefaultConfig("Mapstats", "mark_vetoed", "False")
    setDefaultConfig("Mapstats", "sort_maps", "True")

    setDefaultConfig("Countdown", 'restart', 'True')
    setDefaultConfig("Countdown", 'description', 'Stream will be back in')
    setDefaultConfig("Countdown", 'replacement', 'soon™')
    setDefaultConfig("Countdown", 'duration', '00:05:00')
    setDefaultConfig("Countdown", 'datetime', '2018-11-18 20:00')
    setDefaultConfig("Countdown", 'static', 'False')
    setDefaultConfig("Countdown", 'matchgrabber_update', 'False')
    setDefaultConfig("Countdown", 'pre_txt', 'Countdown is running...')
    setDefaultConfig("Countdown", 'post_txt', 'Countdown is over!')

    setDefaultConfig("Vetoes", "padding", "2.0")


def renameConfigOptions():
    """Delete and rename old config options."""
    from scctool.settings import nightbot_commands

    try:
        value = this.parser.get("Style", "mapicon_landscape")
        this.parser.set("Style", "mapicons_landscape", str(value))
        this.parser.remove_option("Style", "mapicon_landscape")
    except Exception:
        pass

    try:
        value = this.parser.get("Style", "mapicon_box")
        this.parser.set("Style", "mapicons_box", str(value))
        this.parser.remove_option("Style", "mapicon_box")
    except Exception:
        pass

    try:
        value = this.parser.getboolean("SCT", "StrgShiftS")
        this.parser.set("SCT", "CtrlShiftS", str(value))
        this.parser.remove_option("SCT", "StrgShiftS")
    except Exception:
        pass

    this.parser.remove_section("OBS")
    this.parser.remove_section("FTP")

    try:
        command = this.parser.get("Nightbot", "command")
        message = this.parser.get("Nightbot", "message")
        nightbot_commands[command] = message
    except Exception:
        pass

    try:
        this.parser.remove_option("Nightbot", "command")
        this.parser.remove_option("Nightbot", "message")
    except Exception:
        pass

    try:
        this.parser.remove_option('Form', 'playerintros')
    except Exception:
        pass


def nightbotIsValid():
    """Check if nightbot data is valid."""
    from scctool.settings import nightbot_commands
    return (len(this.parser.get("Nightbot", "token")) > 0
            and len(nightbot_commands) > 0)


def twitchIsValid():
    """Check if twitch data is valid."""
    twitchChannel = this.parser.get("Twitch", "Channel")
    oauth = this.parser.get("Twitch", "oauth")
    return (len(oauth) > 0 and len(twitchChannel) > 0)


def getMyTeams():
    """Enpack my teams."""
    return list(
        map(str.strip,
            str(this.parser.get("SCT", "myteams")).split(',')))


def getBlacklist():
    """Enpack my teams."""
    return list(
        map(str.strip,
            str(this.parser.get("SCT", "blacklist")).split(',')))


def getMyPlayers(append=False):
    """Enpack my players."""
    players = list(
        map(str.strip,
            str(this.parser.get("SCT", "commonplayers")).split(',')))
    if (append):
        players.append("TBD")
    return players


def loadHotkey(string):
    """Unpack hotkey from config."""
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
    """Pack hotkey to config."""
    try:
        return "{name}, {scan_code}, {is_keypad}".format(**data)
    except Exception:
        return ""
