"""Request auth tokens from twitch and nightbot."""
import http.server
import logging
import threading
import urllib.parse
import webbrowser
from uuid import uuid4

from PyQt5 import QtCore

import scctool.settings.translation
from scctool.settings import getResFile, safe


module_logger = logging.getLogger(__name__)
_ = scctool.settings.translation.gettext

NIGHTBOT_REDIRECT_URI = "http://localhost:65010/nightbot_callback"

TWITCH_REDIRECT_URI = "http://localhost:65010/twitch_callback"


class myHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP handle for oauth."""

    # Handler for the GET requests
    def do_GET(self):
        """Handle GET request."""
        if self.path in ['/nightbot', '/twitch']:
            js_response = ('<script type="text/javascript">'
                           'window.location = "{}";'
                           '</script>')
            state = str(uuid4())
            scope = self.path.replace('/', '')
            url = getattr(self, f'get_auth_url_{scope}')(state)
            self.send_content(js_response.format(url))
        if self.path in ['/nightbot_callback', '/twitch_callback']:
            js_response = ('<script type="text/javascript">'
                           ' var token = window.location.href.split("#")[1];'
                           ' window.location = "{}_token?" + token;</script>')
            self.send_content(js_response.format(self.path))
        elif self.path.split('?')[0] in ['/nightbot_callback_token',
                                         '/twitch_callback_token']:
            content = _("Succesfully recived access"
                        " to {} - you can close this tab now.")
            if self.path.split('?')[0] == '/twitch_callback_token':
                scope = 'twitch'
            else:
                scope = 'nightbot'
            content = content.format(scope.capitalize())

            with open(getResFile("auth.html"), 'r') as html_file:
                success_html = html_file.read()

            content = success_html.replace('#CONTENT#', content)
            self.send_content(content)
            par = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            self.server.emit_token(scope, par.get('access_token', [''])[0])
        else:
            try:
                self.send_error(404, "File not found")
            except (ConnectionAbortedError, ConnectionResetError):
                pass

    def log_message(self, format, *args):
        """Log a message."""
        pass

    def send_content(self, response):
        """Send content."""
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.send_header("Content-length", len(response))
        self.end_headers()
        self.wfile.write(response.encode('utf-8'))

    @classmethod
    def get_auth_url_nightbot(cls, state):
        """Generate auth url for nightbot."""
        # Generate a random string for the state parameter
        # Save it for use later to prevent xsrf attacks
        params = {"client_id": safe.get('nightbot-client-id'),
                  "response_type": "token",
                  "state": state,
                  "redirect_uri": NIGHTBOT_REDIRECT_URI,
                  "scope": "commands"}
        url = "https://api.nightbot.tv/oauth2/authorize?" + \
            urllib.parse.urlencode(params)
        return url

    @classmethod
    def get_auth_url_twitch(cls, state):
        """Generate auth url for twitch."""
        # Generate a random string for the state parameter
        # Save it for use later to prevent xsrf attacks
        params = {"client_id": safe.get('twitch-client-id'),
                  "response_type": "token",
                  "state": state,
                  "redirect_uri": TWITCH_REDIRECT_URI,
                  "scope": "user:edit:broadcast"}
        url = "https://id.twitch.tv/oauth2/authorize?" + \
            urllib.parse.urlencode(params)
        return url


class AuthThread(http.server.HTTPServer, QtCore.QThread):
    """Define thread for flask."""

    tokenRecived = QtCore.pyqtSignal(str, str)
    pending_requests = set()
    allow_reuse_address = True

    def __init__(self):
        """Init thread."""
        QtCore.QThread.__init__(self)
        http.server.HTTPServer.__init__(
            self, ('', 65010), myHandler)

    def __del__(self):
        """Delete thread."""
        self.terminate()

    def terminate(self):
        """Terminate thread."""
        if self.isRunning():
            assassin = threading.Thread(target=self.shutdown)
            assassin.daemon = True
            assassin.start()
            self.server_close()

    def emit_token(self, scope, token):
        """Emit signal that a new token was recived."""
        self.pending_requests.remove(scope)
        if len(self.pending_requests) == 0:
            assassin = threading.Thread(target=self.shutdown)
            assassin.daemon = True
            assassin.start()
        self.tokenRecived.emit(scope, token)

    def run(self):
        """Run thread."""
        module_logger.info("AuthThread started")
        try:
            self.serve_forever()
        except OSError:
            self.server_close()
        finally:
            module_logger.info("AuthThread done")

    def requestToken(self, scope):
        """Request oauth for a new token."""
        if scope not in ['twitch', 'nightbot']:
            return

        if not self.isRunning():
            self.start()
        self.pending_requests.add(scope)

        webbrowser.open("http://localhost:65010/{}".format(scope))

    def server_bind(self):
        self.socket.setsockopt(http.server.socket.SOL_SOCKET,
                               http.server.socket.SO_REUSEADDR, 1)
        http.server.HTTPServer.server_bind(self)
