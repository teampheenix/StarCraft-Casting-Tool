"""Manager and thread to save map stats and keep them up-to-date."""
import json
import logging
import time

from PyQt5.QtCore import pyqtSignal

import scctool.settings
from scctool.tasks.liquipedia import LiquipediaGrabber, MapNotFound
from scctool.tasks.tasksthread import TasksThread

module_logger = logging.getLogger('scctool.tasks.mapstats')


class MapStatsManager:

    def __init__(self):
        self.loadJson()
        self.__thread = MapStatsThread(self)
        self.__thread.newMapData.connect(self._newData)
        self.refreshMaps()
        self.__currentMapPool = ["Abiogenesis", "Acid Plant",
                                 "Backwater", "Blackpink", "Catalyst",
                                 "Eastwatch", "Neon Violet Square"]

    def loadJson(self):
        """Read json data from file."""
        try:
            with open(scctool.settings.mapstats_json_file,
                      'r',
                      encoding='utf-8-sig') as json_file:
                data = json.load(json_file)
        except Exception as e:
            data = dict()

        self.__maps = data.get('maps', dict())

        if not isinstance(self.__maps, dict):
            self.__maps = dict()

    def _getMaps(self):
        return self.__maps.keys()

    def dumpJson(self):
        """Write json data to file."""
        data = dict()
        data['maps'] = self.__maps

        try:
            with open(scctool.settings.mapstats_json_file,
                      'w',
                      encoding='utf-8-sig') as outfile:
                json.dump(data, outfile)
        except Exception as e:
            module_logger.exception("message")

    def refreshMaps(self):
        for map in scctool.settings.maps:
            if map != 'TBD' and map not in self.__maps.keys():
                self.__maps[map] = dict()
                self.__maps[map]['TvZ'] = None
                self.__maps[map]['ZvP'] = None
                self.__maps[map]['PvT'] = None
                self.__maps[map]['Creator'] = None
                self.__maps[map]['Size'] = None
                self.__maps[map]['Spawn Positions'] = None
                self.__maps[map]['refreshed'] = None

        maps2refresh = list()
        for map, data in self.__maps.items():
            last_refresh = data.get('refreshed', None)
            if (not last_refresh
                    or(time.time() - int(last_refresh)) > 24 * 60 * 60):
                maps2refresh.append(map)

        self.__thread.setMaps(maps2refresh)
        self.__thread.activateTask('refresh_data')

    def _newData(self, map, data):
        self.__maps[map] = data

    def close(self):
        self.__thread.terminate()
        self.dumpJson()

    def getData(self):
        out_data = dict()
        for map, data in self.__maps.items():
            if map not in self.__currentMapPool:
                continue
            out_data[map] = dict()
            out_data[map]['map-name'] = map
            for key, item in data.items():
                if key == 'refreshed':
                    continue
                if not item:
                    item = "?"
                key = key.replace('Spawn Positions', 'positions')
                key = key.lower().replace(' ', '-')
                out_data[map][key] = item

        return out_data


class MapStatsThread(TasksThread):

    newMapData = pyqtSignal(str, object)

    def __init__(self, manager):
        super().__init__()
        self.__manager = manager
        self.__grabber = LiquipediaGrabber()
        self.setTimeout(30)
        self.addTask('refresh_data', self.__refresh_data)

    def setMaps(self, maps):
        self.__maps = maps

    def __refresh_data(self):
        try:
            map = self.__maps.pop()
            try:
                liquipediaMap = self.__grabber.get_map(map)
                stats = liquipediaMap.get_stats()
                info = liquipediaMap.get_info()
                data = dict()
                data['TvZ'] = stats['TvZ']
                data['ZvP'] = stats['ZvP']
                data['PvT'] = stats['PvT']
                data['Creator'] = info['Creator']
                data['Size'] = info['Size']
                data['Spawn Positions'] = info['Spawn Positions']
                data['refreshed'] = int(time.time())
                self.newMapData.emit(map, data)
                module_logger.info('Map {} found.'.format(map))
            except MapNotFound:
                module_logger.info('Map {} not found.'.format(map))
            except ConnectionError:
                module_logger.info('Connection Error for map {}.'.format(map))
            except Exception as e:
                module_logger.exception("message")
        except IndexError:
            self.deactivateTask('refresh_data')
