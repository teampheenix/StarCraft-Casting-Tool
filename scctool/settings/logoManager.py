"""Provide logo manager for SCCTool."""
import filecmp
import itertools
import json
import logging
import os
import shutil
from time import time
from urllib.request import urlopen, urlretrieve

import humanize
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap

from scctool.settings import (casting_html_dir, getAbsPath, getJsonFile,
                              logosDir)

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
        self._matches = dict()
        try:
            self.loadJson()
            self.removeDeadMatches()
            self.removeDuplicates()
            self.clearFolder()
        except Exception as e:
            module_logger.exception("message")

    def newLogo(self):
        return Logo(self)

    def dumpJson(self):
        data = dict()
        data['last_used'] = []
        data['favorites'] = []
        data['matches'] = {}

        for key, match_data in self._matches.items():
            data['matches'][key] = {}
            data['matches'][key]['team1'] = match_data.get('team1').toDict()
            data['matches'][key]['team2'] = match_data.get('team2').toDict()

        for item in self._last_used:
            data['last_used'].append(item.toDict())
        for item in self._favorites:
            data['favorites'].append(item.toDict())

        try:
            with open(getJsonFile('logos'), 'w',
                      encoding='utf-8-sig') as outfile:
                json.dump(data, outfile)
        except Exception as e:
            module_logger.exception("message")

    def loadJson(self):
        self._identifiers = set()
        self._last_used = []
        self._favorites = []
        data = dict()

        try:
            with open(getJsonFile('logos'), 'r',
                      encoding='utf-8-sig') as json_file:
                data = json.load(json_file)
        except (OSError, IOError):
            return

        for item in data['last_used']:
            logo = Logo(self)
            logo.fromDict(item)
            self.addLastUsed(logo)
        for item in data['favorites']:
            logo = Logo(self)
            logo.fromDict(item)
            if logo.isFile():
                self._favorites.append(logo)

        if 'team1' in data and 'team2' in data:
            key = self.checkMatchIdent('')
            self._matches[key] = dict()
            self._matches[key]['logo_changed'] = False
            self._matches[key]['team1'] = Logo(self, data.get('team1', None))
            self._matches[key]['team2'] = Logo(self, data.get('team2', None))

        for key, item in data.get('matches', dict()).items():
            self._matches[key] = dict()
            self._matches[key]['logo_changed'] = False
            self._matches[key]['team1'] = Logo(self, item.get('team1', None))
            self._matches[key]['team2'] = Logo(self, item.get('team2', None))

    def removeDeadMatches(self):
        validMatches = self.__controller.matchControl.getMatchIDs()
        for key in self._matches.keys():
            if key not in validMatches:
                self.deleteMatch(key)

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

    def checkMatchIdent(self, match_ident):
        if not match_ident:
            match_ident = self.__controller.matchControl.selectedMatchId()
        if match_ident not in self._matches.keys():
            self.createMatch(match_ident)

        return match_ident

    def deleteMatch(self, match_ident=''):
        match_ident = self.checkMatchIdent(match_ident)
        self.resetTeam1Logo(match_ident)
        self.resetTeam2Logo(match_ident)
        del self._matches[match_ident]

    def setTeamLogo(self, idx, logo, match_ident=''):

        match_ident = self.checkMatchIdent(match_ident)

        if type(logo) is str:
            logo = self.findLogo(logo)
            if logo is None:
                return False

        if self.getTeam(idx, match_ident).equals(logo):
            logo.delete(False)
            return True

        if(self.getTeam(idx, match_ident).isLogo()):
            self.addLastUsed(self.getTeam(idx, match_ident))
        self._matches[match_ident]['team{}'.format(idx)] = logo
        self._matches[match_ident]['logo_changed'] = True
        return True

    def setTeam1Logo(self, logo, match_ident=''):
        return self.setTeamLogo(1, logo, match_ident)

    def setTeam2Logo(self, logo, match_ident=''):
        return self.setTeamLogo(2, logo, match_ident)

    def resetTeamLogo(self, idx, match_ident=''):
        match_ident = self.checkMatchIdent(match_ident)

        if(self.getTeam(idx, match_ident).isLogo()):
            self.addLastUsed(self.getTeam(idx, match_ident))
        self._matches[match_ident]['team{}'.format(idx)] = Logo(self)
        self._matches[match_ident]['logo_changed'] = True

    def resetTeam1Logo(self, match_ident=''):
        return self.resetTeamLogo(1, match_ident)

    def resetTeam2Logo(self, match_ident=''):
        return self.resetTeamLogo(2, match_ident)

    def createMatch(self, match_ident):
        self._matches[match_ident] = dict()
        self._matches[match_ident]['logo_changed'] = False
        self._matches[match_ident]['team1'] = Logo(self)
        self._matches[match_ident]['team2'] = Logo(self)

    def swapTeamLogos(self, match_ident=''):
        match_ident = self.checkMatchIdent(match_ident)
        self._matches[match_ident]['team1'], \
            self._matches[match_ident]['team2'] = \
            self._matches[match_ident]['team2'], \
            self._matches[match_ident]['team1']

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
        for item in self._matches.values():
            if ident == item['team1']._ident:
                return True
            if ident == item['team2']._ident:
                return True
        for logo in self._favorites:
            if ident == logo._ident:
                return True
        return False

    def isInLastused(self, ident):
        if not ident:
            return False
        for logo in self._last_used:
            if ident == logo._ident:
                return True
        return False

    def findLogo(self, ident):
        if not ident:
            return None
        for item in self._matches.values():
            if ident == item['team1']._ident:
                return item['team1']
            if ident == item['team2']._ident:
                return item['team2']
        for logo in self._favorites:
            if ident == logo._ident:
                return logo
        for logo in self._last_used:
            if ident == logo._ident:
                return logo
        return None

    def removeDuplicates(self):
        all_logos = []
        for item in self._matches.values():
            all_logos.append(item['team1'])
            all_logos.append(item['team2'])
        all_logos = all_logos + self._favorites + self._last_used
        for logo1, logo2 in itertools.combinations(all_logos, 2):
            if logo1.equals(logo2) and logo1._ident != logo2._ident:
                logo2.delete(True, False)
                logo2._ident = logo1._ident

    def clearFolder(self):
        dir = getAbsPath(logosDir)

        for fname in os.listdir(dir):
            full_fname = os.path.join(dir, fname)
            name, ext = os.path.splitext(fname)
            ext = ext.replace(".", "")
            if (os.path.isfile(full_fname) and
                    not (self.isUsed(name) or self.isInLastused(name))):
                os.remove(full_fname)
                module_logger.info("Removed logo {}".format(full_fname))

    def hasLogoChanged(self, match_ident=''):
        match_ident = self.checkMatchIdent(match_ident)
        return bool(self._matches[match_ident].get('logo_changed', False))

    def resetLogoChanged(self, match_ident=''):
        match_ident = self.checkMatchIdent(match_ident)
        self._matches[match_ident]['logo_changed'] = False

    def getFavorites(self):
        return self._favorites

    def getLastUsed(self, match_ident=''):
        lastused = list(self._last_used)

        # TODO: Add other logos
        if match_ident:
            for key, logos in self._matches.item():
                if key != match_ident:
                    logo1 = logos.get('team1')
                    logo2 = logos.get('team2')
                    lastused.append(logo2)
                    lastused.append(logo1)

        lastused.reverse()
        return lastused

    def getTeam1(self, match_ident=''):
        match_ident = self.checkMatchIdent(match_ident)
        return self._matches[match_ident].get('team1')

    def getTeam2(self, match_ident=''):
        match_ident = self.checkMatchIdent(match_ident)
        return self._matches[match_ident].get('team2')

    def getTeam(self, idx, match_ident=''):
        match_ident = self.checkMatchIdent(match_ident)
        return self._matches[match_ident].get('team{}'.format(idx))

    def copyMatch(self, new_ident, old_ident=''):
        old_ident = self.checkMatchIdent(old_ident)
        new_ident = self.checkMatchIdent(new_ident)
        for idx in range(1, 3):
            self.setTeamLogo(idx, self.getTeam(idx, old_ident), new_ident)

    def pixmap2ident(self, pixmap):
        for ident, map in self._ident2map.items():
            if map.cacheKey() == pixmap.cacheKey():
                return ident
        return ""


