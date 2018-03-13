"""Interaction with Browser Source via Websocket."""
import logging

# create logger
module_logger = logging.getLogger('scctool.tasks.websocket')

try:
    import asyncio
    import websockets
    import json
    import keyboard
    import scctool.settings
    import PyQt5

except Exception as e:

    module_logger.exception("message")
    raise


def convert_hotkey(input_str):
    try:
        input_str = str(input_str)
        raw_hex = int(input_str, 16)
        hex_data = hex(raw_hex)
        if str(hex_data).lower() == input_str.lower():
            return raw_hex
    except Exception:
        pass
    return input_str


class WebsocketThread(PyQt5.QtCore.QThread):
    """Thread for websocket interaction."""

    def __init__(self, controller):
        """Init thread."""
        PyQt5.QtCore.QThread.__init__(self)
        self.connected = set()
        self.__loop = None
        self.__controller = controller

    def run(self):
        """Run thread."""
        module_logger.info("WebSocketThread starting!")
        self.connected = set()
        self.__loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.__loop)

        # Create the server.
        start_server = websockets.serve(self.handler, host='localhost', port=4489,
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

    def register_hotkeys(self):
        key = convert_hotkey(scctool.settings.config.parser.get(
            "Intros", "hotkey_player1").strip())
        if key:
            keyboard.add_hotkey(key, self.showIntro, args=[
                0], trigger_on_release=True)

        key = convert_hotkey(scctool.settings.config.parser.get(
            "Intros", "hotkey_player2").strip())
        if key:
            keyboard.add_hotkey(key, self.showIntro, args=[
                1], trigger_on_release=True)

        key = convert_hotkey(scctool.settings.config.parser.get(
            "Intros", "hotkey_debug").strip())
        if key:
            keyboard.add_hotkey(key, self.sendData, args=[
                "DEBUG_MODE", dict()], trigger_on_release=True)

    def unregister_hotkeys(self):
        keyboard.unhook_all()

    async def handler(self, websocket, path):
        if path not in ['/intro']:
            module_logger.info("Client with incorrect path.")
            return
        self.connected.add(websocket)
        module_logger.info("Client connected!")
        self.changeStyle()
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
        self.connected.remove(websocket)

    def changeStyle(self, style=None):
        if style is None:
            style = scctool.settings.config.parser.get("Style", "intro")
        style_file = "src/css/intro/" + style + ".css"
        self.sendData("CHANGE_STYLE", {'file': style_file})

    def showIntro(self, idx):
        self.sendData("SHOW_INTRO", self.__controller.getPlayerIntroData(idx))

    def sendData(self, event, input_data):
        data = dict()
        data['event'] = event
        data['data'] = input_data
        for websocket in self.connected.copy():
            module_logger.info("Sending data: %s" % data)
            coro = websocket.send(json.dumps(data))
            asyncio.run_coroutine_threadsafe(coro, self.__loop)
