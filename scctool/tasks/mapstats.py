"""Manager and thread to save map stats and keep them up-to-date."""
import json
import logging
import os
import time

from PyQt5.QtCore import pyqtSignal

import scctool.settings
import scctool.settings.translation
from scctool.tasks.liquipedia import LiquipediaGrabber, MapNotFound
from scctool.tasks.tasksthread import TasksThread

module_logger = logging.getLogger(__name__)
# _ = scctool.settings.translation.gettext


class MapStatsManager:
    """MapStats Manager."""

    def __init__(self, controller):
        """Init the mapstats manager."""
        self.__controller = controller
        self.loadJson()
        self.__thread = MapStatsThread(self)
        self.__thread.newMapData.connect(self._newData)
        self.__thread.newMapPool.connect(self._newMapPool)
        if not scctool.settings.test:
            self.refreshMapPool()
            self.refreshMaps()

    def _getMaps(self):
        return self.__maps.keys()

    def loadJson(self):
        """Read json data from file."""
        file = scctool.settings.getJsonFile('mapstats')
        if not os.path.exists(file):
            file = scctool.settings.getResFile('mapstats.json')
        try:
            with open(file,
                      'r',
                      encoding='utf-8-sig') as json_file:
                data = json.load(json_file)
        except Exception:
            data = dict()

        self.__maps = data.get('maps', dict())
        self.__customMapPool = data.get('custom_mappool', list())
        self.__ladderMapPool = data.get('ladder_mappool', list())
        self.__mappool_refresh = int(data.get('mappool_refresh', 0))
        self.__mappool = int(data.get('mappool', 0))
        self.__current_map = ''

        if not isinstance(self.__maps, dict):
            self.__maps = dict()
        if not isinstance(self.__customMapPool, list):
            self.__customMapPool = list()
        if not isinstance(self.__ladderMapPool, list):
            self.__ladderMapPool = list()
        if not isinstance(self.__current_map, str):
            self.__current_map = ""

    def dumpJson(self):
        """Write json data to file."""
        data = dict()
        data['maps'] = self.__maps
        data['custom_mappool'] = self.__customMapPool
        data['ladder_mappool'] = self.__ladderMapPool
        data['mappool'] = self.__mappool
        data['mappool_refresh'] = self.__mappool_refresh

        try:
            with open(scctool.settings.getJsonFile('mapstats'),
                      'w',
                      encoding='utf-8-sig') as outfile:
                json.dump(data, outfile)
        except Exception:
            module_logger.exception("message")

    def selectMap(self, map2select, send=True):
        """Select a map in the mapstats browser source."""
        if map2select in self.__maps.keys():
            self.__current_map = map2select
            if scctool.settings.config.parser.getboolean(
                    "Mapstats", "mark_played",):
                played = self.__controller.matchControl.\
                    activeMatch().wasMapPlayed(map2select)
            else:
                played = False
            if scctool.settings.config.parser.getboolean(
                    "Mapstats", "mark_vetoed",):
                vetoed = self.__controller.matchControl.\
                    activeMatch().isMapVetoed(map2select)
            else:
                vetoed = False
            if send:
                self.__controller.websocketThread.selectMap(
                    map2select, played, vetoed)

    def setMapPoolType(self, pool_id):
        """Set the mappool type."""
        self.__mappool = int(pool_id)

    def getMapPoolType(self):
        """Get the map pool type."""
        return int(self.__mappool)

    def getCustomMapPool(self):
        """Get the custom map pool."""
        if len(self.__customMapPool) == 0:
            for mymap in self.getLadderMapPool():
                yield mymap
        else:
            for mymap in self.__customMapPool:
                yield mymap

    def getLadderMapPool(self):
        """Get the ladder map pool."""
        for mymap in self.__ladderMapPool:
            yield mymap

    def setCustomMapPool(self, maps):
        """Set the custom map pool."""
        self.__customMapPool = list(maps)

    def getMapPool(self):
        """Return the map pool."""
        if self.__mappool == 0:
            for mymap in self.getLadderMapPool():
                yield mymap
        elif self.__mappool == 1:
            for mymap in self.getCustomMapPool():
                yield mymap
        else:
            for mymap in self.__controller.matchControl.\
                    activeMatch().yieldMaps():
                if mymap and mymap != "TBD":
                    yield mymap

    def refreshMapPool(self):
        """Refresh the map pool."""
        if (not self.__mappool_refresh
                or (time.time() - int(self.__mappool_refresh)) > 24 * 60 * 60):
            self.__thread.activateTask('refresh_mappool')

    def refreshMaps(self):
        """Refresh map data from liquipedia."""
        for mymap in scctool.settings.maps:
            if mymap != 'TBD' and mymap not in self.__maps.keys():
                self.__maps[mymap] = dict()
                self.__maps[mymap]['tvz'] = None
                self.__maps[mymap]['zvp'] = None
                self.__maps[mymap]['pvt'] = None
                self.__maps[mymap]['creator'] = None
                self.__maps[mymap]['size'] = None
                self.__maps[mymap]['spawn-positions'] = None
                self.__maps[mymap]['refreshed'] = None
                self.__maps[mymap]['broodwar'] = False

        maps2refresh = list()
        maps2refresh_full = list()

        for mymap, data in self.__maps.items():
            # TODO: Old elegant version is currently no longer possible:
            is_none = False
            for key in ['creator', 'size', 'spawn-positions']:
                if data.get(key, None) is None:
                    maps2refresh_full.append(mymap)
                    is_none = True
                    break
            if is_none:
                continue
            last_refresh = data.get('refreshed', None)
            if (not last_refresh
                    or (time.time() - int(last_refresh)) > 24 * 60 * 60):
                maps2refresh.append(mymap)

            # Unelegant way:
            # last_refresh = data.get('refreshed', None)
            # if (not last_refresh or
            #         (time.time() - int(last_refresh)) > 24 * 60 * 60):
            #     maps2refresh_full.append(map)

        if len(maps2refresh) > 0:
            self.__thread.setMaps(maps2refresh)
            self.__thread.activateTask('refresh_stats')

        if len(maps2refresh_full) > 0:
            self.__thread.setMaps(maps2refresh_full, True)
            self.__thread.activateTask('refresh_data')

    def _newData(self, new_map, data):
        for key, item in data.items():
            self.__maps[new_map][key] = item

    def _newMapPool(self, data):
        if len(data) > 0:
            self.__ladderMapPool = data
            self.__mappool_refresh = int(time.time())

    def close(self, save=True):
        """Close the manager."""
        self.__thread.terminate()
        if save:
            self.dumpJson()

    def _sortMaps(self):
        self.__maps = {k: self.__maps[k] for k in sorted(self.__maps)}

    def getData(self):
        """Get data to be send to the browser source."""
        out_data = dict()
        if self.__current_map in self.getMapPool():
            out_data['map'] = self.__current_map
        else:
            out_data['map'] = None
        out_data['maps'] = dict()
        self._sortMaps()
        for mymap, data in self.__maps.items():
            if mymap not in self.getMapPool():
                continue
            out_data['maps'][mymap] = dict()
            out_data['maps'][mymap]['map-name'] = mymap.replace(
                'Dreamcatcher', 'Dream<wbr>catcher')
            if out_data['map'] is None:
                out_data['map'] = mymap
            if scctool.settings.config.parser.getboolean(
                    "Mapstats", "mark_played",):
                out_data['maps'][mymap]['played'] = \
                    self.__controller.matchControl.\
                    activeMatch().wasMapPlayed(mymap)
            else:
                out_data['maps'][mymap]['played'] = False
            if scctool.settings.config.parser.getboolean(
                    "Mapstats", "mark_vetoed",):
                out_data['maps'][mymap]['vetoed'] = \
                    self.__controller.matchControl.\
                    activeMatch().isMapVetoed(mymap)
            else:
                out_data['maps'][mymap]['vetoed'] = False
            for key, item in data.items():
                if key == 'refreshed':
                    continue
                if not item:
                    item = "?"
                key = key.replace('spawn-positions', 'positions')
                out_data['maps'][mymap][key] = item

        return out_data

    def sendMapPool(self):
        """Send the map pool data to the browser source."""
        data = self.getData()
        self.__controller.websocketThread.sendData2Path(
            'mapstats', "MAPSTATS", data)


