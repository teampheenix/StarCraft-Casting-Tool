"""Provide settings for SCCTool."""
import logging
import os

from scctool.settings.config import cfgFile as configFile
from scctool.settings.version import VersionControl

module_logger = logging.getLogger('scctool.settings')

cfgFile = configFile
jsonFile = "src/data.json"
OBSdataDir = "OBS_data"
OBShtmlDir = "OBS_html"
OBSmapDir = "OBS_mapicons"

max_no_sets = 9

races = ("Random", "Terran", "Protoss", "Zerg")

versionControl = VersionControl()

# Creating directories if not exisiting
if not os.path.exists(OBSdataDir):
    os.makedirs(OBSdataDir)


def loadMapList():
    """Load map list form dir."""
    maps = []
    try:
        dir = os.path.normpath(os.path.join(OBSmapDir, "src/maps"))

        for fname in os.listdir(dir):
            full_fname = os.path.join(dir, fname)
            name, ext = os.path.splitext(fname)
            if os.path.isfile(full_fname) and ext in ['.png', '.jpg']:
                maps.append(name.replace('_', " "))
    finally:
        return maps


maps = loadMapList()


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
