"""Provide logo manager for SCCTool."""
import logging
import os
import shutil
import json
import filecmp
import itertools
import humanize
from urllib.request import urlretrieve
from time import time
from scctool.settings import logosDir, logos_json_file, getAbsPath, OBShtmlDir, OBSdataDir
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

module_logger = logging.getLogger(
    'scctool.settings.logoManager')  # create logger


class LogoManager:

    _identifiers = set()
    _last_used = []
    _favorites = []
    _ident2map = dict()
    _last_used_max_len = 10

    def __init__(self, controller):
        self.__controller = controller
        self._team1 = Logo(self)
        self._team2 = Logo(self)
        try:
            self.loadJson()
            self.fromOldFormat()
            self.removeDuplicates()
        except Exception as e:
            module_logger.exception("message")
        
    def newLogo(self):
        return Logo(self)
        
    def fromOldFormat(self):
        if not self._team1.isLogo():
            file = getAbsPath(self.__controller.linkFile(OBSdataDir + "/" + "logo1"))
            if os.path.isfile(file):
                logo = Logo(self)
                logo.fromFile(file)
                self.setTeam1Logo(logo)
                os.remove(file)
        
        if not self._team2.isLogo():
            file = getAbsPath(self.__controller.linkFile(OBSdataDir + "/" + "logo2"))
            if os.path.isfile(file):
                logo = Logo(self)
                logo.fromFile(file)
                self.setTeam2Logo(logo)
                os.remove(file)

    def dumpJson(self):
        data = dict()
        data['last_used'] = []
        data['favorites'] = []
        data['team1'] = None
        data['team2'] = None

        for item in self._last_used:
            data['last_used'].append(item.toDict())
        for item in self._favorites:
            data['favorites'].append(item.toDict())

        data['team1'] = self._team1.toDict()
        data['team2'] = self._team2.toDict()

        try:
            with open(logos_json_file, 'w') as outfile:
                json.dump(data, outfile)
        except Exception as e:
            module_logger.exception("message")

    def loadJson(self):
        self._identifiers = set()
        self._last_used = []
        self._favorites = []
        data = dict()

        try:
            with open(logos_json_file) as json_file:
                data = json.load(json_file)
        finally:
            for item in data['last_used']:
                logo = Logo(self)
                logo.fromDict(item)
                self.addLastUsed(logo)
            for item in data['favorites']:
                logo = Logo(self)
                logo.fromDict(item)
                if logo.isFile():
                    self._favorites.append(logo)

            item = data.get('team1', None)
            logo = Logo(self)
            logo.fromDict(item)
            if logo.isFile():
                self.setTeam1Logo(logo)

            item = data.get('team2', None)
            logo = Logo(self)
            logo.fromDict(item)
            if logo.isFile():
                self.setTeam2Logo(logo)

    def trimLastUsed(self):
        while len(self._last_used) > self._last_used_max_len:
            logo = self._last_used.pop(0)
            logo.delete()

    def addLastUsed(self, logo):
        if logo.isFile():
            for lu_logo in self._last_used:
                if lu_logo.equals(logo):
                    self._last_used.remove(lu_logo)
            self._last_used.append(logo)
        self.trimLastUsed()

    def setTeam1Logo(self, logo):
        if type(logo) is str:
            logo = self.findLogo(logo)

        if self._team1.equals(logo):
            logo.delete(False)
            return True

        if(self._team1.isLogo()):
            self.addLastUsed(self._team1)
        self._team1 = logo
        return True
        
    def resetTeam1Logo(self):
        if(self._team1.isLogo()):
            self.addLastUsed(self._team1)
        self._team1 = Logo(self)

    def setTeam2Logo(self, logo):
        if type(logo) is str:
            logo = self.findLogo(logo)

        if self._team2.equals(logo):
            logo.delete(False)
            return True

        if(self._team2.isLogo()):
            self.addLastUsed(self._team2)
        self._team2 = logo
        return True
        
    def resetTeam2Logo(self):
        if(self._team2.isLogo()):
            self.addLastUsed(self._team2)
        self._team2 = Logo(self)
        
    def swapTeamLogos(self):
        self._team1, self._team2 = self._team2, self._team1

    def addFavorite(self, logo):
        if type(logo) is str:
            logo = self.findLogo(logo)
        if type(logo) is Logo:
            if logo.isLogo():
                for fav_logo in self._favorites:
                    if fav_logo.equals(logo):
                        return False
                self._favorites.append(logo)
                return True
        return False

    def removeFavorite(self, logo):
        if type(logo) is Logo:
            logo = logo._ident

        for fav_logo in self._favorites:
            if fav_logo._ident == logo:
                self._favorites.remove(fav_logo)
                return True
        return False

    def isUsed(self, ident):
        if not ident:
            return False
        if ident == self._team1._ident:
            return True
        if ident == self._team2._ident:
            return True
        for logo in self._favorites:
            if ident == logo._ident:
                return True
        return False
        
    def isInLastused(self, ident):
        if not ident:
            return False
        for logo in self._favorites:
            if ident == logo._ident:
                return True
        return False

    def findLogo(self, ident):
        if not ident:
            return None
        if ident == self._team1._ident:
            return self._team1
        if ident == self._team2._ident:
            return self._team2
        for logo in self._favorites:
            if ident == logo._ident:
                return logo
        for logo in self._last_used:
            if ident == logo._ident:
                return logo
        return None

    def removeDuplicates(self):
        all_logos = [self._team1, self._team2] + \
            self._favorites + self._last_used
        for logo1, logo2 in itertools.combinations(all_logos, 2):
            if logo1.equals(logo2) and logo1._ident != logo2._ident:
                logo2.delete(True, False)
                logo2._ident = logo1._ident
            
    def getFavorites(self):
        return self._favorites

    def getLastUsed(self):
        lastused = list(self._last_used)
        lastused.reverse()
        return lastused

    def getTeam1(self):
        return self._team1

    def getTeam2(self):
        return self._team2
        
    def pixmap2ident(self, pixmap):
        for ident, map in self._ident2map.items():
            if map.cacheKey() == pixmap.cacheKey():
                return ident
        return ""


