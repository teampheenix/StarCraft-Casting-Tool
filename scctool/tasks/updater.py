"""Get info about latest version and download it in the background."""
import json
import logging
import os
import sys
import tarfile
import zipfile

from PyQt5.QtCore import pyqtSignal

import scctool
import scctool.settings.translation
from pyupdater.client import Client
from scctool.settings.client_config import ClientConfig
from scctool.tasks.tasksthread import TasksThread

module_logger = logging.getLogger(__name__)
_ = scctool.settings.translation.gettext
this = sys.modules[__name__]
this.data = dict()


def compareVersions(v1, v2, maximum=5):
    """Compare two versions."""
    v1 = v1.replace('beta', '.')
    v2 = v2.replace('beta', '.')
    v1 = v1.split(".")
    v2 = v2.split(".")
    max_idx = min(max(len(v1), len(v2)), maximum)
    for idx in range(max_idx):
        try:
            n1 = int(v1[idx])
        except Exception:
            n1 = 0
        try:
            n2 = int(v2[idx])
        except Exception:
            n2 = 0
        if n1 > n2:
            return -1
        elif n2 > n1:
            return 1
    return 0


def getChannel(version=None):
    """Get update channel (beta or stable)."""
    if version is None:
        version = scctool.__version__
    return 'beta' if 'beta' in version else 'stable'


def needInitialUpdate(version):
    """Check if data update is needed."""
    if version == '0.0.0':
        return True
    elif not os.path.exists(
            scctool.settings.getAbsPath(scctool.settings.casting_html_dir)):
        return True
    elif getLastVersion() != scctool.__version__:
        setLastVersion(scctool.__version__)
        return True
    else:
        return False


def readJsonFile(force=False):
    """Read versiondata.json file."""
    if not force and len(this.data) > 0:
        return
    try:
        with open(scctool.settings.getJsonFile('versiondata'), 'r',
                  encoding='utf-8-sig') as f:
            this.data = json.load(f)
    except Exception:
        this.data = dict()


def dumpJsonFile():
    """Save to versiondata.json file."""
    readJsonFile()
    with open(scctool.settings.getJsonFile('versiondata'), 'w',
              encoding='utf-8-sig') as o:
        json.dump(this.data, o)


def getDataVersion():
    """Read data version from json file."""
    readJsonFile()
    return this.data.get('data_version', '0.0.0')


def setDataVersion(version):
    """Write data version to json file."""
    readJsonFile()
    this.data['data_version'] = version
    dumpJsonFile()


def getLastVersion():
    """Read data version from json file."""
    readJsonFile()
    return this.data.get('last_version', '0.0.0')


def setLastVersion(version):
    """Write data version to json file."""
    readJsonFile()
    this.data['last_version'] = version
    dumpJsonFile()


def getRestartFlag():
    """Get the current restart flag."""
    readJsonFile()
    return this.data.get('restart_flag', False)


def setRestartFlag(flag=True):
    """Set a restart flag."""
    readJsonFile()
    this.data['restart_flag'] = bool(flag)
    dumpJsonFile()


def extractData(asset_update, handler=lambda x: None):
    """Extract data."""
    handler(10)
    if asset_update.is_downloaded():
        file = os.path.join(asset_update.update_folder,
                            asset_update.filename)
        targetdir = scctool.settings.profileManager.profiledir()
        with zipfile.ZipFile(file, "r") as myzip:
            myzip.extractall(targetdir)
        handler(50)
        file = os.path.join(targetdir,
                            'SCCT-data')
        with tarfile.open(file, "r:gz") as tar:
            tar.extractall(targetdir)
        handler(90)
        os.remove(file)
        handler(95)
        setDataVersion(asset_update.latest)
        handler(100)


class VersionHandler(TasksThread):
    """Check for new version and update or notify."""

    newVersion = pyqtSignal(str)
    newData = pyqtSignal(str)
    noNewVersion = pyqtSignal()
    progress = pyqtSignal(dict)
    updated_data = pyqtSignal(str)

    # Constants
    APP_NAME = ClientConfig.APP_NAME
    APP_VERSION = scctool.__version__

    ASSET_NAME = 'SCCT-data'
    ASSET_VERSION = '0.0.0'

    client = Client(ClientConfig())

    app_update = None
    asset_update = None

    def __init__(self, controller):
        """Init the thread."""
        super().__init__()

        self.__controller = controller
        self.setTimeout(10)

        self.addTask('version_check', self.__version_check)
        self.addTask('update_data', self.__update_data)
        self.addTask('update_app', self.__update_app)

        self.updated_data.connect(controller.displayWarning)
        # self.disableCB.connect(controller.uncheckCB)

    def isCompatible(self):
        """Check if data update is needed."""
        return compareVersions(self.asset_update.latest,
                               self.APP_VERSION, 3) < 1

    def update_progress(self, data):
        """Process progress updates."""
        self.progress.emit(data)

    def __version_check(self):
        try:
            self.client.add_progress_hook(self.update_progress)
            self.client.refresh()
            self.ASSET_VERSION = getDataVersion()
            channel = getChannel(self.APP_VERSION)
            self.app_update = self.client.update_check(self.APP_NAME,
                                                       self.APP_VERSION,
                                                       channel=channel)
            if self.asset_update is not None:
                self.newData.emit(self.asset_update.latest)
                module_logger.info("Asset: " + self.asset_update.latest)
                if self.isCompatible():
                    self.activateTask("update_data")

            if self.app_update is not None:
                scctool.__latest_version__ = self.app_update.latest
                scctool.__new_version__ = True
                self.newVersion.emit(self.app_update.latest)
                module_logger.info("App: " + self.app_update.latest)
            else:
                self.noNewVersion.emit()
        except Exception:
            module_logger.exception("message")
        finally:
            self.deactivateTask('version_check')

    def __update_data(self):
        try:
            module_logger.info("Start to update data files!")
            if self.asset_update is None:
                self.deactivateTask('update_data')
                return
            self.asset_update.download()
            extractData(self.asset_update)
            module_logger.info("Updated data files!")
            self.updated_data.emit(_("Updated data files!"))
        except Exception:
            module_logger.exception("message")
        finally:
            self.deactivateTask('update_data')

    def __update_app(self):
        try:
            if self.app_update is None:
                self.deactivateTask('update_app')
                return
            if hasattr(sys, "frozen"):
                module_logger.info("Start to update app!")
                self.app_update.download(False)
                if self.app_update.is_downloaded():
                    module_logger.info("Download sucessfull.")
                    self.__controller.cleanUp()
                    setRestartFlag()
                    module_logger.info("Restarting...")
                    self.app_update.extract_restart()
        except Exception:
            module_logger.exception("message")
        finally:
            self.deactivateTask('update_app')
