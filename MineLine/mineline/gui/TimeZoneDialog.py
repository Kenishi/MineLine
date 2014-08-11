'''
Created on May 1, 2014

@author: Kei
'''

import pytz
from datetime import datetime
from PyQt4 import QtGui, QtCore

class TimeZoneDialog(QtGui.QDialog):
    '''
    Dialog for asking what time zone a log was saved in
    '''
    
    def __init__(self, parent):
        super(TimeZoneDialog, self).__init__(parent=parent)
        
        # Build the sorted timezone list
        timezones = self.__buildTZList()
        
        # Layouts
        grid = QtGui.QGridLayout(self)
        
        # Create info lael
        label = QtGui.QLabel("Select the time zone the log was saved in")
        grid.addWidget(label, 0, 0, 1, 2)
        
        # Create search helper
        search = QtGui.QLineEdit()
        search.setPlaceholderText("Try a Region or City name")
        search.textChanged.connect(self.onSearchChange)
        grid.addWidget(search, 1, 0, 1, 2)
        
        # Create list
        listBox = QtGui.QListWidget(self)
        listBox.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        listBox.itemDoubleClicked.connect(self.onOkClicked)
        for zone in timezones:
            listBox.addItem(TimeZoneItem(zone, listBox))
        grid.addWidget(listBox, 2, 0, 1, 2)
        self.listBox = listBox
        
        # Add buttons
        okButton = QtGui.QPushButton("Ok")
        okButton.clicked.connect(self.onOkClicked)
        grid.addWidget(okButton, 3, 0, 1, 1)
        
        cancelButton = QtGui.QPushButton("Cancel")
        cancelButton.clicked.connect(self.reject)
        grid.addWidget(cancelButton, 3, 1, 1, 1)
        
        self.setLayout(grid)
        self.setWindowTitle("Select save timezone")
        self.selected = None    
        self.show()
    
    def onOkClicked(self):
        self.selected = self.listBox.currentItem()
        self.accept()
        
    def onSearchChange(self, txt):
        # Perform search if query is not empty
        if txt == "":
            items = None
        else:
            items = self.listBox.findItems(txt, QtCore.Qt.MatchContains)
        
        # Show items
        self.showItems(items)
        pass
    
    def showItems(self, items):
        for i in range(self.listBox.count()):
            listItem = self.listBox.item(i)
            if items:
                if listItem in items:
                    self.listBox.setItemHidden(listItem, False)
                else:
                    self.listBox.setItemHidden(listItem, True)
            else: # Show All
                self.listBox.setItemHidden(listItem, False)
    
    def getValue(self):
        return self.selected.getTzInfo()
    
    def __buildTZList(self):
        '''
        Return a list of tuples with GMT offests and location names
        '''
        neg = list()
        pos = list()
        zero = list()
        
        common = pytz.common_timezones
        for zone in common:
            name = zone
            offset = datetime.now(pytz.timezone(name)).strftime("%z") # Offset is a 'str'
            
            # Sort into correct list
            if int(offset) > 0:
                pos.append((name, offset))
            elif int(offset) < 0:
                neg.append((name, offset))
            else:
                zero.append((name, offset))
        
        # Sort the lists. Neg in reverse, Pos normal
        neg.sort(cmp=lambda x,y:cmp(x[1],y[1]),reverse=True)
        pos.sort(cmp=lambda x,y:cmp(x[1],y[1]))
        
        # Put it together
        output = neg + zero + pos
        
        return output

class TimeZoneItem(QtGui.QListWidgetItem):
    
    def __init__(self, zone, parent=None):
        super(TimeZoneItem, self).__init__(parent=parent)
        
        self.name, self.offset = zone
        
        self.setText(self.offset + "  " + self.name)
    
    def getName(self):
        return self.name
    
    def getOffset(self):
        return self.offset
    
    def getTzInfo(self):
        return pytz.timezone(self.name)