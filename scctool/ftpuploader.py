#!/usr/bin/python
import logging

# create logger
module_logger = logging.getLogger('scctool.ftpuploader')

try:
    from ftplib import FTP
    import scctool.settings
    from PyQt5 import QtCore
    import queue
except Exception as e:
    module_logger.exception("message") 
    raise  
    
class FTPUploader:
    
    def __init__(self):
        self.__upload = bool(scctool.settings.Config.get("FTP","upload"))
        self.__server = scctool.settings.Config.get("FTP","server").strip()
        self.__user   = scctool.settings.Config.get("FTP","user").strip()
        self.__passwd = scctool.settings.Config.get("FTP","passwd").strip()
        self.__thread = UploaderThread()
        
        if(self.__upload):
            self.__thread.start()
            self.connect()
            self.cwd("OBS_mapicons")
        
    def connect(self):
        if(self.__upload):
            self.__thread.q.put_nowait(["connect", self.__server, self.__user, self.__passwd])
        
    def upload(self, localFile, remoteFile):
        if(self.__upload):
            self.__thread.q.put_nowait(["upload",localFile, remoteFile])

    def cwd(self, d):
        if(self.__upload):
            self.__thread.q.put_nowait(["cwd",d])
            
        
    def kill(self):
        if(self.__thread.isRunning()):
            self.__thread.q.put_nowait(["kill"])
            
class UploaderThread(QtCore.QThread):
    
    def __init__(self):
        QtCore.QThread.__init__(self)
        self.q = queue.Queue()
        self.__ftp = None

    def run(self):
        while True:
            try:
                work = self.q.get(timeout=3)  
                cmd = work[0]
                if(cmd == "connect"):
                    self.__ftp = FTP(work[1])
                    self.__ftp.login(work[2], work[3])
                if(cmd == "upload"):
                    localFile = work[1]
                    remoteFile = work[2]
                    f = open(localFile, "rb") 
                    self.__ftp.storbinary("STOR "+remoteFile.strip(), f) 
                    f.close()
                elif(cmd == "cwd"):
                    self.__ftp.cwd(work[1])
                elif(cmd == "kill"):
                    self.__ftp.quit()
                    break
            except queue.Empty:
                pass
            except Exception as e:
                module_logger.exception("message")   
                
        print("FTP Thread finished.")
        

    