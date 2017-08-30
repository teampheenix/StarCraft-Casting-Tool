#!/usr/bin/python
import logging

# create logger
module_logger = logging.getLogger('scctool.ftpuploader')

try:
    import ftplib
    import scctool.settings
    from PyQt5 import QtCore
    import queue
    import base64
    import time
    import os
except Exception as e:
    module_logger.exception("message") 
    raise  
    
class FTPUploader:
    
    def __init__(self):

        module_logger.info("Started FTPThread")
        self.__thread = UploaderThread()
        self.__thread.start()

        
    def connect(self):
        self.__thread.q.put_nowait(["connect"])
        return self.__thread.progress
        
    def disconnect(self):
        self.__thread.q.put_nowait(["disconnect"])
        
    def upload(self, localFile, remoteFile):
        self.__thread.q.put_nowait(["upload",localFile, remoteFile])

    def cwd(self, d):
        self.__thread.q.put_nowait(["cwd",d])
            
    def mkd(self, d):
        self.__thread.q.put_nowait(["mkd",d])        
            
    def kill(self):
        module_logger.info("Terminated FTPThread")
        if(self.__thread.isRunning()):
            self.__thread.q.put_nowait(["kill"])
            
    def progress_start(self):
        self.__thread.q.put_nowait(["progress_start"])
        
    def progress_end(self):
        self.__thread.q.put_nowait(["progress_end"])
        
    def empty_queque(self):
        self.__thread.q = queue.Queue()
            
    def setup(self):
        self.progress_start()
        self.mkd("OBS_data")
        self.mkd("OBS_html")
        self.cwd("OBS_html")
        self.uploadAll('OBS_html')
        self.mkd("src")
        self.cwd("src")
        self.uploadAll('OBS_html/src')
        self.cwd("..")
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
        
        return self.__thread.progress, 88
        
    def uploadAll(self, dir):
        for fname in os.listdir(dir):
            full_fname = os.path.join(dir, fname)
            if os.path.isfile(full_fname):
                self.upload(full_fname, fname)

            
class UploaderThread(QtCore.QThread):
    
    progress = QtCore.pyqtSignal(int)
    
    def __init__(self):
        QtCore.QThread.__init__(self)
        self.q = queue.Queue()
        self.__ftp = None
        self.__progress = False
        self.__current_cmd = 0

    def run(self):
        retry = False
        while True:
            try:
                if(not retry):
                    work = self.q.get(timeout=0.5)  
                retry = False
                
                cmd = work[0]
                self.__upload = scctool.settings.Config.getboolean("FTP","upload")
                
                if(cmd == "progress_start"):
                    self.__progress = True
                    self.__current_cmd = 0
                    self.progress.emit(0)
                elif(cmd == "progress_end"):
                    print("Progress done!")
                    self.progress.emit(-1)
                    self.__progress = False
                elif(self.__upload and cmd == "connect"):
                    self.__connect()
                elif(self.__upload and cmd == "disconnect"):   
                    module_logger.info(self.__ftp.quit())
                elif(self.__upload and cmd == "upload"):
                    localFile = work[1]
                    remoteFile = work[2]
                    print("Upload request for "+localFile)
                    f = open(localFile, "rb") 
                    module_logger.info(self.__ftp.storbinary("STOR "+remoteFile.strip(), f))
                    f.close()
                elif(self.__upload and cmd == "cwd"):
                    print("Cwd "+work[1])
                    module_logger.info(self.__ftp.cwd(work[1]))
                elif(self.__upload and cmd == "mkd"):
                    print("Mkd "+work[1])
                    if(not self.directory_exists(work[1])):
                        print("Already existing "+work[1])
                        module_logger.info(self.__ftp.mkd(work[1]))
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
            except ftplib.error_perm:
                module_logger.exception("message") 
                self.progress.emit(-2)
                self.q = queue.Queue()
                pass
            except queue.Empty:
                self.progress.emit(-3)
            except Exception as e:
                module_logger.exception("message")   

        print("FTP Thread finished.")
        
    def __connect(self):
        self.__server = scctool.settings.Config.get("FTP","server").strip()
        self.__user   = scctool.settings.Config.get("FTP","user").strip()
        self.__passwd = base64.b64decode(scctool.settings.Config.get("FTP","passwd").strip().encode()).decode("utf8")
        self.__dir    = scctool.settings.Config.get("FTP","dir").strip()
        self.__ftp = ftplib.FTP(self.__server)
        module_logger.info(self.__ftp.login(self.__user, self.__passwd))
        
        if(self.__dir != "" and self.__dir != "."):
            if(not self.directory_exists(self.__dir)):
                module_logger.info(self.__ftp.mkd(self.__dir))
            module_logger.info(self.__ftp.cwd(self.__dir))
        
    def directory_exists(self, dir):
        filelist = []
        self.__ftp.retrlines('LIST',filelist.append)
        return any(f.split()[-1] == dir and f.upper().startswith('D') for f in filelist)
    
