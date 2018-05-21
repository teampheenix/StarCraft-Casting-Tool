"""Interaction with Browser Source via Websocket."""
import asyncio
import json
import logging
import re

import keyboard
import websockets
from PyQt5.QtCore import QThread, pyqtSignal

import scctool.settings

# create logger
module_logger = logging.getLogger('scctool.tasks.websocket')


class WebsocketThread(QThread):
    """Thread for websocket interaction."""

    keyboard_state = dict()
    socketConnectionChanged = pyqtSignal(int, str)
    valid_scopes = ['score', 'mapicons_box_[1-3]', 'intro', 'mapstats']
    scopes = dict()

    def __init__(self, controller):
        """Init thread."""
        QThread.__init__(self)
        self.connected = dict()
        self.__loop = None
        self.__controller = controller
        self.setup_scopes()

    def setup_scopes(self):
        self.scope_regex = re.compile(r'_\[\d-\d\]')
        for scope in self.valid_scopes:
            scope = self.scope_regex.sub('', scope)
            self.scopes[scope] = set()

    def get_primary_scopes(self):
        return list(self.scopes.keys())

    def run(self):
        """Run thread."""
        module_logger.info("WebSocketThread starting!")
        self.connected = dict()
        self.__loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.__loop)

        port = int(scctool.settings.profileManager.currentID(), 16)
        module_logger.info(
            'Starting Websocket Server with port {}.'.format(port))
        # Create the server.
        start_server = websockets.serve(self.handler,
                                        host='localhost',
                                        port=port,
                                        max_queue=16,
                                        max_size=10240,
                                        read_limit=10240,
                                        write_limit=10240)
        self.__server = self.__loop.run_until_complete(start_server)
        self.register_hotkeys()
        self.__loop.run_forever()

        # Shut down the server.
        self.__server.close()
        self.__loop.run_until_complete(self.__server.wait_closed())
        self.unregister_hotkeys()

        module_logger.info("WebSocketThread finished!")

    def stop(self):
        if self.__loop is not None:
            module_logger.info("Requesting stop of WebsocketThread.")
            self.__loop.call_soon_threadsafe(self.__loop.stop)

    def __callback_on_hook(self, scan_code, is_keypad, e, callback):
        if e.is_keypad == is_keypad:
            if e.event_type == keyboard.KEY_DOWN:
                if((scan_code, is_keypad) not in self.keyboard_state or
                   self.keyboard_state[(scan_code, is_keypad)]):
                    try:
                        callback()
                    except Exception as e:
                        module_logger.exception("message")
                self.keyboard_state[(scan_code, is_keypad)] = False
            if e.event_type == keyboard.KEY_UP:
                self.keyboard_state[(scan_code, is_keypad)] = True

    def __register_hotkey(self, string, callback):
        data = scctool.settings.config.loadHotkey(string)
        if not data['name']:
            return
        if data['scan_code'] == 0:
            return

        keyboard.hook_key(data['scan_code'], lambda e: self.__callback_on_hook(
            data['scan_code'], data['is_keypad'], e, callback))

    def register_hotkeys(self):
        self.__register_hotkey(
            scctool.settings.config.parser.get("Intros", "hotkey_player1"),
            lambda: self.showIntro(0))

        self.__register_hotkey(
            scctool.settings.config.parser.get("Intros", "hotkey_player2"),
            lambda: self.showIntro(1))

        self.__register_hotkey(
            scctool.settings.config.parser.get("Intros", "hotkey_debug"),
            lambda: self.sendData2Path("intro", "DEBUG_MODE", dict()))

    def unregister_hotkeys(self):
        try:
            keyboard.unhook_all()
        except AttributeError:
            pass
        finally:
            self.keyboard_state = dict()

    def handle_path(self, path):
        paths = path.split('/')[1:]

        for path in paths:
            for scope in self.valid_scopes:
                if re.match(scope, path):
                    return path
        return ''

    def get_primary_scope(self, path):
        if path in self.scopes.keys():
            return path
        for scope in self.valid_scopes:
            if re.match(scope, path):
                return self.scope_regex.sub('', scope)
        return ''

    async def handler(self, websocket, path):
        path = self.handle_path(path)
        if not path:
            module_logger.info("Client with incorrect path.")
            return
        self.registerConnection(websocket, path)
        module_logger.info("Client connected!")
        self.changeStyle(path)
        primary_scope = self.get_primary_scope(path)
        if primary_scope == 'mapstats':
            self.changeColors(primary_scope)
            self.changeFont(primary_scope)
            data = self.__controller.mapstatsManager.getData()
            self.sendData2WS(websocket, "MAPSTATS", data)
        elif primary_scope == 'score':
            self.changeFont(primary_scope)
            data = self.__controller.matchData.getScoreData()
            self.sendData2WS(websocket, "ALL_DATA", data)
        elif primary_scope == 'mapicons_box':
            self.changeFont(primary_scope)
            data = self.__controller.matchData.getMapIconsData()
            self.sendData2WS(websocket, 'DATA', data)
        else:
            module_logger.info(
                "Couldn't connect websocket: {} {}".
                format(path, primary_scope))

        while True:
            try:
                await asyncio.wait_for(websocket.recv(), timeout=20)
            except asyncio.TimeoutError:
                try:
                    pong_waiter = await websocket.ping()
                    await asyncio.wait_for(pong_waiter, timeout=10)
                except asyncio.TimeoutError:
                    # No response to ping in 10 seconds, disconnect.
                    module_logger.info(
                        "No response to ping in 10 seconds, disconnect.")
                    break
            except websockets.ConnectionClosed:
                module_logger.info("Connection closed")
                break

        module_logger.info("Connection removed")
        self.unregisterConnection(websocket, path)

    def registerConnection(self, websocket, path):
        if path not in self.connected.keys():
            self.connected[path] = set()
        primary_scope = self.get_primary_scope(path)
        self.scopes[primary_scope].add(path)
        self.connected[path].add(websocket)
        self.socketConnectionChanged.emit(
            len(self.connected[path]), primary_scope)

    def unregisterConnection(self, websocket, path):
        if path in self.connected.keys():
            self.connected[path].remove(websocket)
            primary_scope = self.get_primary_scope(path)
            self.socketConnectionChanged.emit(
                len(self.connected[path]), primary_scope)

    def changeStyle(self, path, style=None):
        primary_scope = self.get_primary_scope(path)
        if primary_scope:
            if style is None:
                style = scctool.settings.config.parser.get(
                    "Style", primary_scope)
            style_file = "src/css/{}/{}.css".format(primary_scope, style)
            self.sendData2Path(path, "CHANGE_STYLE", {'file': style_file})
        else:
            raise ValueError('Change style is not available for this path.')

    def changeColors(self, path, colors=None):
        if path in ['mapstats']:
            if colors is None:
                colors = dict()
                for i in range(1, 3):
                    key = 'color{}'.format(i)
                    colors[key] = scctool.settings.config.parser.get(
                        "Mapstats", key)
            self.sendData2Path(path, "CHANGE_COLORS", colors)
        else:
            raise ValueError('Change style is not available for this path.')

    def changeFont(self, path=None, font=None):
        valid_paths = ['mapstats', 'score', 'mapicons_box']
        if path is None:
            for path in valid_paths:
                self.changeFont(path, font)
            return
        if path in valid_paths:
            if font is None:
                if not scctool.settings.config.parser.getboolean(
                    "Style",
                        "use_custom_font"):
                    font = "DEFAULT"
                else:
                    font = scctool.settings.config.parser.get(
                        "Style", "custom_font")
            self.sendData2Path(path, "CHANGE_FONT", {'font': font})
        else:
            raise ValueError('Change font is not available for this path.')

    def showIntro(self, idx):
        self.sendData2Path("intro", "SHOW_INTRO",
                           self.__controller.getPlayerIntroData(idx))

    def selectMap(self, map):
        self.sendData2Path('mapstats', 'SELECT_MAP', {'map': str(map)})

    def sendData2Path(self, path, event, input_data):
        try:
            data = dict()
            data['event'] = event
            data['data'] = input_data

            paths = self.scopes.get(path, [path])

            for path in paths:
                connections = self.connected.get(path, set()).copy()
                for websocket in connections:
                    module_logger.info("Sending data: %s" % data)
                    coro = websocket.send(json.dumps(data))
                    asyncio.run_coroutine_threadsafe(coro, self.__loop)
        except Exception as e:
            module_logger.exception("message")

    def sendData2WS(self, websocket, event, input_data):
        try:
            data = dict()
            data['event'] = event
            data['data'] = input_data
            module_logger.info("Sending data: %s" % data)
            coro = websocket.send(json.dumps(data))
            asyncio.run_coroutine_threadsafe(coro, self.__loop)
        except Exception as e:
            module_logger.exception("message")
