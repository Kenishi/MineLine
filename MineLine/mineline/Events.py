'''
Created on Mar 9, 2014

@author: Kei
'''
from mineline.AbstractEvent import AbstractEvent
import json

class MessageEvent(AbstractEvent):
    __message = ""
    
    def __init__(self, user, time, msg):
        super(MessageEvent,self).__init__(user=user,time=time)
        self.__message = msg  # NOTE: Message MAY be a Tuple
        
    def getMessage(self):
        return self.__message
    
    @staticmethod
    def getEventType():
        return "MESSAGE"
    
    def __eq__(self, other):
        if not super(MessageEvent,self).__eq__(other):
            return False
        if not other.getMessage() == self.__message:
            return False
        return True
 
class InviteEvent(AbstractEvent):
    __invited_user = ""
    
    def __init__(self,inviting_user,invited_user,time):
        super(InviteEvent, self).__init__(user=inviting_user, time=time)
        self.__invited_user = invited_user
        pass
    
    def getInvitingUser(self):
        return self.getUser()
    
    def getInvitedUser(self):
        return self.__invited_user
    
    def json_out(self):
        package = {'type':self.getEventType(),'invited_user':self.getInvitedUser()}
        return json.dumps(package)
    
    def hasJSONContent(self):
        return True
    
    @staticmethod
    def getEventType():
        return "INVITE"
    
    @staticmethod
    def fromJSON_getInvitedUser(json_str):
        package = json.loads(json_str)
        if package['type'] == InviteEvent.getEventType():
            return package['invited_user']
        return None
        pass
    
    def __eq__(self, other):
        if not super(InviteEvent,self).__eq__(other):
            return False
        if not other.getInvitedUser() == self.__invited_user:
            return False
        return True
        pass

class JoinedChatEvent(AbstractEvent):    
    @staticmethod
    def getEventType():
        return "JOINED_CHAT"
    pass

class LeaveChatEvent(AbstractEvent):
    @staticmethod
    def getEventType():
        return "LEAVE_CHAT"
    pass

class LeaveGroupEvent(AbstractEvent):
    @staticmethod
    def getEventType():
        return "LEAVE_GROUP"
    pass

class PhotoEvent(AbstractEvent):
    @staticmethod
    def getEventType():
        return "PHOTO"
    pass

class StickerEvent(AbstractEvent):
    @staticmethod
    def getEventType():
        return "STICKER"
    pass

class VideoEvent(AbstractEvent):
    @staticmethod
    def getEventType():
        return "VIDEO"
    pass

class FileEvent(AbstractEvent):
    @staticmethod
    def getEventType():
        return "FILE"
    pass
class AudioEvent(AbstractEvent):
    @staticmethod
    def getEventType():
        return "AUDIO"
    pass

class ChangeGroupNameEvent(AbstractEvent):
    __newname = ""
    
    def __init__(self, user, time, newname):
        super(ChangeGroupNameEvent, self).__init__(user=user, time=time)
        self.__newname = newname
    
    def getNewGroupName(self):
        return self.__newname
    
    @staticmethod
    def getEventType():
        return "CHANGE_GROUP_NAME"
    
    def __eq__(self, other):
        if not super(ChangeGroupNameEvent,self).__eq__(other):
            return False
        if not other.getNewGroupName() == self.__newname:
            return False
        return True
    
    def hasJSONContent(self):
        return True
    
    def json_out(self):
        package = {'type':self.getEventType(), 'newname':self.getNewGroupName()}
        return json.dumps(package)
    
    @staticmethod
    def fromJSON_getNewGroupName(json_str):
        package = json.loads(json_str)
        if package["type"] == ChangeGroupNameEvent.getEventType():
            return package["newname"]
        return None
    pass
    
class EnumEvents:
    events = (MessageEvent, InviteEvent, JoinedChatEvent, LeaveChatEvent, LeaveGroupEvent,
               PhotoEvent, StickerEvent, ChangeGroupNameEvent)