class Logo:
    
    _iconsize = 120

    def __init__(self, manager):
        self._manager = manager
        self._reset()

    def _reset(self):
        self._format = "none"
        self._width = 0
        self._height = 0
        self._size = 0
        self._ident = "0"

    def generateIdentifier(self):
        while True:
            self._ident = self._uniqid()
            if self._ident in self._manager._identifiers:
                continue
            else:
                self._manager._identifiers.add(self._ident)
                break

    def isLogo(self):
        return bool(self._ident != "0")

    def isFile(self):
        if self.isLogo():
            return os.path.isfile(self.getAbsFile())
        else:
            return False

    def getFile(self, web=False):
        if self._format == "none":
            file = os.path.join(OBShtmlDir, "src/SC2.png")
        else:
            file = os.path.join(logosDir, "{}.{}".format(self._ident, self._format))
            
        if web:
            file = file.replace('\\','/')
            
        return file

    def getAbsFile(self):
        file = self.getFile()
        if file:
            return getAbsPath(file)
        else:
            return file

    def fromFile(self, file):
        if not os.path.isfile(file):
            file = getAbsPath(file)
            if not os.path.isfile(file):
                return False

        self.generateIdentifier()
        self._format = os.path.splitext(file)[1].replace(".", "").lower()
        newfile = self.getAbsFile()
        shutil.copy(file, newfile)
        self.refreshData()

        return True

    def fromURL(self, url):
        base, ext = os.path.splitext(url)
        self._format = ext.split("?")[0].replace(".", "").lower()
        self.generateIdentifier()
        fname = self.getAbsFile()
        urlretrieve(url, fname)
        self.refreshData()

    def refreshData(self):
        file = self.getAbsFile()
        self._size = os.path.getsize(file)
        map = QPixmap(file)
        self._width = map.height()
        self._height = map.width()

    def _uniqid(self):
        return hex(int(time() * 10000000))[10:]

    def toDict(self):
        data = dict()
        data['ident'] = self._ident
        data['format'] = self._format
        data['width'] = self._width
        data['height'] = self._height
        data['size'] = self._size

        return data

    def fromDict(self, data):
        if data is None:
            self._reset()
            return False
        self._ident = data['ident']
        self._format = data['format']
        self._width = data['width']
        self._height = data['height']
        self._size = data['size']

        self._manager._identifiers.add(self._ident)
        return True
        
    def provideQPixmap(self):
        if self._manager._ident2map.get(self._ident, None) is None:
            map = QPixmap(self.getAbsFile()).scaled(self._iconsize, self._iconsize, Qt.KeepAspectRatio)
            self._manager._ident2map[self._ident] = map
        return self._manager._ident2map[self._ident]

    def getDesc(self):
        size = humanize.naturalsize(self._size)
        return "{}, {}x{}px".format(self._format.upper(), self._width, self._height, str(size))

    def __str__(self):
        return str(self.toDict())

    def delete(self, force=False, reset=True):
        if force or not self._manager.isUsed(self._ident):
            if self.isFile():
                os.remove(self.getAbsFile())
            if reset:
                self._reset()

    def equals(self, logo):
        if self._ident == logo._ident:
            return True
        if (self._format == logo._format and self._size == logo._size
            and self._height == logo._height
            and self._width == logo._width
                and filecmp.cmp(self.getAbsFile(), logo.getAbsFile())):
            return True
