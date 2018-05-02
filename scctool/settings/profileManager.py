import logging
import os
import random
import shutil
import sys

import appdirs
from PyQt5.QtCore import QSettings

from scctool.settings.client_config import ClientConfig

module_logger = logging.getLogger(
    'scctool.settings.profileManager')  # create logger

# TODO: Tell browser sources what profile is used.


class ProfileManager:

    _settings = QSettings(ClientConfig.APP_NAME, ClientConfig.COMPANY_NAME)

    def __init__(self, local=False):
        self.setupDirs(local)
        self._loadSettings()

    def basedir(self):
        return self._basedir

    def profilesdir(self):
        return self._profilesdir

    def profiledir(self, profile=""):
        if not profile:
            profile = self._current
        return os.path.join(self._profilesdir, profile)

    def getFile(self, file, profile=""):
        if not profile:
            profile = self._current
        return os.path.normpath(os.path.join(self._profilesdir, profile, file))

    def setupDirs(self, local=False):
        if local:
            if getattr(sys, 'frozen', False):
                self._basedir = os.path.dirname(sys.executable)
            else:
                self._basedir = os.path.dirname(
                    sys.modules['__main__'].__file__)
        else:
            self._basedir = appdirs.user_data_dir(
                ClientConfig.APP_NAME, ClientConfig.COMPANY_NAME)

        self._profilesdir = os.path.join(self._basedir, 'profiles')

        if not os.path.exists(self._basedir):
            os.makedirs(self._basedir)
        if not os.path.exists(self._profilesdir):
            os.makedirs(self._profilesdir)

    def _saveSettings(self):
        self._settings.setValue('profiles', self._profiles)

    def _loadSettings(self):
        self._default = ""
        self._current = ""
        self._profiles = self._settings.value('profiles', dict())
        self._checkProfils()
        self.setCurrent(self._default)

    def _checkProfils(self):
        profiles = list(self._profiles.keys())
        for profile in profiles:
            if not os.path.exists(self.profiledir(profile)):
                del self._profiles[profile]

        if len(self._profiles) == 0:
            self.addProfile("Default", True, True)

        self._default = ""
        self._current = ""

        for profile, info in self._profiles.items():
            if info['default'] and not self._default:
                self._default = profile
            elif info['default'] and self._default:
                self._profiles[profile]['default'] = False

        if not self._current:
            self.setCurrent(profile)
        if not self._default:
            self.setDefault(profile)

        self._saveSettings()

    def renameProfile(self, myid, name):
        name = name.strip()

        if name == self._profiles[myid].get('name', ''):
            return

        if not name:
            raise ValueError(_('You cannot use empty names.'))

        for id, info in self._profiles.items():
            if info['name'] == name:
                raise ValueError(_('The name is already in use.'))

        self._profiles[myid]['name'] = name
        self._saveSettings()

    def setCurrent(self, profile):
        if profile in self._profiles.keys():
            self._current = profile

    def current(self):
        id = self._current
        data = dict()
        data['id'] = id
        data['name'] = self._profiles[id]['name']
        data['default'] = self._profiles[id]['default']
        data['current'] = True
        return data

    def currentID(self):
        return self._current

    def setDefault(self, profile):
        if self._default:
            self._profiles[self._default]['default'] = False

        self._profiles[profile]['default'] = True
        self._default = profile

        self._saveSettings()

    def addProfile(self, name, current=False, default=False, copy=''):
        name = name.strip()
        if not name:
            raise ValueError(_('You cannot use empty names.'))

        for id, info in self._profiles.items():
            if info['name'] == name:
                raise ValueError(_('The name is already in use.'))

        if copy and copy not in self._profiles.keys():
            raise ValueError(_('Initial profile is not valid.'))

        profile = self._uniqid()

        self._profiles[profile] = dict()
        self._profiles[profile]['name'] = name
        self._profiles[profile]['default'] = default

        dir = self.profiledir(profile)

        if copy:
            if os.path.exists(dir):
                shutil.rmtree(dir)
            shutil.copytree(self.profiledir(copy), dir)
        else:
            if not os.path.exists(dir):
                os.makedirs(dir)

        if current:
            self.setCurrent(profile)

        if default:
            self.setDefault(profile)

        module_logger.info('Profile {} created.'.format(profile))
        self._saveSettings()
        return profile

    def _uniqid(self):
        while True:
            uniqid = hex(random.randint(49152, 65535))[2:]
            if uniqid not in self._profiles.keys():
                return uniqid

    def deleteProfile(self, profile):
        if profile in self._profiles.keys():
            if len(self._profiles) <= 1:
                raise ValueError("Last profile cannot be deleted.")
            dir = self.profiledir(profile)
            shutil.rmtree(dir)
            del self._profiles[profile]
            if self._current == profile or self._default == profile:
                self._checkProfils()
            module_logger.info('Profile {} deleted.'.format(profile))
            self._saveSettings()
            return True
        return False

    def exportProfile(self, profile, filename):
        filename, file_extension = os.path.splitext(filename)
        if profile not in self._profiles.keys():
            raise ValueError("Profile '{}' is not valid.".format(profile))
        dir = self.profiledir(profile)
        shutil.make_archive(filename, 'zip', dir)

    def importProfile(self, filename, name):
        id = self.addProfile(name)
        dir = self.profiledir(id)
        shutil.unpack_archive(filename, dir)
        self._saveSettings()
        return id

    def getProfiles(self):
        for id, info in self._profiles.items():
            data = dict()
            data['id'] = id
            data['name'] = info['name']
            data['default'] = info['default']
            data['current'] = self._current == id
            yield data
