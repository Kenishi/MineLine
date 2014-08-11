'''
Created on Mar 24, 2014

@author: Kei
'''
import unittest
import os
from mineline.LineLogDB import LineLogDB
from mineline.LineLog import LineLog
from mineline.Events import *
from mineline.EventsDB import *


class Test(unittest.TestCase):
    TestDBPath = "./LineLogTest.DB"
    
    def testCanAddLineLog_newer(self):
        ''' Test that we can add a small NEW LineLog to DB and retrieve the events '''
        
        import datetime, pytz
        
        # Setup - Create Mock LineLog
        
        event1_dt = pytz.utc.localize(datetime.datetime.strptime("2014/01/01 12:00 UTC", "%Y/%m/%d %H:%M %Z"))
        event2_dt = pytz.utc.localize(datetime.datetime.strptime("2014/01/01 12:01 UTC", "%Y/%m/%d %H:%M %Z"))
        
        msg_list = [MessageEvent("i am ok", event1_dt, "Test Message 1"),
                    MessageEvent("i am ok", event2_dt, "Test Message 2")]
        
        savedTime = datetime.datetime.strptime("2014/01/02 13:00 UTC", "%Y/%m/%d %H:%M %Z")
        
        linelog = LineLog(msg_list, savedTime)
        logDB = LineLogDB(self.TestDBPath)

        # Exercise
        logDB.addLineLog(linelog)
        events = logDB.getEvents(events=[MessageEvent])        
        
        # Test
        try:
            for x in range(2):
                # Have to test using function calls due to class type mismatch
                self.assertEqual(msg_list[x].getUser(),events[x].getUser())
                self.assertEqual(msg_list[x].getMessage(),events[x].getMessage())
                self.assertEqual(msg_list[x].getTimeString(), events[x].getTimeString())
                self.assertEqual(msg_list[x].getEventType(),events[x].getEventType())
        finally:
            os.remove(self.TestDBPath)
        
    def testStickerEventDB(self):
        ''' Test that normal events like Sticker/Photo/Audio, return proper info when using fromRowResult() '''
        # Setup
        row = {"user":"i am ok", "time":"1398281296"}
        
        # Exercise
        event = StickerEventDB.fromRowResult(row)
        user = event.getUser()
        eventtype = event.getEventType()
        time_str = event.getTimeString()
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
        time_str = event.getTimeString()
        time_epoch = event.getTimeEpoch()
        eventtype = event.getEventType()
        msg = event.getMessage()
        msg_tag = event.getTaggedMessage()
        
        # Test
        self.assertEqual(user, row['user'])
        self.assertEqual(time_epoch, row['time'])
        self.assertEqual(eventtype, "MESSAGE")
        self.assertEqual(time_str, "2014/04/23 19:28 UTC")
        self.assertEqual(msg, row['content'])
        self.assertEqual(msg_tag, row['content_pos_tag'])
        
    def testCreatesDB(self):
        ''' Test that we should be able to create a DB '''
        
        # Setup & Exercise
        try:
            os.remove(self.TestDBPath)
        except Exception:
            pass
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