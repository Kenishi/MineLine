'''
Created on Apr 28, 2014

@author: Kei

The GUI for easily working with the MineLine package
'''

import sys
from PyQt4 import QtGui
from PyQt4.QtCore import Qt, QDir
from PyQt4.Qt import QSizePolicy
from PyQt4.QtGui import QFormLayout, QStackedLayout

from mineline.gui.NoFileFrame import NoFileFrame
from mineline.gui.TimeZoneDialog import TimeZoneDialog
from mineline.gui.LoadingDialog import LoadingDialog
from mineline.gui.CommandFrame import CommandFrame
from mineline.gui.FileLoader import FileLoader

from mineline.LineLog import LineLog
from mineline.LineLogDB import LineLogDB



class MineLine(QtGui.QMainWindow):
    
    def __init__(self):
        super(MineLine, self).__init__()
        
        self.initUI()
        
    def initUI(self):
        
        self.initMenuBar()
        self.initFrameStack()
        
        self.showNoFileFrame()
        
        self.setGeometry(300, 300, 400, 300)
        self.setWindowTitle("MineLine")
        self.show()
    
    def initMenuBar(self):
        
        load_Action = QtGui.QAction("Load Chat Log", self)
        load_Action.setToolTip("Load from a chat log")
        load_Action.triggered.connect(self.onLoadChatLog)
        
        openDB_Action = QtGui.QAction("Open Chat DB", self)
        openDB_Action.setToolTip("Open Chat DB")
        openDB_Action.triggered.connect(self.onOpenDB)
        
        exit_Action = QtGui.QAction("Quit", self)
        exit_Action.setToolTip("Quit Application")
        exit_Action.triggered.connect(QtGui.qApp.quit)
    
        menubar = self.menuBar()
        filemenu = menubar.addMenu('&File')
        filemenu.addAction(load_Action)
        filemenu.addAction(openDB_Action)
        filemenu.addAction(exit_Action)
        
    
    def initFrameStack(self):
        # Put the "initial" start message up and center it in the frame
        centralWindow = QtGui.QStackedWidget(self)
        
        # Startup Frame
        self.__nofileframe = NoFileFrame(self)
        
        # Commands Frame
        self.__commandframe = CommandFrame(self)
        
        # Add Frames to Stack
        centralWindow.addWidget(self.__nofileframe)
        centralWindow.addWidget(self.__commandframe)
        
        self.setCentralWidget(centralWindow)
        pass
    
    def showNoFileFrame(self):
        self.centralWidget().setCurrentWidget(self.__nofileframe)
        
    def showCommandFrame(self):
        self.centralWidget().setCurrentWidget(self.__commandframe)
    
    def onLoadChatLog(self):
        # Get filepath from user
        result = self.__askForFilePath()
        if result:
            filepath, file_filter = result
        else:
            return # Abort
        
        savedTimeZone = self.__askForSavedTimeZone()
        if not savedTimeZone:
            return # Abort
        
        # Create LineLog using FileLoader thread
        self.__importLogText(filepath, savedTimeZone)
        
        pass
    
    def onOpenDB(self):
        print "Open DB"
        pass
    
    def onFinishedLoading(self):
        '''
        Called when the FileLoader finishes load/processing a log file
        '''
        self.linelog = self.__loaderthread.getLineLog()
        self.__loaderthread = None # Cleanup
        
        self.__askForConversion2DB()
        self.showCommandFrame()
                
    def __askForFilePath(self):
        filepath, file_filter = QtGui.QFileDialog.getOpenFileNameAndFilter(parent=self,
                                                   caption="Load Chat Log",
                                                   directory=QDir.homePath(),
                                                   filter='Text files (*.txt *.log);;All files (*)',
                                                   options=QtGui.QFileDialog.ReadOnly)
        return (filepath, file_filter)
    
    def __askForSavedTimeZone(self):
        '''
        Private method called during the loading of an unprocessed text log file.
        
        This function will show the timezone selector dialog and return the tzinfo
        '''
        tzDiag = TimeZoneDialog(self)
        val = tzDiag.exec_()
        
        if val == QtGui.QDialog.Accepted:
            return tzDiag.getValue()
        else: # Abort
            return None
        
    def __importLogText(self, filepath, savedTimeZone):
        '''
        Private method called during the loading of an unprocessed text log file.
        
        This function will create a FileLoader thread and start processing.
        '''
        
        self.__loaderthread = FileLoader.fromFilename(filepath,
                                         savedTimeZone,
                                         self.onFinishedLoading,
                                         LoadingDialog.getLoadingDialog(self))
        self.__loaderthread.finished.connect(self.onFinishedLoading)
        self.__loaderthread.start()        
    
    def __askForConversion2DB(self):
        # BUG: Call MsgBox will cause an error in console about "modalSession has been exited prematurely"
        # Ask if user wants to convert to faster SQL DB
        response = QtGui.QMessageBox.question(self,
                                              "Convert to SQL DB?",
                                              "Log Successfully processed.\nWould you like to build a SQL DB to make analysis faster?",
                                              QtGui.QMessageBox.Yes|QtGui.QMessageBox.No,
                                              QtGui.QMessageBox.No)
        if response == QtGui.QMessageBox.Yes:
            filepath = self.__askForDBSavePath()
            if filepath:
                self.linelog_db = LineLogDB(str(filepath))
                
                def finishConvert():
                    self.linelog = self.linelog_db
                    self.showCommandFrame()

                self.linelog_db.addLineLog(self.linelog, LoadingDialog.getLoadingDialog(self), finishConvert)
    
    def __askForDBSavePath(self):
        filepath = QtGui.QFileDialog.getSaveFileName(parent=self,
                                                     caption="Save DB to...",
                                                     directory=QDir.homePath(),
                                                     filter="SQL DB (*.db)")
        return filepath
    
def main():
    
    app = QtGui.QApplication(sys.argv)
    mineline = MineLine()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
    pass