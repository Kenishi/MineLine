'''
Created on May 1, 2014

@author: Kei
'''

from PyQt4 import QtGui
from PyQt4.QtCore import Qt
from PyQt4 import QtCore



class LoadingDialog(QtGui.QDialog):
    '''
    A loading frame with a label and progress bar
    '''

    instance = None
    onUpdate = QtCore.pyqtSignal('QString', int, int, name='update')
        
    @classmethod
    def getLoadingDialog(cls, parent=None):
        if not cls.instance:
            cls.instance = cls()
            super(LoadingDialog, cls.instance).__init__(parent)
            
            grid = QtGui.QGridLayout(cls.instance)
            
            # Info label
            cls.instance.__infoLabel = QtGui.QLabel("")
            cls.instance.__infoLabel.setAlignment(Qt.AlignHCenter)
            grid.addWidget(cls.instance.__infoLabel, 0, 0, 1, 1)
            
            # Progress bar
            cls.instance.__bar = QtGui.QProgressBar()
            grid.addWidget(cls.instance.__bar, 1, 0, 1, 1)
            
            cls.instance.setLayout(grid)
            cls.instance.setWindowTitle("Progress")
            cls.instance.show()
            cls.instance.setVisible(False)
            cls.instance.onUpdate.connect(cls.instance._update, type=Qt.DirectConnection)

        return cls.instance
    
    def update(self, msg, cur, finish):
        self.onUpdate.emit(msg, cur, finish)
        
        pass
    
    def _update(self, msg, cur, finish):
        if cur >= finish:
            self.finish()
            return
        
        if not self.instance.isVisible():
            self.setVisible(True)
        self.__infoLabel.setText(msg)
        self.__bar.setMaximum(finish)
        self.__bar.setValue(cur)
    
    def finish(self):
        self.setVisible(False)
    
        