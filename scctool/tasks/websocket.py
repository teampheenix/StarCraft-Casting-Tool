"""Interaction with Browser Source via Websocket."""
import asyncio
import http
import json
import logging
import os.path
import re
from uuid import uuid4

import keyboard
import websockets
from configparser import NoOptionError
from PyQt5.QtCore import QThread, pyqtSignal

import scctool.settings
import scctool.settings.translation

# create logger
module_logger = logging.getLogger(__name__)
_ = scctool.settings.translation.gettext


class WebsocketThread(QThread):
    """Thread for websocket interaction."""

    keyboard_state = dict()
    hooked_keys = dict()
    socketConnectionChanged = pyqtSignal(int, str)
    valid_scopes = ['score', 'mapicons_box_[1-3]', 'mapicons_landscape_[1-3]',
                    'intro', 'mapstats', 'logo_[1-2]', 'ui_logo_[1-2]',
                    'aligulac', 'countdown', 'vetoes']
    mapicon_sets = dict()
    scopes = dict()
    intro_state = ''
    introShown = pyqtSignal()

    def __init__(self, controller):
        """Init thread."""
        QThread.__init__(self)
        self.connected = dict()
        self.__loop = None
        self.__controller = controller
        self.setup_scopes()
        self._hotkeys_active = False
        self.hooked_keys['intro'] = set()
        self.hooked_keys['ctrlx'] = set()

    def setup_scopes(self):
        """Setup all scopes."""
        self.scope_regex = re.compile(r'_\[\d-\d\]')
        for scope in self.valid_scopes:
            scope = self.scope_regex.sub('', scope)
            self.scopes[scope] = set()

    def get_primary_scopes(self):
        """Get all primary scopes."""
        return list(self.scopes.keys())

    @classmethod
    def get_port(cls):
        """Get websocket port from profile ID."""
        return int(scctool.settings.profileManager.currentID(), 16)

    def run(self):
        """Run thread."""
        module_logger.info("WebSocketThread starting!")
        self.connected = dict()
        self.__loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.__loop)

        port = self.get_port()
        module_logger.info(f'Starting Websocket Server with port {port}.')
        # Create the server.
        start_server = websockets.serve(self.handler,
                                        port=port,
                                        max_queue=16,
                                        max_size=10240,
                                        read_limit=10240,
                                        write_limit=10240,
                                        process_request=self.http_request)
        self.__server = self.__loop.run_until_complete(start_server)
        self.__loop.run_forever()

        # Shut down the server.
        self.__server.close()
        self.__loop.run_until_complete(self.__server.wait_closed())
        self.unregister_hotkeys(force=True)

        module_logger.info("WebSocketThread finished!")

    def stop(self):
        """Stop Websocket Thread."""
        if self.__loop is not None:
            module_logger.info("Requesting stop of WebsocketThread.")
            self.__loop.call_soon_threadsafe(self.__loop.stop)

    def __callback_on_hook(self, scan_code, is_keypad, e, callback):
        if e.is_keypad == is_keypad:
            if e.event_type == keyboard.KEY_DOWN:
                if((scan_code, is_keypad) not in self.keyboard_state
                   or self.keyboard_state[(scan_code, is_keypad)]):
                    try:
                        callback()
                    except Exception:
                        module_logger.exception("message")
                self.keyboard_state[(scan_code, is_keypad)] = False
            if e.event_type == keyboard.KEY_UP:
                self.keyboard_state[(scan_code, is_keypad)] = True

    def __register_hotkey(self, hotkey, callback, scope='intro'):
        if isinstance(hotkey, str):
            hotkey = scctool.settings.config.loadHotkey(hotkey)
        if not hotkey['name']:
            return
        if hotkey['scan_code'] == 0:
            return

        value = keyboard.hook_key(
            hotkey['scan_code'],
            lambda e, hotkey=hotkey: self.__callback_on_hook(
                hotkey['scan_code'],
                hotkey['is_keypad'],
                e,
                callback))
        self.hooked_keys[scope].add(value)

    def register_hotkeys(self, scope=''):
        """Register hotkeys."""
        if not scope:
            for scope in self.hooked_keys:
                self.register_hotkeys(scope)
            return
        elif scope == 'intro':
            if (not self.hooked_keys[scope]
                    and len(self.connected.get('intro', [])) > 0):
                module_logger.info('Register intro hotkeys.')
                player1 = scctool.settings.config.loadHotkey(
                    scctool.settings.config.parser.get(
                        "Intros", "hotkey_player1"))
                player2 = scctool.settings.config.loadHotkey(
                    scctool.settings.config.parser.get(
                        "Intros", "hotkey_player2"))
                if player1 == player2:
                    self.__register_hotkey(player1,
                                           lambda: self.showIntro(-1))
                else:
                    self.__register_hotkey(player1,
                                           lambda: self.showIntro(0))

                    self.__register_hotkey(player2,
                                           lambda: self.showIntro(1))

                self.__register_hotkey(
                    scctool.settings.config.parser.get(
                        "Intros", "hotkey_debug"),
                    lambda: self.sendData2Path("intro", "DEBUG_MODE", dict()))
        elif scope == 'ctrlx':
            pass

        module_logger.info('Registered {} hotkeys.'.format(scope))

    def unregister_hotkeys(self, scope='', force=False):
        """Unregister hotkeys."""
        if not scope:
            for scope in self.hooked_keys:
                self.unregister_hotkeys(scope)
            if force:
                try:
                    keyboard.unhook_all()
                except Exception:
                    pass
            self.keyboard_state = dict()
        else:
            while self.hooked_keys[scope]:
                if scope == 'ctrlx':
                    try:
                        keyboard.remove_hotkey(self.hooked_keys[scope].pop())
                    except ValueError:
                        pass
                else:
                    try:
                        keyboard.unhook(self.hooked_keys[scope].pop())
                    except ValueError:
                        pass

            module_logger.info('Unregistered {} hotkeys.'.format(scope))

    def handle_path(self, path):
        """Check if path repesents a valid scope."""
        paths = path.split('/')[1:]

        for path in paths:
            for scope in self.valid_scopes:
                if re.match(scope, path):
                    return path
        return ''

    def get_primary_scope(self, path):
        """Get the primary scope from the path."""
        if path in self.scopes.keys():
            return path
        for scope in self.valid_scopes:
            if re.match(scope, path):
                return self.scope_regex.sub('', scope)
        return ''

    async def handler(self, websocket, input_path):
        """Handle websocket connetion."""
        try:
            ip = websocket.remote_address[0]
        except Exception:
            ip = '?'
        path = self.handle_path(input_path)
        if not path:
            module_logger.info(
                "Client with incorrect path {}.".format(input_path))
            return
        self.registerConnection(websocket, path)
        module_logger.info(f"Client ({ip}) connected at path {path}!")
        primary_scope = self.get_primary_scope(path)

        if primary_scope not in ['ui_logo', 'logo']:
            self.changeStyle(path, websocket=websocket)

        try:
            self.changeFont(primary_scope, websocket=websocket)
        except ValueError:
            pass

        if primary_scope == 'mapstats':
            self.changeColors(primary_scope, websocket=websocket)
            data = self.__controller.mapstatsManager.getData()
            self.sendData2WS(websocket, "MAPSTATS", data)
        elif primary_scope == 'score':
            data = self.__controller.matchControl.\
                activeMatch().getScoreData()
            self.sendData2WS(websocket, "ALL_DATA", data)
        elif primary_scope in ['mapicons_box', 'mapicons_landscape']:
            self.changePadding(primary_scope, websocket=websocket)
            scope = path.replace('mapicons', 'scope')
            scope = scctool.settings.config.parser.get("MapIcons", scope)
            if not self.__controller.matchControl.\
                    activeMatch().isValidScope(scope):
                scope = 'all'
            data = self.__controller.matchControl.\
                activeMatch().getMapIconsData()
            processedData = dict()
            self.mapicon_sets[path] = set()
            for idx in self.__controller.matchControl.\
                    activeMatch().parseScope(scope):
                processedData[idx + 1] = data[idx + 1]
                self.mapicon_sets[path].add(idx + 1)
            self.sendData2WS(websocket, 'DATA', processedData)
        elif primary_scope == 'vetoes':
            self.changePadding(primary_scope, websocket=websocket)
            data = self.__controller.matchControl.\
                activeMatch().getVetoData()
            self.sendData2WS(websocket, "DATA", data)
        elif primary_scope == 'countdown':
            self.sendData2WS(websocket, "DATA", self.getCountdownData())
        elif path == 'logo_1':
            logo = self.__controller.logoManager.getTeam(
                1,
                self.__controller.matchControl.activeMatchId())
            self.sendData2WS(websocket, 'DATA',
                             {'logo': logo.getFile(True)})
        elif path == 'logo_2':
            logo = self.__controller.logoManager.getTeam(
                2,
                self.__controller.matchControl.activeMatchId())
            self.sendData2WS(websocket, 'DATA',
                             {'logo': logo.getFile(True)})

        while True:
            try:
                msg = await asyncio.wait_for(websocket.recv(), timeout=20)
                if msg == self.intro_state:
                    self.intro_state = ''
                    self.introShown.emit()
                elif msg == 'countdown_started':
                    module_logger.info("Countdown started")
                    self.__controller.textFilesThread.put('cd_start')
                elif msg == 'countdown_finished':
                    module_logger.info("Countdown finished")
                    self.__controller.textFilesThread.put('cd_end')
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
        """Register a connection."""
        if path not in self.connected.keys():
            self.connected[path] = set()
        primary_scope = self.get_primary_scope(path)
        self.scopes[primary_scope].add(path)
        self.connected[path].add(websocket)
        self.socketConnectionChanged.emit(
            len(self.scopes[primary_scope]), primary_scope)
        if primary_scope == 'intro':
            self.register_hotkeys('intro')
        if primary_scope == 'ui_logo':
            pass
            # self.register_hotkeys('ctrlx')

    def unregisterConnection(self, websocket, path):
        """Unregister a connection."""
        if path in self.connected.keys():
            self.connected[path].remove(websocket)
            primary_scope = self.get_primary_scope(path)
            num = len(self.connected[path])
            self.socketConnectionChanged.emit(num, primary_scope)
            if primary_scope == 'intro' and num == 0:
                self.unregister_hotkeys('intro')
            if primary_scope == 'ui_logo' and num == 0:
                pass
                # self.unregister_hotkeys('ctrlx')

    def changeStyle(self, path, style=None, websocket=None):
        """Send a change style command to websockets."""
        primary_scope = self.get_primary_scope(path)
        scope = path
        if primary_scope:
            if style is None:
                try:
                    separate_style = scctool.settings.config.parser.getboolean(
                        "MapIcons",
                        path.replace("mapicons", "separate_style"))
                    if separate_style:
                        style = scctool.settings.config.parser.get(
                            "Style", path)
                    else:
                        style = scctool.settings.config.parser.get(
                            "Style", primary_scope)
                except NoOptionError:
                    style = scctool.settings.config.parser.get(
                        "Style", primary_scope)
            style_file = "src/css/{}/{}.css".format(primary_scope, style)
            if websocket is None:
                self.sendData2Path(path, "CHANGE_STYLE", {'file': style_file})
            else:
                self.sendData2WS(websocket, "CHANGE_STYLE",
                                 {'file': style_file})
        else:
            raise ValueError('Change style is not available for this path.')

    def changePadding(self, path, padding=None, websocket=None):
        """Send a change padding command to websockets."""
        primary_scope = self.get_primary_scope(path)
        if primary_scope in ['mapicons_box', 'mapicons_landscape']:
            setting = primary_scope.replace('mapicons', 'padding')
            padding = scctool.settings.config.parser.getfloat(
                "MapIcons", setting)
            padding = f'{padding}px'
            if websocket is None:
                self.sendData2Path(path, "CHANGE_PADDING",
                                   {'padding': padding})
            else:
                self.sendData2WS(websocket, "CHANGE_PADDING",
                                 {'padding': padding})
        elif primary_scope == 'vetoes':
            padding = scctool.settings.config.parser.getfloat(
                "Vetoes", 'padding')
            padding = f'{padding}px'
            if websocket is None:
                self.sendData2Path(path, "CHANGE_PADDING",
                                   {'padding': padding})
            else:
                self.sendData2WS(websocket, "CHANGE_PADDING",
                                 {'padding': padding})
        else:
            module_logger.info('Path or scope "{}" unknown.'.format(path))

    def changeColors(self, path, colors=None, websocket=None):
        """Send a change colors command to websockets."""
        if path in ['mapstats']:
            if colors is None:
                colors = dict()
                for i in range(1, 3):
                    key = 'color{}'.format(i)
                    colors[key] = scctool.settings.config.parser.get(
                        "Mapstats", key)
            if websocket is None:
                self.sendData2Path(path, "CHANGE_COLORS", colors)
            else:
                self.sendData2WS(websocket, "CHANGE_COLORS", colors)

        else:
            raise ValueError('Change style is not available for this path.')

    def changeFont(self, path=None, font=None, websocket=None):
        """Send a change font command to websockets."""
        valid_paths = ['mapstats', 'score',
                       'mapicons_box', 'mapicons_landscape', 'countdown']
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
            if websocket is None:
                self.sendData2Path(path, "CHANGE_FONT", {'font': font})
            else:
                self.sendData2WS(websocket, "CHANGE_FONT", {'font': font})
        else:
            raise ValueError('Change font is not available for this path.')

    def showIntro(self, idx):
        """Send a show intro command to intro browser sources."""
        self.intro_state = self.sendData2Path(
            "intro", "SHOW_INTRO",
            self.__controller.getPlayerIntroData(idx))

    @classmethod
    def getCountdownData(cls):
        """Pack and return the countdown data from settings."""
        data = {}
        data['static'] = scctool.settings.config.parser.getboolean(
            'Countdown', 'static')
        data['desc'] = scctool.settings.config.parser.get(
            'Countdown', 'description')
        data['restart'] = scctool.settings.config.parser.getboolean(
            'Countdown', 'restart')
        data['datetime'] = scctool.settings.config.parser.get(
            'Countdown', 'datetime')
        data['duration'] = scctool.settings.config.parser.get(
            'Countdown', 'duration')
        data['replacement'] = scctool.settings.config.parser.get(
            'Countdown', 'replacement')
        return data

    def selectMap(self, sc2_map, played=False, vetoed=False):
        """Send select map command to mapstats browser source."""
        self.sendData2Path('mapstats', 'SELECT_MAP', {
                           'map': str(sc2_map),
                           'played': played,
                           'vetoed': vetoed})

    def sendData2Path(self, path, event, input_data=None, state=''):
        """Send a command to all websocket with a specified path."""
        if not state:
            state = str(uuid4())

        if isinstance(path, list):
            for item in path:
                self.sendData2Path(item, event, input_data, state)
            return
        try:
            data = dict()
            data['event'] = event
            data['data'] = input_data
            data['state'] = state

            paths = self.scopes.get(path, [path])

            for path in paths:
                connections = self.connected.get(path, set()).copy()
                for websocket in connections:
                    module_logger.info(
                        "Sending data to '{}': {}".format(path, data))
                    coro = websocket.send(json.dumps(data))
                    asyncio.run_coroutine_threadsafe(coro, self.__loop)
        except Exception:
            module_logger.exception("message")

        return state

    def sendData2WS(self, websocket, event, input_data, state=''):
        """Send data to to a websocket."""
        if not state:
            state = str(uuid4())

        if isinstance(websocket, list):
            for item in websocket:
                self.sendData2WS(item, event, input_data, state)
            return
        try:
            data = dict()
            data['event'] = event
            data['data'] = input_data
            data['state'] = state
            module_logger.info("Sending data: %s" % data)
            coro = websocket.send(json.dumps(data))
            asyncio.run_coroutine_threadsafe(coro, self.__loop)
        except Exception:
            module_logger.exception("message")

        return state

    def compareMapIconSets(self, path):
        """Compare to old set and yield items if different."""
        scope = path.replace('mapicons', 'scope')
        scope = scctool.settings.config.parser.get("MapIcons", scope)
        if not self.__controller.matchControl.\
                activeMatch().isValidScope(scope):
            scope = 'all'
        old_set = self.mapicon_sets.get(path, set())
        new_set = set()
        for idx in self.__controller.matchControl.\
                activeMatch().parseScope(scope):
            new_set.add(idx + 1)

        # This can later be used to animate single items in and out:
        # for idx in (old_set - new_set):
        #     yield idx, True
        #
        # for idx in (new_set - old_set):
        #     yield idx, False

        self.mapicon_sets[path] = new_set

        if old_set != new_set:
            for item in new_set:
                yield item

    async def http_request(self, path, request_headers):
        """Handle http requests."""
        if len(request_headers.get_all('Sec-WebSocket-Key')) > 0:
            return None
        headers = dict()

        file = os.path.join(scctool.settings.casting_html_dir, 'score.html')

        html_dir = scctool.settings.casting_html_dir
        casting_data_dir = scctool.settings.casting_data_dir
        data_dir = scctool.settings.dataDir

        if path in ['/', '']:
            path = "/score.html"

        if path in ['/score', '/logo1', '/logo2', '/aligulac', '']:
            path = f'{path}.html'

        path = path.replace(f'/{html_dir}/', '/./')
        path = path.replace(f'/{html_dir}/', f'/../{html_dir}/')
        path = path.replace(f'/{casting_data_dir}/',
                            f'/../{casting_data_dir}/')
        path = path.replace(f'/{data_dir}/logos/', f'/../{data_dir}/logos/')
        path = path.split('?')[0]

        path = path[1:]
        module_logger.info(f'HTTP request for {path}')
        tts = False

        try:
            if path.endswith(".html"):
                mimetype = 'text/html; charset=utf-8'
            elif path.endswith(".txt"):
                mimetype = 'text/plain; charset=utf-8'
            elif path.endswith(".jpg"):
                mimetype = 'image/jpg'
            elif path.endswith(".jpeg"):
                mimetype = 'image/jpeg'
            elif path.endswith(".svg"):
                mimetype = 'image/svg+xml'
            elif path.endswith(".png"):
                mimetype = 'image/png'
            elif path.endswith(".gif"):
                mimetype = 'image/gif'
            elif path.endswith(".wav"):
                mimetype = 'audio/x-wav'
                tts = True
            elif path.endswith(".mp3"):
                mimetype = 'audio/mpeg'
            elif path.endswith(".js"):
                mimetype = 'application/javascript; charset=utf-8'
            elif path.endswith(".css"):
                mimetype = 'text/css; charset=utf-8'
            elif path.endswith('.otf'):
                mimetype = 'font/opentype'
            else:
                path = f'{path}.html'
                mimetype = 'text/html'

            path = os.path.normpath(path)

            file = scctool.settings.getAbsPath(
                os.path.join(html_dir, path))
            sendReply = os.path.isfile(file)

            if not sendReply:
                file = scctool.settings.getAbsPath(
                    os.path.join(casting_data_dir, path))
                sendReply = os.path.isfile(file)
            if not sendReply and tts:
                file = scctool.settings.getAbsPath(path)
                sendReply = os.path.isfile(file)

            if path.count('..') > 1:
                sendReply = False

            if sendReply:
                # Open the static file requested and send it
                with open(file, 'rb') as f:
                    headers['Content-Type'] = f'{mimetype}'
                    content = f.read()
                    status = http.HTTPStatus.OK
            else:
                status = http.HTTPStatus.INTERNAL_SERVER_ERROR
                content = b'ERROR'
        except Exception:
            status = http.HTTPStatus.NOT_FOUND
            content = b'ERROR'

        return status, headers, content
