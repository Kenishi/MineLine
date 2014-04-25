'''
Created on Mar 24, 2014

@author: Kei
'''
import unittest
import sqlite3
from mineline.LineLogDB import LineLogDB
from mineline.LineLog import LineLog
from mineline.Events import *
from mineline.EventsDB import *

class Test(unittest.TestCase):
    
    def testCanAddLineLog_newer(self):
        # Setup - Create Mock LineLog
        msg_list = [MessageEvent("i am ok", "2014/01/01 12:00", "Test Message 1"),
                    MessageEvent("i am ok", "2014/01/01 12:01", "Test Message 2")]
        linelog = LineLog(msg_list, "2014/01/02 13:00")
    
        logDB = LineLogDB("./LineLogTest.db")

        # Exercise
        logDB.addLineLog(linelog)
        
        # Test
        events = logDB.getEvents(events=[MessageEvent])
        self.assertEqual(msg_list[0], events[0])
        self.assertEqual(msg_list[1], events[1])
    
    def testStickerEventDB(self):
        # Setup
        row = {"user":"i am ok", "time":"1398281296"}
        
        # Exercise
        event = StickerEventDB.fromRowResult(row)
        
        # Test
        print event.getUser()
        print event.getTime()
        print event.getTimeEpoch()
        print event.getEventType()
    
    def testMessageEventDB(self):
        # Setup
        row = {"user":"i am ok", "time":"1398281296", "content":"HEELLLO","content_pos_tag":["stuff","inhere"]}
        
        # Exercise
        event = MessageEventDB.fromRowResult(row)
        
        # Test
        print event.getUser()
        print event.getTime()
        print event.getTimeEpoch()
        print event.getMessage()
        print event.getTaggedMessage()
        
    def testCreatesDB(self):
        # Setup & Exercise
        logDB = LineLogDB("/Users/Kei/Documents/LineLogTest.DB")
        
        # Test
        import os
        test = os.path.exists("/Users/Kei/Documents/LineLogTest.DB")
        self.assertTrue(test)
        pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()