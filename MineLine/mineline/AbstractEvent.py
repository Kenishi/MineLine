'''
Created on Mar 9, 2014

@author: Kei
'''
from abc import ABCMeta, abstractmethod


class AbstractEvent(object):
    __metaclass__ = ABCMeta
    
    def __init__(self, user, time):
        self.__user = user
        self.__time = time
    
    @abstractmethod
    def getEventType(self):
        raise NotImplementedError    
    
    def getTimeAsStruct(self):
        import time
        out = time.strptime(self.__time,"%Y/%m/%d %H:%M UTC")
        return out
    
    def getTime(self):
        return self.__time

    def getUser(self):
        return self.__user
    
    def hasJSONContent(self):
        return False
    
    def __eq__(self, other):
        if not other.getUser() == self.__user:
            return False
        if not other.getTime() == self.__time:
            return False
        return True 
    
    def __str__(self):
        str = self.getEventType() + " " + self.getTime() + " " + self.getUser()
        return str