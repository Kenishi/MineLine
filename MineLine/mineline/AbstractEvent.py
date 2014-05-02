'''
Created on Mar 9, 2014

@author: Kei
'''
import pytz
import datetime
from abc import ABCMeta, abstractmethod


class AbstractEvent(object):
    
    __metaclass__ = ABCMeta
    
    def __init__(self, user, time):
        self.__user = user
        self.__time = time # Datetime Structure in UTC
        self.__time_fmt = "%Y/%m/%d %H:%M"
    
    @abstractmethod
    def getEventType(self):
        raise NotImplementedError    
    
    def getTime(self, timezone=pytz.utc):
        '''
        Returns the time in a datetime object.
        
        timezone is a tzinfo specifying the target timezone wanted. By default, the timezone is UTC.
        '''
        if timezone == pytz.utc:
            return self.__time
        
        # Convert to timezone
        target = self.__time.astimezone(timezone)
        
        return target
    
    def getTimeString(self, timezone=pytz.utc):
        if timezone != pytz.utc:
            target = self.getTime(timezone)
        else:
            target = self.__time
        return target.strftime(self.getTimeFormatString(True))
        

    def getUser(self):
        return self.__user
    
    def hasJSONContent(self):
        return False
    
    def getTimeFormatString(self, addTZ=True):
        '''
        Return the time format string which can be used in strftime() strptime() calls.
        
        addTZ determines whether to add the %Z to the timeformat or leave it off. 
        Returns a string with the format.
        ''' 
        if addTZ:
            return self.__time_fmt + " %Z"
        else:
            return self.__time_fmt
    
    def __eq__(self, other):
        if not other.getUser() == self.__user:
            return False
        if not other.getTime() == self.__time:
            return False
        return True 
    
    def __str__(self):
        str = self.getEventType() + " " + self.getTimeString() + " " + self.getUser()
        return str