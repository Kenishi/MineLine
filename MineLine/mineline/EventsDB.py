'''
Created on Apr 21, 2014

@author: Kei
'''
from mineline.Events import *

class AbstractEventDB(AbstractEvent):
    '''
    Class acts as a base inheritor for events from the DB
    Mimics the AbstractEvent class in many ways. 
    
    Note: The reason for the lack of multiple inheritance is that call signatures
            do not and cannot match up the tree when mixing the AbstractEventDB class
            and any of the normal Event classes.
    ''' 
    def getTimeEpoch(self):
        return self.__time_epoch  
    
    def getEventType(self):
        '''
        If called somehow, this will return None.
        There is no way to pass on implementing this.
        '''
        return None
    
    @classmethod   
    def fromRowResult(cls,row):
        cls.__user = row['user']
        cls.__time = cls.convertEpochToDateTime(row['time'])
        cls.__time_epoch = row['time']
        self = cls(cls.__user, cls.__time)
        return self
            
    @staticmethod
    def convertEpochToDateTime(secs):
        '''
        Change a time in epoch seconds to its string representation.
        
        secs: An integer with an epoch timestamp
        Returns the time as a string in Year/Month/Date 24h:Minute
        '''
        import datetime, pytz
        secs = int(secs)
        utc_dt = datetime.datetime.utcfromtimestamp(secs)
        utc_dt = pytz.utc.localize(utc_dt)
        return utc_dt

class MessageEventDB(MessageEvent, AbstractEventDB):
    def __init__(self, user, time, msg, pos_msg):
        super(MessageEventDB, self).__init__(user, time, msg)
        self.__pos_msg = pos_msg
        pass

    def getTaggedMessage(self):
        return self.__pos_msg 
       
    @classmethod
    def fromRowResult(cls, row):
        event = AbstractEventDB.fromRowResult(row)
        return cls(event.getUser(), event.getTime(), row['content'], row['content_pos_tag'])
    pass

class InviteEventDB(InviteEvent, AbstractEventDB):
    def __init__(self, user, time, invited_user):
        super(InviteEventDB, self).__init__(inviting_user=user, invited_user=invited_user, time=time)
        pass
    
    @classmethod
    def fromRowResult(cls, row):
        event = AbstractEventDB.fromRowResult(row)
        invited_user = InviteEvent.fromJSON_getInvitedUser(row['content'])
        return cls(event.getUser(), event.getTime(), invited_user)
    pass

class JoinedChatEventDB(JoinedChatEvent, AbstractEventDB):
    pass

class LeaveChatEventDB(LeaveChatEvent, AbstractEventDB):
    pass

class PhotoEventDB(PhotoEvent, AbstractEventDB):
    pass

class StickerEventDB(StickerEvent, AbstractEventDB):
    pass

class VideoEventDB(VideoEvent, AbstractEventDB):
    pass

class FileEventDB(FileEvent, AbstractEventDB):   
    pass

class AudioEventDB(AudioEvent, AbstractEventDB):    
    pass

class ChangeGroupNameEventDB(ChangeGroupNameEvent, AbstractEventDB):
    def __init__(self,user, time, newname):
        super(JoinedChatEventDB, self).__init__(user, time, newname)
        pass
    
    @classmethod
    def fromRowResult(cls, row):
        event = AbstractEventDB.fromRowResult(row)
        newname = cls.fromJSON_getNewGroupName(row['content'])
        return cls(event.getUser(), event.getTime(), newname)
    
    pass

class EnumEventsDB:
    events = (MessageEventDB, InviteEventDB, JoinedChatEventDB, LeaveChatEventDB, PhotoEventDB, StickerEventDB,
                VideoEventDB, FileEventDB, AudioEventDB, ChangeGroupNameEventDB)