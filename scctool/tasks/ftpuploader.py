"""FTP upload via thread."""
import logging

# create logger
module_logger = logging.getLogger('scctool.tasks.ftpuploader')

try:
    import ftplib
    import scctool.settings
    import PyQt5
    import queue
    import base64
    import os
except Exception as e:
    module_logger.exception("message")
    raise


class FTPUploader:
    """Provide FTP uploader."""

    def __init__(self):
        """Init uploader."""
        module_logger.info("Started FTPThread")
        self.__thread = UploaderThread()
        self.__thread.start()

    def connect(self):
        """Connect to FTP server."""
        self.__thread.q.put_nowait(["connect"])
        return self.__thread.progress

    def disconnect(self):
        """Disconnect from FTP server."""
        self.__thread.q.put_nowait(["disconnect"])

    def upload(self, localFile, remoteFile):
        """Upload a file."""
        localFile = scctool.settings.getAbsPath(localFile)
        self.__thread.q.put_nowait(["upload", localFile, remoteFile])

    def cwd(self, d):
        """Change dir."""
        self.__thread.q.put_nowait(["cwd", d])

    def delete(self, d):
        """Delete file."""
        self.__thread.q.put_nowait(["delete", d])

    def mkd(self, d):
        """Create directory."""
        self.__thread.q.put_nowait(["mkd", d])

    def kill(self):
        """Kill thread."""
        module_logger.info("Terminated FTPThread")
        if(self.__thread.isRunning()):
            self.__thread.q.put_nowait(["kill"])

    def progress_start(self):
        """Start progress."""
        self.__thread.q.put_nowait(["progress_start"])

    def progress_end(self):
        """End progress."""
        self.__thread.q.put_nowait(["progress_end"])

    def empty_queque(self):
        """Empty queque."""
        self.__thread.q = queue.Queue()

    def cwdback(self, d):
        """Change dir backwards."""
        dirs = []
        head = d
        while head != '':
            head, tail = os.path.split(head)
            dirs.append("..")

        self.cwd("/".join(dirs))

    def setup(self):
        """Set up directory on server and upload basic files."""
        self.progress_start()
        self.mkd("OBS_data")
        self.mkd("OBS_html")
        self.cwd("OBS_html")
        self.uploadAll('OBS_html')
        self.mkd("src")
        self.cwd("src")
        self.uploadAll('OBS_html/src')
        self.mkd("css")
        self.cwd("css")
        self.uploadAll('OBS_html/src/css')
        self.cwd("../..")
        self.mkd("data")
        self.cwd("..")
        self.mkd("OBS_mapicons")
        self.cwd("OBS_mapicons")
        self.mkd("icons_box")
        self.cwd("icons_box")
        self.mkd("data")
        self.uploadAll('OBS_mapicons/icons_box')
        self.cwd("..")
        self.mkd("icons_landscape")
        self.cwd("icons_landscape")
        self.mkd("data")
        self.uploadAll('OBS_mapicons/icons_landscape')
        self.cwd("..")
        self.mkd("src")
        self.cwd("src")
        self.uploadAll('OBS_mapicons/src')
        self.mkd("css")
        self.cwd("css")
        self.uploadAll('OBS_mapicons/src/css')
        self.cwd("..")
        self.mkd("maps")
        self.cwd("maps")
        self.uploadAll('OBS_mapicons/src/maps')
        self.cwd("..")
        self.mkd("races")
        self.cwd("races")
        self.uploadAll('OBS_mapicons/src/races')
        self.cwd("..")
        self.cwd("../..")
        self.progress_end()

        return self.__thread.progress, 104

    def uploadAll(self, dir):
        """Upload all files in a dir."""
        dir = scctool.settings.getAbsPath(dir)
        for fname in os.listdir(dir):
            full_fname = os.path.join(dir, fname)
            if os.path.isfile(full_fname):
                self.upload(full_fname, fname)


class UploaderThread(PyQt5.QtCore.QThread):
    """Thread for FTP actions."""

    progress = PyQt5.QtCore.pyqtSignal(int)

    def __init__(self):
        """Init thread."""
        PyQt5.QtCore.QThread.__init__(self)
        self.q = queue.Queue()
        self.__ftp = None
        self.__progress = False
        self.__current_cmd = 0

    def run(self):
        """Run thread."""
        retry = False
        while True:
            try:
                if(not retry):
                    cmd, *args = self.q.get(timeout=0.5)
                retry = False

                self.__upload = scctool.settings.config.parser.getboolean(
                    "FTP", "upload")

                if(cmd == "progress_start"):
                    self.__progress = True
                    self.__current_cmd = 0
                    self.progress.emit(0)
                elif(cmd == "progress_end"):
                    module_logger.info("Progress done! " +
                                       str(self.__current_cmd))
                    self.progress.emit(-1)
                    self.__progress = False
                elif(self.__upload and cmd == "connect"):
                    self.__connect()
                elif(self.__upload and cmd == "disconnect"):
                    module_logger.info(self.__ftp.quit())
                elif(self.__upload and cmd == "upload"):
                    localFile, remoteFile, *_ = args
                    f = open(localFile, "rb")
                    module_logger.info(self.__ftp.storbinary(
                        "STOR " + remoteFile.strip(), f))
                    f.close()
                elif(self.__upload and cmd == "delete"):
                    module_logger.info(self.__ftp.delete(args[0]))
                elif(self.__upload and cmd == "cwd"):
                    module_logger.info(self.__ftp.cwd(args[0]))
                elif(self.__upload and cmd == "mkd"):
                    if(not self.directory_exists(args[0])):
                        module_logger.info(self.__ftp.mkd(args[0]))
                elif(cmd == "kill"):
                    module_logger.info("Killing FTP Server!")
                    try:
                        module_logger.info(self.__ftp.quit())
                    except:
                        pass
                    break

                if(self.__progress and not retry):
                    self.__current_cmd += 1
                    self.progress.emit(self.__current_cmd)
                else:
                    self.progress.emit(0)

            except ftplib.error_temp:
                self.__connect()
                retry = True
            except ConnectionAbortedError:
                self.__ftp.quit()
                self.__connect()
                retry = True
            except ftplib.error_perm:
                module_logger.exception("message")
                self.progress.emit(-2)
                self.q = queue.Queue()
                pass
            except queue.Empty:
                self.progress.emit(-3)
            except Exception as e:
                module_logger.exception("message")

        module_logger.info("FTP Thread finished.")

    def __connect(self):
        self.__server = scctool.settings.config.parser.get(
            "FTP", "server").strip()
        self.__user = scctool.settings.config.parser.get("FTP", "user").strip()
        self.__passwd = base64.b64decode(scctool.settings.config.parser.get(
            "FTP", "passwd").strip().encode()).decode("utf8")
        self.__dir = scctool.settings.config.parser.get("FTP", "dir").strip()
        self.__ftp = ftplib.FTP(self.__server)
        module_logger.info(self.__ftp.login(self.__user, self.__passwd))

        if(self.__dir != "" and self.__dir != "."):
            if(not self.directory_exists(self.__dir)):
                module_logger.info(self.__ftp.mkd(self.__dir))
            module_logger.info(self.__ftp.cwd(self.__dir))

    def directory_exists(self, dir):
        """Check if directory exists on server."""
        filelist = []
        self.__ftp.retrlines('LIST', filelist.append)
        return any(f.split()[-1] == dir and f.upper().startswith('D') for f in filelist)
