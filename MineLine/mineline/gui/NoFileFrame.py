'''
Created on Apr 30, 2014

@author: Kei
'''

from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import QLayout

class NoFileFrame(QtGui.QFrame):
    '''
    The frame that is used when there is no file or database loaded
    
    Creates a Horizontal and Vertical Layout to center the label in frame
    '''
    
    def __init__(self, parent):
        super(NoFileFrame, self).__init__()
        self.parent = parent
        
        label = QtGui.QLabel("""No file loaded. <a href="open">Open a DB</a> or <a href="load">Load a chat log</a>.""", self)
        label.setSizePolicy(QtGui.QSizePolicy.Minimum,
                            QtGui.QSizePolicy.Minimum)
        label.setAlignment(QtCore.Qt.AlignCenter)
        
        # Setup interactive links
        label.setTextFormat(QtCore.Qt.RichText)
        label.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse)
        label.linkActivated.connect(self.onLinkClick)
        
        hbox = QtGui.QHBoxLayout()
        hbox.setSizeConstraint(QLayout.SetNoConstraint)
        hbox.addWidget(label)
        
        vbox = QtGui.QVBoxLayout()
        vbox.setSizeConstraint(QLayout.SetNoConstraint)
        vbox.addLayout(hbox)
        
        self.setLayout(vbox)
        
    def onLinkClick(self, link):
        '''
        Fired when one of the links in the label is clicked.
        
        Function will call the parent for onOopenDB() or onLoadChatLog() respectively
        '''
        if link == "open":
            self.parent.onOpenDB()
        elif link == "load":
            self.parent.onLoadChatLog()
        else:
            raise Exception("NoFileFrame: Unknown link fired")