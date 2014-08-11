'''
Created on May 1, 2014

@author: Kei
'''

from PyQt4 import QtCore
from mineline.LineLog import LineLog

class FileLoader(QtCore.QThread):
    '''
    This class is used in conjunction with loading log files. Due to the size of some logs and the time required
    for processing them, it is necessary to Thread the loading process to avoid locking up the main thread UI.
    
    Ideally there should be an interface-like inheritance to maintain conformity to LineLog call signs
    '''
    

    def __init__(self, finishCallback):
        super(FileLoader, self).__init__()
        
        self.fromfile_pack = None
        self.fromstring_pack = None
        self.frompickle_pack = None
        
        self.finishCallback = finishCallback
    
    def run(self):
        if self.fromfile_pack:
            self.linelog = LineLog.fromFilename(self.fromfile_pack['filepath'],
                                                 self.fromfile_pack['savedTimeZone'],
                                                 self.fromfile_pack['progressCallback'])
            print "Log import complete"
        elif self.fromstring_pack:
            self.linelog = LineLog.fromString(self.fromstring_pack['unprocessed_str'],
                                              self.fromstring_pack['savedTimeZone'],
                                              self.fromstring_pack['progressCallback'])
        elif self.frompickle_pack:
            self.linelog = LineLog.fromPickle(self.frompickle_pack['dataFilePath'])
        
    def getLineLog(self):
        if not self.isFinished():
            return None
        else:
            return self.linelog
    
    @classmethod
    def fromFilename(cls, filepath, savedTimeZone, finishCallback, progressCallback=None):
        thread = cls(finishCallback)
        thread.finishCallback = finishCallback
        thread.fromfile_pack = {'filepath': filepath,
                                'savedTimeZone': savedTimeZone,
                                'progressCallback': progressCallback}
        return thread
    @classmethod
    def fromString(cls, unprocessed_str, savedTimeZone, finishCallback, progressCallback=None):
#         thread = cls(finishCallback)
        cls.fromstring_pack = {'unprocessed_str': unprocessed_str,
                                  'savedTimeZone': savedTimeZone,
                                  'progressCallback': progressCallback}
#         return thread
    
    def fromPickle(self, dataFilePath, finishCallback):
#         thread = cls(finishCallback)
        self.frompickle_pack = {'dataFilePath': dataFilePath}
#         return thread