class Logo:

    _iconsize = 120

    def __init__(self, manager, fromDict=None):
        self._manager = manager
        self._reset()
        if isinstance(fromDict, dict):
            self.fromDict(fromDict)

    def _reset(self):
        self._format = "none"
        self._width = 0
        self._height = 0
        self._size = 0
        self._ident = "0"

    def getIdent(self):
        return self._ident

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
            file = os.path.join(casting_html_dir, "src/img/SC2.png")
        else:
            file = os.path.join(logosDir, "{}.{}".format(
                self._ident, self._format))

        if web:
            file = file.replace('\\', '/')

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

    def fromURL(self, url, download=True, localFile=None):
        _, ext = os.path.splitext(url)
        self._format = ext.split("?")[0].replace(".", "").lower()
        self.generateIdentifier()

        fname = self.getAbsFile()

        if not download:
            return fname

        if localFile:
            with open(localFile, "rb") as in_file:
                local_byte = in_file.read(512)

            file = urlopen(url)
            data = file.read(512)
            if(data == local_byte):
                needs_download = False
            else:
                needs_download = True

        if needs_download:
            urlretrieve(url, fname)
            self.refreshData()
            return True
        else:
            return False

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
            map = QPixmap(self.getAbsFile()).scaled(
                self._iconsize, self._iconsize, Qt.KeepAspectRatio)
            self._manager._ident2map[self._ident] = map
        return self._manager._ident2map[self._ident]

    def getDesc(self):
        size = humanize.naturalsize(self._size)
        return "{}, {}x{}px".format(self._format.upper(),
                                    self._width, self._height, str(size))

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
        if (self._format == logo._format and self._size == logo._size and
            self._height == logo._height and self._width == logo._width and
                filecmp.cmp(self.getAbsFile(), logo.getAbsFile())):
            return True
