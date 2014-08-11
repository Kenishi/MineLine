'''
Created on May 1, 2014

@author: Kei
'''

from PyQt4 import QtGui

class CommandFrame(QtGui.QFrame):
    '''
    The command frame will hold the interface for running analysis.
    
    Currently just a bunch of buttons that will make a message dialog pop up with results
    '''

    def __init__(self, parent):
        super(CommandFrame, self).__init__(parent)
        
        self.parent = parent
        
        grid = QtGui.QGridLayout()
        
        countEventsButton = QtGui.QPushButton("Count Events")
        countEventsButton.clicked.connect(self.onCountEvents)
        grid.addWidget(countEventsButton, 0, 0, 1, 1)
        
        self.setLayout(grid)
    
    def onCountEvents(self):
        print self.parent.linelog.getEventCount()