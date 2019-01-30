"""Provide settings for SCCTool."""
import json
import logging
import os
import platform
import sys
import time

import appdirs

from scctool.settings.client_config import ClientConfig
from scctool.settings.config import init as initConfig
from scctool.settings.profileManager import ProfileManager
from scctool.settings.safeGuard import SafeGuard

module_logger = logging.getLogger(__name__)
this = sys.modules[__name__]

if getattr(sys, 'frozen', False):
    basedir = os.path.dirname(sys.executable)
else:
    basedir = os.path.dirname(sys.modules['__main__'].__file__)

casting_data_dir = "casting_data"
casting_html_dir = "casting_html"

dataDir = "data"
logosDir = os.path.join(dataDir, "logos")
ttsDir = os.path.join(dataDir, "tts")

windows = (platform.system().lower() == "windows")
max_no_sets = 19
max_no_vetos = 9
races = ("Random", "Terran", "Protoss", "Zerg")

this.profileManager = ProfileManager()
this.maps = []
this.nightbot_commands = dict()
this.safe = SafeGuard()


def loadSettings():
    """Load all settings."""
    this.profileManager = ProfileManager()

    initConfig(configFile())

    loadNightbotCommands()

    # Creating directories if not exisiting
    if not os.path.exists(getAbsPath(casting_data_dir)):
        os.makedirs(getAbsPath(casting_data_dir))
    # Creating directories if not exisiting
    if not os.path.exists(getAbsPath(logosDir)):
        os.makedirs(getAbsPath(logosDir))
    # Creating directories if not exisiting
    if not os.path.exists(getAbsPath(ttsDir)):
        os.makedirs(getAbsPath(ttsDir))

    # Create a symnolic link to the profiles directory
    # Not working on Windows 10 - admin rights needed
    # link = os.path.normpath(os.path.join(basedir, 'profiles'))
    # profiles = this.profileManager.profilesdir()
    # if not os.path.exists(link):
    #     module_logger.info('Creating symbolic link.')
    #     os.symlink(link, profiles)
    # elif os.path.islink(link) and os.readlink(link) != profiles:
    #     module_logger.info('Updating symbolic link.')
    #     os.unlink(link)
    #     os.symlink(link, profiles)
    # elif not os.path.islink(link):
    #     module_logger.info('Deleting file and creating symbolic link.')
    #     os.remove(link)
    #     os.symlink(link, profiles)

    loadMapList()


def getResFile(file):
    """Get the norm path of a resource file."""
    if hasattr(sys, '_MEIPASS'):
        return os.path.normpath(os.path.join(sys._MEIPASS, 'src', file))
    else:
        return os.path.normpath(os.path.join(basedir, 'src', file))


def getLocalesDir():
    """Get the locales dir."""
    if hasattr(sys, '_MEIPASS'):
        return os.path.normpath(os.path.join(sys._MEIPASS, 'locales'))
    else:
        return os.path.normpath(os.path.join(basedir, 'locales'))


def getJsonFile(scope):
    """Get the absolute path of a json file."""
    return getAbsPath(f"{dataDir}/{scope}.json")


def configFile():
    """Get the absolute path of the config file."""
    return getAbsPath("config.ini")


def getLogFile():
    """Get the absolute path to the logfile."""
    logdir = getLogDir()
    if not os.path.exists(logdir):
        os.makedirs(logdir)
    else:
        # Delete old logfiles
        for f in os.listdir(logdir):
            full = os.path.join(logdir, f)
            if (os.path.isfile(full)
                    and os.stat(full).st_mtime < time.time() - 7 * 86400):
                os.remove(full)

    filename = 'scct-{}-{}.log'.format(time.strftime(
        "%Y%m%d-%H%M%S"), this.profileManager._current)
    return os.path.normpath(os.path.join(logdir, filename))


def getLogDir():
    """Get the absolut path to the log dir."""
    return appdirs.user_log_dir(
        ClientConfig.APP_NAME, ClientConfig.COMPANY_NAME)


def getAbsPath(file):
    """Link to absolute path of a file."""
    return this.profileManager.getFile(file)


def loadMapList():
    """Load map list form dir."""
    data = []
    try:
        dir = os.path.normpath(os.path.join(
            getAbsPath(casting_html_dir), "src/img/maps"))

        for fname in os.listdir(dir):
            full_fname = os.path.join(dir, fname)
            name, ext = os.path.splitext(fname)
            if os.path.isfile(full_fname) and ext in ['.jpg', '.png']:
                mapName = name.replace('_', " ")
                if mapName not in data:
                    data.append(mapName)
    finally:
        this.maps = data
        return data


def loadNightbotCommands():
    """Read json data from file."""
    try:
        with open(getJsonFile('nightbot'), 'r',
                  encoding='utf-8-sig') as json_file:
            data = json.load(json_file)
    except Exception:
        data = dict()

    this.nightbot_commands = data
    return data


def saveNightbotCommands():
    """Write json data to file."""
    try:
        with open(getJsonFile('nightbot'), 'w',
                  encoding='utf-8-sig') as outfile:
            json.dump(this.nightbot_commands, outfile)
    except Exception:
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
