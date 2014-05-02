from mineline.PreProcessLog import PreProcessLog
from mineline.Events import *

class LineLog(object):
    __log__ = list() # List containing each line in the log
    __saveTime = None # String of timestamp for when the log was saved
    
    def __init__(self,log_list, saveTime):
        assert log_list != None
        self.__log__ = log_list    
        self.__saveTime = saveTime
        pass
    
    @classmethod
    def fromString(cls, unprocessed_str, savedTimeZone, progressCallback=None):
        processed_log, logSaveTime = PreProcessLog.processLog(unprocessed_str, savedTimeZone)
        return cls(processed_log, logSaveTime)
    
    @classmethod
    def fromFilename(cls, filepath, savedTimeZone, progressCallback=None):
        # Open log file and read in data
        with open(filepath) as logfile:
            unprocessed_str = logfile.read()
        
            # Process for log objects
            processed_log, logSaveTime =  PreProcessLog.processLog(unprocessed_str, savedTimeZone, progressCallback)
            return cls(processed_log, logSaveTime)
        pass
    
    @staticmethod
    def fromPickle(dataFilePath):
        import gzip, cPickle
        
        fp = gzip.open(dataFilePath, 'rb')
        saveTime = cPickle.load(fp)
        logList = cPickle.load(fp)
        fp.close()
        
        return LineLog(logList, saveTime)
    
    def pickleLog(self, dataFilePath):
        import gzip, cPickle
        fp = gzip.open(dataFilePath, 'wb')
        cPickle.dump(self.__saveTime,fp)
        cPickle.dump(self.__log__, fp)
        fp.close()
        return True
    
    def getLogTimeStamp(self):
        '''
        Return the timestamp of when the original text log was saved.
        
        This method returns the timestamp as a string in the format YYYY/MM/DD HH:MM
        '''
        return self.__saveTime
    
    def getEventCount(self):
        '''
        Return the number of events in the log
        
        This method returns an integer of the number of events in the log
        '''
        return len(self.__log__)
    
    def getFirstEventDate(self):
        '''
        Return the time of the first event in the log.
        
        This method returns the time as a string in the format YYYY/MM/DD HH:MM
        '''
        first_event = self.__log__[0]
        return first_event.getTime()
    
    def getLastEventDate(self):
        '''
        Return the time of the last event in the log.
        
        This method returns the time as a string in the format YYYY/MM/DD HH:MM
        '''
        last_event = self.__log__[-1]
        return last_event.getTime()
    
    def getUserEvents(self,user,exclude=None,include=None):
        '''
        Yield the events for a single user.
        
        This yields the events for a user based on exclude/include. If both exclude and include are None, then
        this method returns all events by a user.
        
        exclude: Should be a list of type() events to exclude from the yield. Exclude has precedence over 'include'
        include: Should be a list of type() events to include in the yield.
        '''
        for event in self.__log__:
            if event.getUser() == user:
                if exclude and (type(event) in exclude): # Event is in exclude, skip
                    continue
                elif include and (type(event) not in include): # Event isn't in include, skip
                    continue
                yield event
    
    def getUserNames(self):
        '''
        Return the users present in the log.
        
        This method returns a list of strings for all the usernames that appear in the log.
        '''
        users = []
        for event in self.__log__:
            if event.getUser() not in users:
                users.append(event.getUser())
        return users
    
    def getEvents(self,events=None):
        '''
        Generator to yield events
        
        events: List of target event types to return. When None, will return all events.
        '''
        for event in self.__log__:
            if events == None:
                yield event
            elif type(event) in events:
                yield event
    
    """ Stats Functions """
    
    def countUserEvents(self, users=None,events=None):
        '''
        Returns a pair tuple containing a 2-D list of users plus a count
            for each event. The other part of the tuple tells the  
        '''        
        # Prepare headers and Fill events if empty
        if events:
            header = events
        else:
            from mineline.Events import EnumEvents
            events = header = EnumEvents.events
        
        user_stats = self.__countEventLoop(users, events)
        
        return (user_stats, header)
        pass
                
    def __countEventLoop(self,users,events):
        count = {}
        # Count events
        for event in self.__log__:
            if type(event) not in events:
                continue
            
            user = event.getUser()
            if users: # There is a user target list
                if user in users and user in count: # User is in target list and has been initilized
                    count[user][type(event)] += 1
                elif user in users and user not in count: # User is in target list but hasn't been initilized
                    from itertools import repeat
                    zero_events = list(repeat(0,len(events))) # Create a zero'd count list for every event in target
                    count[user] = dict(zip(events,zero_events))
            else: # Do all users
                if user in count: # User has already been initilized
                    count[user][type(event)] += 1
                else:
                    from itertools import repeat
                    zero_events = list(repeat(0,len(events))) # Create a zero'd count list for every event in target
                    count[user] = dict(zip(events,zero_events))
        return count
    
    def __str__(self):
        str_out = ""
        for line in self.log:
            str_out += line
        return str_out
    
    def __eq__(self,other):
        if type(other) != LineLog:
            return False
        if self.__log__ != other.__log__:
            return False
        return True