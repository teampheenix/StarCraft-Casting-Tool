"""Hosts browser sources in the local network."""
import http.server
import logging
import threading
import os
import urllib.parse
from uuid import uuid4

from PyQt5 import QtCore

import scctool.settings

module_logger = logging.getLogger(__name__)


class myHandler(http.server.SimpleHTTPRequestHandler):

    # Handler for the GET requests
    def do_GET(self):
        print(self.path)

        if not self.path:
            self.path = "score.html"

        self.path = self.path.replace('/' + scctool.settings.casting_html_dir + '/', '/./')
        self.path = self.path.replace('/' + scctool.settings.casting_data_dir + '/',
                                      '/../'+scctool.settings.casting_data_dir+'/')
        self.path = self.path.replace('/' + scctool.settings.dataDir + '/',
                                      '/../'+scctool.settings.dataDir+'/')

        self.path = self.path[1:]
        print(self.path, self.requestline)

        file = scctool.settings.getAbsPath(
            os.path.join(scctool.settings.casting_html_dir,
                         self.path))
        try:
            sendReply = False
            if self.path.endswith(".html"):
                mimetype = 'text/html'
                sendReply = True
            if self.path.endswith(".jpg"):
                mimetype = 'image/jpg'
                sendReply = True
            if self.path.endswith(".png"):
                mimetype = 'image/png'
                sendReply = True
            if self.path.endswith(".gif"):
                mimetype = 'image/gif'
                sendReply = True
            if self.path.endswith(".js"):
                mimetype = 'application/javascript'
                sendReply = True
            if self.path.endswith(".css"):
                mimetype = 'text/css'
                sendReply = True

            if sendReply == True:
                # Open the static file requested and send it
                with open(file, 'rb') as f:
                    self.send_response(200)
                    self.send_header('Content-type', mimetype)
                    self.end_headers()
                    self.wfile.write(f.read())
            else:
                self.send_error(404, 'Invalid format')
        except Exception:
            msg = 'File Not Found: {}'.format(file)
            module_logger.info(msg)
            self.send_error(404, msg)


class LocalhostThread(http.server.HTTPServer, QtCore.QThread):
    """Define thread for flask."""

    def __init__(self):
        """Init thread."""
        QtCore.QThread.__init__(self)
        http.server.HTTPServer.__init__(self, ('', 8080), myHandler)

    def __del__(self):
        """Delete thread."""
        self.terminate()

    def terminate(self):
        if self.isRunning():
            assassin = threading.Thread(target=self.shutdown)
            assassin.daemon = True
            assassin.start()
            self.server_close()

    def run(self):
        """Run thread."""
        module_logger.info("AuthThread started")
        try:
            self.serve_forever()
        except OSError as e:
            pass
        finally:
            module_logger.info("AuthThread done")

    def server_bind(self):
        http.server.HTTPServer.server_bind(self)
        self.socket.setsockopt(http.server.socket.SOL_SOCKET,
                               http.server.socket.SO_REUSEADDR, 1)
