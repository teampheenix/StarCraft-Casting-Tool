#!/usr/bin/python
import logging

# create logger
module_logger = logging.getLogger('scctool.ftpuploader')

try:
    from ftplib import FTP
    import scctool.settings
    from PyQt5 import QtCore
    import queue
    import base64
    import os
except Exception as e:
    module_logger.exception("message") 
    raise  
    
class FTPUploader:
    
    def __init__(self):
        self.__upload = bool(scctool.settings.Config.get("FTP","upload"))
        self.__server = scctool.settings.Config.get("FTP","server").strip()
        self.__user   = scctool.settings.Config.get("FTP","user").strip()
        self.__passwd = base64.b64decode(scctool.settings.Config.get("FTP","passwd").strip().encode()).decode("utf8")
        print(self.__passwd)
        self.__thread = UploaderThread()
        
        if(self.__upload):
            module_logger.info("Started FTPThread")
            self.__thread.start()
            self.connect()
           #self.createFileStructure()
        
    def connect(self):
        if(self.__upload):
            self.__thread.q.put_nowait(["connect", self.__server, self.__user, self.__passwd])
        
    def upload(self, localFile, remoteFile):
        if(self.__upload):
            self.__thread.q.put_nowait(["upload",localFile, remoteFile])

    def cwd(self, d):
        if(self.__upload):
            self.__thread.q.put_nowait(["cwd",d])
            
    def mkd(self, d):
        if(self.__upload):
            self.__thread.q.put_nowait(["mkd",d])        
            
    def kill(self):
        module_logger.info("Terminated FTPThread")
        if(self.__thread.isRunning()):
            self.__thread.q.put_nowait(["kill"])
            
    def createFileStructure(self):
        self.mkd("OBS_data")
        
        self.mkd("OBS_html")
        self.cwd("OBS_html")
        self.uploadAll('OBS_html')
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
        
    def uploadAll(self, dir):
        for fname in os.listdir(dir):
            full_fname = os.path.join(dir, fname)
            if os.path.isfile(full_fname):
                self.upload(full_fname, fname)

            
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
                    module_logger.info(self.__ftp.login(work[2], work[3]))
                if(cmd == "upload"):
                    localFile = work[1]
                    remoteFile = work[2]
                    print("Upload request for "+localFile)
                    f = open(localFile, "rb") 
                    module_logger.info(self.__ftp.storbinary("STOR "+remoteFile.strip(), f))
                    f.close()
                elif(cmd == "cwd"):
                    print("Cwd "+work[1])
                    module_logger.info(self.__ftp.cwd(work[1]))
                elif(cmd == "mkd"):
                    print("Mkd "+work[1])
                    if(not self.directory_exists(work[1])):
                        print("Already existing "+work[1])
                        module_logger.info(self.__ftp.mkd(work[1]))
                elif(cmd == "kill"):
                    module_logger.info(self.__ftp.quit())
                    break
            except queue.Empty:
                pass
            except Exception as e:
                module_logger.exception("message")   
                
        print("FTP Thread finished.")
        
    def directory_exists(self, dir):
        filelist = []
        self.__ftp.retrlines('LIST',filelist.append)
        return any(f.split()[-1] == dir and f.upper().startswith('D') for f in filelist)
    