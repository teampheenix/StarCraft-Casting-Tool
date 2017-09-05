import urllib.request
import logging
from re import search as rsearch
from threading import Thread
from PyQt5.QtCore import QThread, pyqtSignal

# create logger
module_logger = logging.getLogger('scctool.settings.version')


class VersionControl(object):
    def __init__(self):
        self.__version_file = "src/version"
        self.__url = "https://raw.githubusercontent.com/teampheenix/StarCraft-Casting-Tool/master/src/version"
        self.current, self.major, self.minor, self.patch = self.__get_from_file(
            self.__version_file)
        self.latest = self.current

    def __parse(self, string):
        string = str(string)
        string = string.strip()
        m = rsearch("^v([0-9]+)\.([0-9]+)\.([0-9]+)$", string)
        major = int(m.group(1))
        minor = int(m.group(2))
        patch = int(m.group(3))

        return major, minor, patch

    def __get_from_file(self, version_file):
        try:
            with open(self.__version_file, 'r') as infile:
                version = infile.readline().strip()
            major, minor, patch = self.__parse(version)
        except Exception as e:
            module_logger.exception("message")
            version, major, minor, patch = 'v0.0.0', 0, 0, 0

        return version, major, minor, patch

    def __latest(self):
        try:
            with urllib.request.urlopen(self.__url, timeout = 5) as response:
                latest_version = response.read().decode("utf8").strip()

            major, minor, patch = self.__parse(latest_version)
            return latest_version,  major, minor, patch
        except Exception as e:
            module_logger.exception("message")
            return 'v0.0.0', 0, 0, 0

    def isNewAvaiable(self):
        self.latest, lmajor, lminor, lpatch = self.__latest()
        if(lmajor > self.major or
            (lmajor == self.major and (lminor > self.minor
                                       or (lminor == self.minor and lpatch > self.patch)))):
            return True
        return False

class CheckVersionThread(QThread):

    newVersion = pyqtSignal(str)

    def __init__(self, versionc):
        QThread.__init__(self)
        self.versionc = versionc

    def run(self):
        if(self.versionc.isNewAvaiable()):
            self.newVersion.emit(self.versionc.latest)