class MapStatsThread(TasksThread):
    """Thread to update map stats data."""

    newMapData = pyqtSignal(str, object)
    newMapPool = pyqtSignal(object)

    def __init__(self, manager):
        """Init the thread."""
        super().__init__()
        self.__manager = manager
        self.__grabber = LiquipediaGrabber()
        self.setTimeout(30)
        self.addTask('refresh_data', self.__refresh_data)
        self.addTask('refresh_stats', self.__refresh_stats)
        self.addTask('refresh_mappool', self.__refresh_mappool)

    def setMaps(self, maps, full=False):
        """Set the maps."""
        if full:
            self.__fullmaps = maps
        else:
            self.__maps = maps

    def __refresh_data(self):
        try:
            mymap = self.__fullmaps.pop()
            try:
                liquipediaMap = self.__grabber.find_map(mymap)
                stats = liquipediaMap.get_stats()
                info = liquipediaMap.get_info()
                data = dict()
                data['tvz'] = stats['tvz']
                data['zvp'] = stats['zvp']
                data['pvt'] = stats['pvt']
                data['creator'] = info['creator']
                data['broodwar'] = liquipediaMap.is_broodwar()
                data['size'] = info['size']
                data['spawn-positions'] = info['spawn-positions']
                data['refreshed'] = int(time.time())
                self.newMapData.emit(mymap, data)
                module_logger.info(f'Map {mymap} found.')
            except MapNotFound:
                module_logger.info(f'Map {mymap} not found.')
            except ConnectionError:
                module_logger.info(f'Connection Error for map {mymap}.')
            except Exception:
                module_logger.exception("message")
        except IndexError:
            self.deactivateTask('refresh_data')

    def __refresh_stats(self):
        try:
            for stats in self.__grabber.get_map_stats(self.__maps):
                mymap = stats['map']
                data = dict()
                data['tvz'] = stats['tvz']
                data['zvp'] = stats['zvp']
                data['pvt'] = stats['pvt']
                data['refreshed'] = int(time.time())
                module_logger.info(f'Map {mymap} found.')
                self.newMapData.emit(mymap, data)
        finally:
            self.deactivateTask('refresh_stats')

    def __refresh_mappool(self):
        try:
            mappool = list(self.__grabber.get_ladder_mappool())
            self.newMapPool.emit(mappool)
            module_logger.info('Current map pool found.')
        finally:
            self.deactivateTask('refresh_mappool')
