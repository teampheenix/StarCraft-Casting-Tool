"""Control version numbers."""
import urllib.request
import logging
from re import search as rsearch
from PyQt5.QtCore import QThread, pyqtSignal

# create logger
module_logger = logging.getLogger('scctool.settings.version')


class VersionControl(object):
    """Control version numbers."""

    def __init__(self):
        """Init Controller."""
        self.__version_file = "src/version"
        self.__url = "https://raw.githubusercontent.com/teampheenix/" +\
                     "StarCraft-Casting-Tool/master/src/version"
        self.current, self.major, self.minor, self.patch = self.__get_from_file(
            self.__version_file)
        self.latest, self.lmajor, self.lminor, self.lpatch  = self.current, self.major, self.minor, self.patch

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
            with urllib.request.urlopen(self.__url, timeout=5) as response:
                latest_version = response.read().decode("utf8").strip()

            major, minor, patch = self.__parse(latest_version)
            return latest_version,  major, minor, patch
        except Exception as e:
            module_logger.exception("message")
            return 'v0.0.0', 0, 0, 0

    def isNewAvaiable(self, check = True):
        """Check if a newer version is available."""
        if(check):
            self.latest, self.lmajor, self.lminor, self.lpatch = self.__latest()
        if(self.lmajor > self.major or
            (self.lmajor == self.major and (self.lminor > self.minor
                                       or (self.lminor == self.minor and self.lpatch > self.patch)))):
            return True
        return False


class CheckVersionThread(QThread):
    """Thread to check for new version."""

    newVersion = pyqtSignal(str)

    def __init__(self, versionc):
        """Init thread."""
        QThread.__init__(self)
        self.versionc = versionc

    def run(self):
        """Run thread."""
        if(self.versionc.isNewAvaiable()):
            self.newVersion.emit(self.versionc.latest)
