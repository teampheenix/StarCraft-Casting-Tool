"""Provides safe-data for SCCTool."""
import json
import logging

module_logger = logging.getLogger(__name__)


class SafeGuard:
    """Provides data sensitive data from a json file."""

    safe = dict()
    loaded = False

    def __init__(self):
        """Init guard."""
        pass

    def loadJson(self):
        """Load json file."""
        from scctool.settings import getResFile
        try:
            with open(getResFile('safe.json'), 'r',
                      encoding='utf-8-sig') as json_file:
                self.safe = json.load(json_file)
        except Exception:
            self.safe = dict()

        self.loaded = True

    def get(self, key):
        """Get an entry from the guard."""
        if not self.loaded:
            self.loadJson()
        return self.safe.get(key, '')
