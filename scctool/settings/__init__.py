"""Provide settings for SCCTool."""
import json
import logging
import os
import platform
import sys

module_logger = logging.getLogger('scctool.settings')


if getattr(sys, 'frozen', False):
    basedir = os.path.dirname(sys.executable)
else:
    basedir = os.path.dirname(sys.modules['__main__'].__file__)


def getAbsPath(file):
    """Link to absolute path of a file."""
    return os.path.normpath(os.path.join(basedir, file))


configFile = getAbsPath("config.ini")

OBSdataDir = "OBS_data"
OBShtmlDir = "OBS_html"
OBSmapDir = "OBS_mapicons"

dataDir = "data"
logosDir = os.path.join(dataDir, "logos")
matchdata_json_file = getAbsPath(dataDir + "/matchdata.json")
versiondata_json_file = getAbsPath(dataDir + "/versiondata.json")
nightbot_json_file = getAbsPath(dataDir + "/nightbot.json")
logos_json_file = getAbsPath(dataDir + "/logos.json")
history_json_file = getAbsPath(dataDir + "/history.json")
alias_json_file = getAbsPath(dataDir + "/alias.json")
mapstats_json_file = getAbsPath(dataDir + "/mapstats.json")

windows = (platform.system().lower() == "windows")

max_no_sets = 9

races = ("Random", "Terran", "Protoss", "Zerg")

# Creating directories if not exisiting
if not os.path.exists(getAbsPath(OBSdataDir)):
    os.makedirs(getAbsPath(OBSdataDir))
# Creating directories if not exisiting
if not os.path.exists(getAbsPath(dataDir)):
    os.makedirs(getAbsPath(dataDir))
# Creating directories if not exisiting
if not os.path.exists(getAbsPath(logosDir)):
    os.makedirs(getAbsPath(logosDir))


def loadMapList():
    """Load map list form dir."""
    maps = []
    try:
        dir = os.path.normpath(os.path.join(getAbsPath(OBSmapDir), "src/maps"))

        for fname in os.listdir(dir):
            full_fname = os.path.join(dir, fname)
            name, ext = os.path.splitext(fname)
            if os.path.isfile(full_fname) and ext in ['.jpg', '.png']:
                mapName = name.replace('_', " ")
                if mapName not in maps:
                    maps.append(mapName)
    finally:
        return maps


maps = []

nightbot_commands = []


def loadNightbotCommands():
    """Read json data from file."""
    global nightbot_commands
    try:
        with open(nightbot_json_file, 'r', encoding='utf-8-sig') as json_file:
            data = json.load(json_file)
    except Exception as e:
        data = dict()

    nightbot_commands = data
    return data


def saveNightbotCommands():
    """Write json data to file."""
    global nightbot_commands
    try:
        with open(nightbot_json_file, 'w', encoding='utf-8-sig') as outfile:
            json.dump(nightbot_commands, outfile)
    except Exception as e:
        module_logger.exception("message")


def race2idx(str):
    """Convert race to idx."""
    for idx, race in enumerate(races):
        if(race.lower() == str.lower()):
            return idx
    return 0


def idx2race(idx):
    """Convert idx to race."""
    try:
        return races[idx]
    except Exception:
        return races[0]


loadNightbotCommands()
