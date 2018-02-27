"""Provide settings for SCCTool."""
import logging
import os
import platform
import sys

module_logger = logging.getLogger('scctool.settings')

if getattr(sys, 'frozen', False):
    basedir = os.path.dirname(sys.executable)
else:
    basdir = os.path.dirname(sys.modules['__main__'].__file__)

def getAbsPath(file):
    """Link to absolute path of a file."""
    return os.path.normpath(os.path.join(basedir, file))


configFile = getAbsPath("config.ini")

OBSdataDir = "OBS_data"
OBShtmlDir = "OBS_html"
OBSmapDir = "OBS_mapicons"

dataDir = "data"
matchdata_json_file = getAbsPath(dataDir + "/matchdata.json")
versiondata_json_file = getAbsPath(dataDir + "/versiondata.json")

windows = (platform.system().lower() == "windows")

max_no_sets = 9

races = ("Random", "Terran", "Protoss", "Zerg")

# Creating directories if not exisiting
if not os.path.exists(getAbsPath(OBSdataDir)):
    os.makedirs(getAbsPath(OBSdataDir))
# Creating directories if not exisiting
if not os.path.exists(getAbsPath(dataDir)):
    os.makedirs(getAbsPath(dataDir))


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
    except:
        return races[0]
