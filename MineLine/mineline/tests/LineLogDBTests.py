'''
Created on Mar 24, 2014

@author: Kei
'''
import unittest
import sqlite3
import os
from mineline.LineLogDB import LineLogDB
from mineline.LineLog import LineLog
from mineline.Events import *
from mineline.EventsDB import *


class Test(unittest.TestCase):
    TestDBPath = "./LineLogTest.DB"
    
    def testCanAddLineLog_newer(self):
        ''' Test that we can add a small NEW LineLog to DB and retrieve the events '''
        
        # Setup - Create Mock LineLog
        msg_list = [MessageEvent("i am ok", "2014/01/01 12:00", "Test Message 1"),
                    MessageEvent("i am ok", "2014/01/01 12:01", "Test Message 2")]
        
        '''Due to no pre-processing, times are assumed to already be converted to UTC'''
        expectedTime = ["2014/01/01 12:00 UTC", "2014/01/01 12:01 UTC"]
        
        linelog = LineLog(msg_list, "2014/01/02 13:00")
        
        os.remove(self.TestDBPath)
        logDB = LineLogDB(self.TestDBPath)

        # Exercise
        logDB.addLineLog(linelog)
        events = logDB.getEvents(events=[MessageEvent])        
        
        # Test
        for x in range(2):
            # Have to test using function calls due to class type mismatch
            self.assertEqual(msg_list[x].getUser(),events[x].getUser())
            self.assertEqual(msg_list[x].getMessage(),events[x].getMessage())
            self.assertEqual(expectedTime[x], events[x].getTime())
            self.assertEqual(msg_list[x].getEventType(),events[x].getEventType())
        
        # Clean-up
        os.remove(self.TestDBPath)
    
    def testStickerEventDB(self):
        ''' Test that normal events like Sticker/Photo/Audio, return proper info when using fromRowResult() '''
        # Setup
        row = {"user":"i am ok", "time":"1398281296"}
        
        # Exercise
        event = StickerEventDB.fromRowResult(row)
        user = event.getUser()
        eventtype = event.getEventType()
        time_str = event.getTime()
        time_epoch = event.getTimeEpoch()
        
        # Test
        self.assertEqual(user, row['user'])
        self.assertEqual(time_epoch, row['time'])
        self.assertEqual(eventtype, "STICKER")
        self.assertEqual(time_str, "2014/04/23 19:28 UTC")
        
    
    def testMessageEventDB(self):
        ''' Test that MessageEventDB's fromRowResult() returns expected values '''
        # Setup
        row = {"user":"i am ok", "time":"1398281296", "content":"HEELLLO","content_pos_tag":["stuff","inhere"]}
        
        # Exercise
        event = MessageEventDB.fromRowResult(row)
        user = event.getUser()
        time_str = event.getTime()
        time_epoch = event.getTimeEpoch()
        eventtype = event.getEventType()
        msg = event.getMessage()
        msg_tag = event.getTaggedMessage()
        
        # Test
        self.assertEqual(user, row['user'])
        self.assertEqual(time_epoch, row['time'])
        self.assertEqual(eventtype, "MESSAGE")
        self.assertEqual(time_str, "2014/04/23 19:28")
        self.assertEqual(msg, row['content'])
        self.assertEqual(msg_tag, row['content_pos_tag'])
        
    def testCreatesDB(self):
        ''' Test that we should be able to create a DB '''
        
        # Setup & Exercise
        os.remove(self.TestDBPath)
        logDB = LineLogDB(self.TestDBPath)
        
        # Test
        test = os.path.exists("/Users/Kei/Documents/LineLogTest.DB")
        self.assertTrue(test)
        
        #Clean-up
        os.remove(self.TestDBPath)
        pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()