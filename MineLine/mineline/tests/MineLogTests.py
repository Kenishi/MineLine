'''
Created on Mar 7, 2014

@author: Kei
'''
import unittest

class Test(unittest.TestCase):
    filepath = "/Users/Kei/Documents/[LINE] Chat in Climate Shockin'.txt"
       
    def testPickle(self):
        from mineline.Events import MessageEvent, PhotoEvent
        from mineline.LineLog import LineLog
        
        # Setup
        loglist = [MessageEvent("John", "12/13/14 12:12", "Testing"),PhotoEvent("John","12/13/14")]
        line = LineLog(loglist, "2014/01/01 13:00")
        
        # Exercise
        testFile = "./testPickle.data"
        line.pickleLog(testFile)
        testLine = LineLog.fromPickle(testFile)
        
        self.assertEqual(line, testLine)
        
     
    def testGetUserEvents(self):
        import pytz
        from mineline.LineLog import LineLog
     
        # Setup
        log = LineLog.fromFilename(self.filepath, pytz.timezone("Asia/Tokyo"))
        
        # Exercise
        count = 0
        for event in log.getUserEvents('i am ok'):
            count += 1
        print str(count)
    
    def testRealFile(self):
        import pytz
        from mineline.LineLog import LineLog
        
        # Exercise & Test
        #LineLog.fromFilename(self.filepath, pytz.timezone("Asia/Tokyo"))
    
    def testBaseEqual(self):
        from mineline.Events import PhotoEvent
        
        # Setup
        photo = PhotoEvent("John", "2013/05/23 12:00")
        photoMatch = PhotoEvent("John", "2013/05/23 12:00")
        photoDiff = PhotoEvent("John", "2014/05/23 12:01")
        
        # Exercise
        matchResult = (photo == photoMatch)
        diffResult = (photo == photoDiff)
        
        # Test
        self.assertTrue(matchResult == True)
        self.assertFalse(diffResult == False)
        
    def testProcessLines(self):
        import pytz
        from mineline.PreProcessLog import PreProcessLog
        from mineline.Events import MessageEvent
        # Setup
        data = ("2013/05/23(Thursday)\r\n"
        "12:48\tJohn\tI think so too\r\n"
        "2013/05/25(Friday)\r\n"
        "14:25\tJohn\tHello?\r\n")
        
        PreProcessLog.saveTimeZone = pytz.timezone("US/Eastern") # Set timezone so converTime() works
        data = PreProcessLog.splitLines(data)
        data = PreProcessLog.splitTabsAndCleanBlanks(data)
        data = PreProcessLog.convertTimes(data)
        
        expectedData = [MessageEvent("John", "2013/05/23 16:48 UTC", "I think so too"),
                        MessageEvent("John", "2013/05/25 18:25 UTC", "Hello?")]
        # Exercise
        log_list, saveTime = PreProcessLog.processLines(data)
        
        # Test
        self.assertEqual(log_list, expectedData)

    def testExpandDates(self):
        import pytz
        from mineline.PreProcessLog import PreProcessLog
        
        # Setup
        data = ("2013/05/23(Thursday)\r\n"
        "12:00\tBob\tSome test text\r\n"
        "12:48\tJohn\tI think so too\r\n"
        "2013/05/25(Friday)\r\n"
        "14:25\tJohn\tHello?\r\n"
        "14:28\tBob\tYo what's up?\r\n"
        "14:29\tJohn\tNot much you?\r\n")
        
        data = PreProcessLog.splitLines(data)
        data = PreProcessLog.splitTabsAndCleanBlanks(data)
        
        expectedData = [["2013/05/23 16:00 UTC","Bob","Some test text"],["2013/05/23 16:48 UTC","John","I think so too"],["2013/05/25 18:25 UTC","John","Hello?"],["2013/05/25 18:28 UTC","Bob","Yo what's up?"],["2013/05/25 18:29 UTC","John","Not much you?"]]
        
        # Exercise
        PreProcessLog.saveTimeZone = pytz.timezone("US/Eastern") # Set timezone so converTimes() works
        testResult = PreProcessLog.convertTimes(data)
        
        # Test
        self.assertEqual(testResult, expectedData, "Expanded Date result did not match expected.\nExpected:" + str(expectedData) + "\nActual:" + str(testResult))
        
    def testSplitTabs(self):
        from mineline.PreProcessLog import PreProcessLog
        # Setup
        data = ("2013/05/23(Thursday)\r\n"
        "12:00\tBob\tSome test text\r\n"
        "\r\n"
        "12:48\tJohn\tI think so too\r\n")
        data = PreProcessLog.splitLines(data)
        
        expectedData = [["2013/05/23(Thursday)"],["12:00","Bob","Some test text"],["12:48","John","I think so too"]]
        
        # Exercise
        testResult = PreProcessLog.splitTabsAndCleanBlanks(data)
        
        # Test
        self.assertEqual(testResult, expectedData, "Split Tab Data does not match expected.\nExpected:" + str(expectedData) + "\nActual:" + str(testResult))
        pass
    
    def testSplitLines(self):
        from mineline.PreProcessLog import PreProcessLog
        # Setup
        data = ("2013/05/23(Thursday)\r\n"
        "12:00\tBob\tSome test text\r\n"
        "12:48\tJohn\tI think so too\r\n")
        
        expectedData = ["2013/05/23(Thursday)","12:00\tBob\tSome test text","12:48\tJohn\tI think so too"]
        
        # Exercise
        log_list = PreProcessLog.splitLines(data)
        
        # Test
        self.assertEqual(log_list, expectedData, "Split Line List does not match expected.\nExpected:" + str(expectedData) + "\nActual:" + str(log_list))
        
    def testGetUser(self):
        from mineline.Events import MessageEvent
        # Setup
        message = MessageEvent(user="i am ok", time="12/4/2014", msg="Hi")
        
        # Exercise
        testStr = message.getUser()
        
        #Test
        self.assertEqual(testStr, "i am ok")

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()