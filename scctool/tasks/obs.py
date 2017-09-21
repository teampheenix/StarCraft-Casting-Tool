"""Interaction with OBS-Websocket."""
import logging

# create logger
module_logger = logging.getLogger('scctool.tasks.obs')

try:
    import asyncio
    import time
    import base64
    import scctool.settings
    import PyQt5

    import obswsrc
    obswsrc.struct.SKIP_OPTIONAL_CHECK = True
    
    from obswsrc import OBSWS  # pip install obs-ws-rc
    from obswsrc.client import AuthError
    from obswsrc.requests import SetSourceRenderRequest, ResponseStatus
    
except Exception as e:

    module_logger.exception("message")
    raise


def testConnection():
    """Test connection."""
    passwd = base64.b64decode(scctool.settings.config.parser.get(
        "OBS", "passwd").strip().encode()).decode("utf8")
    port = scctool.settings.config.parser.getint("OBS", "port")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(None)
    obsws = OBSWS("localhost", port, passwd, loop=loop)

    try:
        loop.run_until_complete(obsws.connect())
        msg = "Connected!"

    except OSError:
        msg = "{host}:{port} is unreachable. Is OBS Studio with obs-websocket plugin launched?"
        msg = msg.format(host=obsws.host, port=obsws.port)

    except AuthError:
        msg = "Couldn't auth to obs-websocket. Correct password?"

    except Exception as e:
        module_logger.exception("message")
        msg = "Unkown Error!"

    finally:
        loop.close()

    return msg


async def hideIntros(thread):
    """Hide browser sources of playyer intros."""
    passwd = base64.b64decode(scctool.settings.config.parser.get(
        "OBS", "passwd").strip().encode()).decode("utf8")
    port = scctool.settings.config.parser.getint("OBS", "port")

    obsws = OBSWS("localhost", port, passwd)
    try:
        await obsws.connect()
    except Exception as e:
        module_logger.exception("message")
        return

    try:

        while not thread.getKillStatus():
            try:
                event = await asyncio.wait_for(obsws.event(), timeout=3.0)
                if(event is None):
                    break
            except:
                continue

            if(event.type_name == 'SceneItemVisibilityChanged'):
                source_name = event.get('item-name')
                visible = event.get('item-visible')
                sources = list(map(str.strip, str(
                    scctool.settings.config.parser.get("OBS", "sources")).split(',')))
                if(visible and source_name in sources):
                    time.sleep(4.5)
                    response = await obsws.require(SetSourceRenderRequest(
                        source=source_name, render=False))
                    # Check if everything is OK
                    if response.status == ResponseStatus.OK:
                        module_logger.info(
                            "Source " + source_name + " hidden!")
                    else:
                        module_logger.info(
                            "Couldn't hide the source. Reason:", response.error)

    except Exception as e:
        module_logger.exception("message")
    finally:
        await obsws.close()


class WebsocketThread(PyQt5.QtCore.QThread):
    """Thread for websocket interaction."""

    requestCancellation = PyQt5.QtCore.pyqtSignal(int)

    def __init__(self):
        """Init thread."""
        PyQt5.QtCore.QThread.__init__(self)
        self.__kill = False

    def run(self):
        """Run thread."""
        self.__kill = False
        while not self.__kill:
            if(scctool.settings.config.parser.getboolean("OBS", "active")):
                loop = asyncio.new_event_loop()
                loop.run_until_complete(hideIntros(self))
                loop.close()
            time.sleep(5)

        module_logger.info("WebSocketThread finished!")

    def getKillStatus(self):
        """Get kill status."""
        return self.__kill

    def requestKill(self):
        """Request kill of thread."""
        self.__kill = True

    def cancelKillRequest(self):
        """Cancel kill request."""
        self.__kill = False
