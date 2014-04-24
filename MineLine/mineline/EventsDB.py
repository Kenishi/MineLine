'''
Created on Apr 21, 2014

@author: Kei
'''
from mineline.Events import *
from abc import ABCMeta, abstractmethod

class AbstractEventDB(object):
    

class BaseEventDB(object):
    '''
    Class acts as a base inheritor for events from the DB
    Mimics the AbstractEvent class in many ways. 
    
    Note: The reason for the lack of multiple inheritance is that call signatures
            do not and cannot match up the tree when mixing the BaseEventDB class
            and any of the normal Event classes.
    ''' 
    def __init__(self, user, time, time_epoch):
        self.__user = user
        self.__time = time
        self.__time_epoch = time_epoch
    
    def getUser(self):
        return self.__user
    
    def getTime(self):
        return self.__time
    
    def getTimeEpoch(self):
        return self.__time_epoch  
    
    @staticmethod   
    def fromRowResult(row):
        user = row['user']
        time = BaseEventDB.convertEpochToStr(row['time'])
        time_epoch = row['time']
        return BaseEventDB(user, time, time_epoch)
            
    @staticmethod
    def convertEpochToStr(secs):
        '''
        Change a time in epoch seconds to its string representation.
        
        secs: An integer with an epoch timestamp
        Returns the time as a string in Year/Month/Date 24h:Minute
        '''
        import time
        secs = int(secs)
        time_struct = time.gmtime(secs)
        time_str = time.strftime("%Y/%m/%d %H:%M", time_struct)
        return time_str

class MessageEventDB(BaseEventDB, MessageEvent):
    def __init__(self, user, time, msg, pos_msg):
        super(MessageEventDB, self).__init__(user, time, msg)
        self.__pos_msg = pos_msg
        pass

    def getTaggedMessage(self):
        return self.__pos_msg 
       
    @staticmethod
    def fromRowResult(row):
        event = BaseEventDB.fromRowResult(row)
        return MessageEventDB(event.getUser(), event.getTime(), row['content'], row['content_pos_tag'])
    pass

class InviteEventDB(BaseEventDB, InviteEvent):
    def __init__(self, time_epoch, user, invited_user):
        time = EventDBHelper.convertEpochToStr(time_epoch)
        super(InviteEventDB, self).__init__(inviting_user=user, invited_user=invited_user, time=time)
        pass
    
    @staticmethod
    def fromRowResult(row):
        invited_user = InviteEvent.fromJSON_getInvitedUser(row['content'])
        return InviteEventDB(row['time'], row['user'], invited_user)

    pass

class JoinedChatEventDB(JoinedChatEvent):
    def __init__(self,user, time):
        super(JoinedChatEventDB, self).__init__(user, time)
    pass

class LeaveChatEventDB(LeaveChatEvent):
    def __init__(self,user, time_epoch):
        super(LeaveChatEventDB, self).__init__(user, EventDBHelper.convertEpochToStr(time_epoch))
    pass

class PhotoEventDB(PhotoEvent):
    def __init__(self,user, time_epoch):
        super(PhotoEventDB, self).__init__(user, EventDBHelper.convertEpochToStr(time_epoch))
    pass

class StickerEventDB(StickerEvent):
    
    fromRowResult = BaseEventDB.fromRowResult
    pass

class VideoEventDB(VideoEvent):
    def __init__(self,user, time_epoch):
        super(VideoEventDB, self).__init__(user, EventDBHelper.convertEpochToStr(time_epoch))
    pass

class FileEventDB(FileEvent):
    def __init__(self,user, time_epoch):
        super(FileEventDB, self).__init__(user, EventDBHelper.convertEpochToStr(time_epoch))    
    pass

class AudioEventDB(AudioEvent):
    def __init__(self,user, time_epoch):
        super(AudioEventDB, self).__init__(user, EventDBHelper.convertEpochToStr(time_epoch))    
    pass

class ChangeGroupNameEventDB(ChangeGroupNameEvent):
    def __init__(self,user, time_epoch, newname):
        
        super(JoinedChatEventDB, self).__init__(user, EventDBHelper.convertEpochToStr(time_epoch))
    pass