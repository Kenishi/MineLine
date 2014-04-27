'''
Created on Mar 24, 2014

@author: Kei
'''

import sqlite3
import time
import nltk
from nltk.tokenize import word_tokenize
from mineline.Events import *
from mineline.EventsDB import *

class LineLogDB(object):
    '''
    The class interface for a LineLog SQL DB.
    '''
    def __init__(self, db_file):
        '''
        Constructor
        
        db_file should be a string filepath pointing to where the DB file is or should be created.
        '''
        
        self.__conn = sqlite3.connect(db_file)
        self.__initDB()
        pass
    
    def getEvents(self,events):
        '''
        Get all events of an event type.
        
        events: Should be a list() of class events. Either base event (ex: MessageEvent) or
                    their database representation class (ex: MessageEventDB) will work.
        Returns matching events as a list of dictionaries for each event
        '''
        
        # Convert base events to their string event type. 
        event_str = []
        for event in events:
            isRealEvent = (event in EnumEventsDB.events or event in EnumEvents.events)
            isDuplicate = (event.getEventType() in event_str)
            if isRealEvent and not isDuplicate: 
                event_str.append(event.getEventType())
        
        cursor = self.__conn.cursor()
        
        # Create where string based on event_str
        def buildWhereComp(event_str):
            for event in event_str:
                yield "event_type='" + event + "'" 
        
        where = "WHERE " 
        conditionals = " OR ".join(buildWhereComp(event_str))
        where = where + conditionals
        sql = """SELECT * FROM log """ + where
        
        cursor.execute(sql)
        results = self.__ReWrapEvents(cursor.fetchall())
        
        return results
    
    def addLineLog(self, linelog):
        '''
        Add a current LineLog to the DB
        '''
        cursor = self.__conn.cursor()
        
        # Create a new log table and delete the old one if this one is newer, otherwise show error message.
        if not self.__logTableExists():
            self.__createLogTable()
        else:
            if not self.__isNewerLog(linelog):
                print "The Line Log being added is not currently newer than currently stored log.\
                     Consider doing a mergeLog() to add in older events."
                return
            else:
                self.__deleteLogTable() # Delete the log table
                self.__createLogTable() # Create new log table
                
        # Get the linelog's details
        created, first_event, last_event = self.__convertLineLogTimes(linelog)
        event_count = linelog.getEventCount()
        
        # Update the meta-table to reflect the new LineLog
        self.__UpdateTableInfo("log", created, first_event, last_event, event_count)
        
        # Add events to the log table
        for event in linelog.getEvents():
            time, user, event_type, content, tagged_str = self.__gatherRowValuesFromEvent(event)
            
            sql = """INSERT INTO log (time, user, event_type, content, content_pos_tag) 
                        VALUES ({0},"{1}","{2}","{3}","{4}")"""
            sql = sql.format(time, user, event_type, content, tagged_str)
            
            cursor.execute(sql)
            
        self.__conn.commit()
        pass
    
    def __ReWrapEvents(self, rows):
        '''
        Returns the rows of events as their Class Events
        
        rows: List of rows returned from a query containing
        Returns: A list of events as their class
        '''
        
        events = []
        for row in rows:
            event_type = row['event_type']
            # Find the matching event type and rewrap
            for event_class in EnumEventsDB.events:
                if event_type == event_class.getEventType():
                    events.append(event_class.fromRowResult(row))
        return events
                
    
    def __initDB(self):
        self.__conn.row_factory = sqlite3.Row
        cursor = self.__conn.cursor()
        
        # Create table_info if it doesn't exist
        cursor.execute('''CREATE TABLE IF NOT EXISTS table_info 
                            ( tbl_name TEXT, created INTEGER, first_event INTEGER,
                               last_event INTEGER, event_count INTEGER )  ''')
        self.__conn.commit()
    
    def __UpdateTableInfo(self, table_name, created, first_event, last_event, count):
        cursor = self.__conn.cursor()
        
        sql = """SELECT * FROM table_info WHERE tbl_name='{0}'""".format(table_name)
        cursor.execute(sql)

        bundle = (table_name, created, first_event, last_event, count)        
        # UPDATE the row if its already there otherwise INSERT
        if cursor.rowcount > 0:
            sql = """UPDATE table_info SET created={1}, first_event={2},\
             last_event={3}, event_count={4} WHERE tbl_name='{0}'""".format(*bundle)
        else:
            sql = """INSERT INTO table_info(tbl_name, created, first_event, last_event, event_count)\
                         VALUES('{0}','{1}','{2}','{3}','{4}')""".format(*bundle)
        
        cursor.execute(sql)
        self.__conn.commit()
        pass
    
    def __convertLineLogTimes(self,linelog):
        ''' Convert the LineLog's internal times to epochs and return in a tuple '''
        
        # Get the linelog's details
        created = linelog.getLogTimeStamp()
        first_event = linelog.getFirstEventDate()
        last_event = linelog.getLastEventDate()
        
        # Convert the times to epoch
        created = self.__getEpochTimeStamp(created)
        first_event = self.__getEpochTimeStamp(first_event)
        last_event = self.__getEpochTimeStamp(last_event)
        
        return (created, first_event, last_event)
        pass
    
    def __gatherRowValuesFromEvent(self, event):
        '''
        Collects the needed information for a row in the table log, from the supplied Event
        
        Returns the data in a tuple in following order:
            time: Time of the event as epoch in an integer
            user: The username of the person who generated the event
            event_type: String representing the event type
            content: For MessageEvents this is the untagged message string.
                     For InviteEvents this is will hold the invited_user's name in a JSON object.
                     For ChangeGroup..Events this will hold the new group name in a JSON object.
                     This data is returned in a JSON String
            tagged_str: For message events this holds the message after its been Part-Of-Speech tagged
        '''
        time = self.__getEpochTimeStamp(event.getTime())
        user = event.getUser()
        event_type = event.getEventType()
        content = ""
        tagged_str = ""
        
        if type(event) is MessageEvent:
            content = event.getMessage()
            tagged_str = nltk.pos_tag(word_tokenize(content))
        elif event.hasJSONContent():
            content = event.json_out()
        
        return (time, user, event_type, content, tagged_str)
    
    def __getEpochTimeStamp(self, timestr):
        import calendar

        time_struct = time.strptime(timestr, "%Y/%m/%d %H:%M")
        timestamp = calendar.timegm(time_struct)
        return int(timestamp)
        pass
    
    def __isNewerLog(self, linelog):
        cursor = self.__conn.cursor()
        
        time_str = linelog.getLogTimeStamp() 
        timestamp = self.__getEpochTimeStamp(time_str)
        
        # Grab the timestamp for when the linelog was created
        if self.__logTableExists():
            sql = "SELECT created FROM table_info WHERE tbl_name='log'"
            cursor.execute(sql)
            row = cursor.fetchone()
            stored_timestamp = int(row[0])
            if timestamp > stored_timestamp:
                return True
            else:
                return False
        else:
            return True
    
    def __logTableExists(self):
        cursor = self.__conn.cursor()
        sql = "SELECT name FROM sqlite_master WHERE type='table' and name='log'"
        cursor.execute(sql)
        row = cursor.fetchone()
        if row:
            return True
        else: # Log table doesn't even exist
            return False
        pass  
      
    def __deleteLogTable(self):
        cursor = self.__conn.cursor()
        sql = "DROP TABLE IF EXISTS log"
        cursor.execute(sql)
        self.__conn.commit()
        pass
    
    def __createLogTable(self):
        cursor = self.__conn.cursor()
        
        sql = """CREATE TABLE log(time INTEGER NOT NULL, user TEXT NOT NULL,
                 event_type TEXT NOT NULL, content TEXT, content_pos_tag TEXT)"""
        cursor.execute(sql)
        self.__conn.commit()        