"""Provides safe-data for SCCTool."""
import json
import logging

module_logger = logging.getLogger(
    'scctool.settings.safeGuard')  # create logger


class SafeGuard:

    safe = dict()
    loaded = False

    def __init__(self):
        pass

    def loadJson(self):
        from scctool.settings import getResFile
        try:
            with open(getResFile('safe.json'), 'r',
                      encoding='utf-8-sig') as json_file:
                self.safe = json.load(json_file)
        except Exception as e:
            self.safe = dict()

        self.loaded = True

    def get(self, key):
        if not self.loaded:
            self.loadJson()
        return self.safe.get(key, '')
