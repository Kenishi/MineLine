'''
Created on May 1, 2014

@author: Kei
'''
import unittest
import sys

from PyQt4 import QtGui
from mineline.gui.LoadingDialog import LoadingFrame

class LoadFrameTests(unittest.TestCase):


    def setUp(self):
        self.app = QtGui.QApplication(sys.argv)
        self.main = QtGui.QMainWindow()
        
        # Set Looks
        self.main.setWindowTitle("Test Loading Frame")
        self.main.setGeometry(300, 300, 150, 200)
        
        pass


    def tearDown(self):
        pass


    def testShouldShowHalf(self):
        # Setup
        loadingFrame = LoadingFrame(self.main)
        self.main.setCentralWidget(loadingFrame)
        self.main.show()
        
        # Exercise
        loadingFrame.updateProgress("This is Half", 50, 100)
        
        # Test
        self.app.exec_()
        
        pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()