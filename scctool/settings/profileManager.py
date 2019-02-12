"""Profile Manager."""
import logging
import os
import random
import shutil
import sys

import appdirs
from PyQt5.QtCore import QSettings

from scctool.settings.client_config import ClientConfig
from scctool.settings.translation import gettext

module_logger = logging.getLogger(__name__)

_ = gettext


class ProfileManager:
    """Profile Manager."""

    _settings = QSettings(ClientConfig.APP_NAME, ClientConfig.COMPANY_NAME)

    def __init__(self, local=False):
        """Init the manager."""
        self.setupDirs(local)
        self._loadSettings()

    def basedir(self):
        """Get the base dir."""
        return self._basedir

    def profilesdir(self):
        """Get the base profile dir."""
        return self._profilesdir

    def profiledir(self, profile=""):
        """Get the dir of (current) profile."""
        if not profile:
            profile = self._current
        return os.path.join(self._profilesdir, profile)

    def getFile(self, file, profile=""):
        """Get absolut path of file in a profile."""
        if not profile:
            profile = self._current
        return os.path.normpath(os.path.join(self._profilesdir, profile, file))

    def setupDirs(self, local=False):
        """Setup profil directory."""
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
        """Save settings."""
        self._settings.setValue('profiles', self._profiles)

    def _loadSettings(self):
        """Load settings."""
        self._default = ""
        self._current = ""
        self._profiles = self._settings.value('profiles', dict())
        self._checkProfils()
        self.setCurrent(self._default)

    def _checkProfils(self):
        """Check all profiles."""
        profiles = list(self._profiles.keys())
        for profile in profiles:
            if not os.path.exists(self.profiledir(profile)):
                del self._profiles[profile]

        if len(self._profiles) == 0:
            for f in os.scandir(self._profilesdir):
                if f.is_dir():
                    self._profiles[f.name] = {
                        'name': 'Default', 'default': True}
                    self._createPortFile(f.name)

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
        """Rename a profile."""
        name = name.strip()

        if name == self._profiles[myid].get('name', ''):
            return

        if not name:
            raise ValueError(_('You cannot use empty names.'))

        for __, info in self._profiles.items():
            if info['name'] == name:
                raise ValueError(_('The name is already in use.'))

        self._profiles[myid]['name'] = name
        self._saveSettings()

    def setCurrent(self, profile):
        """Select the current profile."""
        if profile in self._profiles.keys():
            self._current = profile
            self._createPortFile(profile)

    def current(self):
        """Return the current profile info."""
        ident = self._current
        data = dict()
        data['id'] = ident
        data['name'] = self._profiles[ident]['name']
        data['default'] = self._profiles[ident]['default']
        data['current'] = True
        return data

    def currentID(self):
        """Return the id of the current profile."""
        return self._current

    def setDefault(self, profile):
        """Set the default profile."""
        if self._default and self._default in self._profiles.keys():
            self._profiles[self._default]['default'] = False

        self._profiles[profile]['default'] = True
        self._default = profile

        self._saveSettings()

    def addProfile(self, name, current=False,
                   default=False, copy='', ident=''):
        """Add a new profile."""
        name = name.strip()
        if not name:
            raise ValueError(_('You cannot use empty names.'))

        for info in self._profiles.values():
            if info['name'] == name:
                raise ValueError(_('The name is already in use.'))

        if copy and copy not in self._profiles.keys():
            raise ValueError(_('Initial profile is not valid.'))

        if ident and ident not in self._profiles.keys():
            profile = ident
        else:
            profile = self._uniqid()

        self._profiles[profile] = dict()
        self._profiles[profile]['name'] = name
        self._profiles[profile]['default'] = default

        profile_dir = self.profiledir(profile)

        if copy:
            if os.path.exists(profile_dir):
                shutil.rmtree(profile_dir)
            shutil.copytree(self.profiledir(copy), profile_dir)
        else:
            if not os.path.exists(profile_dir):
                os.makedirs(profile_dir)

        if current:
            self.setCurrent(profile)

        if default:
            self.setDefault(profile)

        self._createPortFile(profile)

        module_logger.info(f'Profile {profile} created.')
        self._saveSettings()
        return profile

    def _createPortFile(self, profile=""):
        from scctool.settings import casting_html_dir
        if not profile:
            profile = self._current

        js_dir = os.path.join(
            self.profiledir(profile),
            casting_html_dir,
            'src/js')
        if not os.path.exists(js_dir):
            os.makedirs(js_dir)
        file = os.path.join(js_dir, 'profile.js')

        with open(file, 'w', encoding='utf-8') as o:
            o.write(f"var profile = '{profile}';")

    def _uniqid(self):
        while True:
            uniqid = hex(random.randint(49152, 65535))[2:]
            if uniqid not in self._profiles.keys():
                return uniqid

    def deleteProfile(self, profile, force=False):
        """Delete a profile."""
        if profile not in self._profiles.keys():
            module_logger.warning('Profile to delete does not exist.')
            return False
        if len(self._profiles) <= 1:
            if force:
                self._profiles = dict()
            else:
                raise ValueError("Last profile cannot be deleted.")
        else:
            del self._profiles[profile]

        directory = self.profiledir(profile)
        shutil.rmtree(directory)
        if ((self._current == profile or self._default == profile) and
                not force):
            self._checkProfils()
        module_logger.info(f'Profile {profile} deleted: {self._profiles}')
        self._saveSettings()
        return True

    def exportProfile(self, profile, filename):
        """Export a profile to a zip archive."""
        filename, __ = os.path.splitext(filename)
        if profile not in self._profiles.keys():
            raise ValueError(f"Profile '{profile}' is not valid.")
        shutil.make_archive(filename, 'zip', self.profiledir(profile))

    def importProfile(self, filename, name, ident=''):
        """Import a profile from a zip archive."""
        ident = self.addProfile(name, ident=ident)
        directory = self.profiledir(ident)
        shutil.unpack_archive(filename, directory)
        self._saveSettings()
        return ident

    def getProfiles(self):
        """Get all profiles."""
        for ident, info in self._profiles.items():
            data = dict()
            data['id'] = ident
            data['name'] = info['name']
            data['default'] = info['default']
            data['current'] = self._current == ident
            yield data
