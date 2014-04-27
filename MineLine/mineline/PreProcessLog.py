'''
Created on Mar 7, 2014

@author: Kei
'''
import re
import sqlite3
from mineline.Events import *
import time

class PreProcessLog(object):
    
    @classmethod
    def createLineLogFromString(cls,data, saveTimeZone):
        log_list = cls.splitLines(data)
        log_list = cls.splitTabsAndCleanBlanks(log_list)
        log_list = cls.expandDates(log_list)
        processed_log, saveTime = cls.processLines(log_list)
        
        from mineline.LineLog import LineLog
        return LineLog(processed_log, saveTime)
        pass
    
    @classmethod
    def splitLines(cls, data_str):
        split_line = data_str.split('\r\n')
        if len(split_line) > 0:
            del split_line[len(split_line)-1]
        else:
            del split_line[0]   
        return split_line
    
    @classmethod
    def splitTabsAndCleanBlanks(cls,log_list):
        '''
        Split a line along the tabs.
        Remove any lines that are blank
        '''
        split_lines = list()
        for line in log_list:
            if len(line) > 0: # Only add lines with content
                split_lines.append(line.split('\t'))
        return split_lines
    
    @classmethod
    def expandDates(cls,log_list, saveTimeZone):
        current_date = None
        expanded_list = []
        for line in log_list:
            if re.search('^[0-9]{,4}/[0-9]{,2}/[0-9]{,2}\(.+?\)', line[0]): # Check for start of new day
                current_date = time.strptime(line[0],"%Y/%m/%d(%A)")
                continue
            if re.search('^[0-9]{1,2}:[0-9]{1,2}', line[0]) != None:
                if current_date == None:
                    raise ParsingError("Current date was not set.")
                else:
                    fixed_hour = cls.__fixHour(line[0])
                    line[0] = time.strftime("%Y/%m/%d",current_date) + " " + fixed_hour
                    line[0] = cls.__convertToUTC(line[0], saveTimeZone)
            expanded_list.append(line)
        
        return expanded_list
        pass
    
    @classmethod
    def __convertToUTC(cls, time, saveTimeZone):
        '''
        Convert the current string time from the specified timze zone into UTC timezone.
        
        time: This is a string with a time in format %Y/%m/%d %H:%M
        saveTimeZone: This is a tzinfo for the timezone of the computer/phone that the log file was saved on.
                        Ex: If the phone is set for EST at save, then this needs to be the EST tzinfo.
        '''
        import pytz, datetime
        time_fmt = "%Y/%m/%d %H:%M"
        
        saved_time = datetime.datetime.strptime(time, time_fmt)
        savedWithTZ = saveTimeZone.localize(saved_time)
        saved_dt_utc = savedWithTZ.astimezone(pytz.utc)
        utc_str = saved_dt_utc.strftime(time_fmt + " %Z")
        return utc_str
    
    @classmethod
    def __fixHour(cls,time_str):
        match = re.search(r'(?P<hour>[0-9]{,2})(?P<rest>:[0-9]{,2})',time_str)
        hour = match.group("hour")
        rest = match.group("rest")
        if hour == "24":
            hour = "0"
        return hour + rest
    
    @classmethod    
    def processLines(cls,log_list):
        processed_list = []
        saveTime = None
        for line in log_list:
            processed_line = None
            
            if len(line) >= 3: # 3 sections indicates likely Message
                processed_line = cls.processMessageEvents(line)
            elif len(line) == 2: # 2 sections indicates likely Non-Message
                processed_line = cls.processNonMessageEvents(line)
            elif cls.isSaveTimeStamp(line):
                saveTime = cls.processSaveTime(line)
            elif cls.isKnownEdgeCase(line):
                pass
            else:
                print "Edge case detected: [" + str(log_list.index(line)) +'] ' + str(line)
            
            if processed_line != None:
                processed_list.append(processed_line)
        return ((processed_list),saveTime)
    
    @classmethod
    def processNonMessageEvents(cls,line):
        match = None
        msg = line[1]
        if cls.isInvited(msg):
            match=re.search(r'(?P<user>.+)? invited (?P<invited>.+)? to the group', msg)
            user = match.group("user")
            invited = match.group("invited")
            time = line[0]
            return InviteEvent(user, invited, time)
        elif cls.isJoinedChat(msg):
            match=re.search(r'(?P<user>.+)? joined the chat.', msg)
            user = match.group("user")
            time = line[0]
            return  JoinedChatEvent(user, time)
        elif cls.isLeftChat(msg):
            match=re.search(r'(?P<user>.+)? left the chat.', msg)
            user = match.group("user")
            time = line[0]
            return LeaveChatEvent(user, time)
        elif cls.isLeftGroup(msg):
            match=re.search(r'(?P<user>.+)? left the group.', msg)
            user = match.group("user")
            time = line[0]
            return LeaveGroupEvent(user, time)
        elif cls.isChangeName(msg):
            match=re.search(r'(?P<user>.+)? changed the group name to (?P<newname>.+)?', msg)
            user = match.group("user")
            newname = match.group("newname")
            time = line[0]
            return ChangeGroupNameEvent(user, time, newname)
        else:
            return None
        
    @classmethod
    def processMessageEvents(cls,line):
        time = line[0]
        user = line[1]
        msg = line[2:]
    
        # Check for instances where msg becomes more than 1 field due to UNICODE
        if type(msg) is list:
            msg = '\t'.join(msg)
            
        if cls.isPhoto(msg):
            return PhotoEvent(user=user, time=time)
        elif cls.isSticker(msg):
            return StickerEvent(user=user, time=time)
        elif cls.isVideo(msg):
            return VideoEvent(user=user, time=time)
        elif cls.isAudio(msg):
            return AudioEvent(user=user, time=time)
        elif cls.isFile(msg):
            return FileEvent(user=user, time=time)
        else:
            return MessageEvent(time=time, user=user, msg=msg)
    
    @classmethod
    def processSaveTime(cls, line):
        line = "".join(line)
        timeStr = re.search('^(?:Saved time).+?(?P<time>[0-9]{,4}/.+?)$',line).group("time")
        return timeStr
    
    @classmethod
    def isSaveTimeStamp(cls, line):
        line = "".join(line)
        if re.search('^Saved time', line):
            return True
        return False
    
    @classmethod
    def isKnownEdgeCase(cls, line):
        line = "".join(line)
        if re.search('^[LINE] Chat in', line):
            return True
        return False
    
    @classmethod
    def isPhoto(cls,msg):
        match = re.search(r'^\[Photo\]$', msg)
        return cls.__isMatch(match)
        pass
    
    @classmethod
    def isSticker(cls,msg):
        match = re.search(r'^\[Sticker\]$', msg)
        return cls.__isMatch(match)
        pass
    
    @classmethod
    def isVideo(cls, msg):
        match = re.search(r'^\[Video\]$', msg)
        return cls.__isMatch(match)
        pass
    
    @classmethod
    def isFile(cls, msg):
        match = re.search(r'^\[File\]$', msg)
        return cls.__isMatch(match)
        pass
    
    @classmethod
    def isAudio(cls, msg):
        match = re.search(r'^\[Sticker\]$', msg)
        return cls.__isMatch(match)
        pass
    
    @classmethod
    def isInvited(cls, msg):
        match=re.search(r'(?P<user>.+)? invited (?P<invited>.+)? to the group', msg)
        return cls.__isMatch(match)
        pass
    
    @classmethod
    def isJoinedChat(cls, msg):
        match=re.search(r'(?P<user>.+)? joined the chat.', msg)
        return cls.__isMatch(match)
        pass
    
    @classmethod
    def isLeftChat(cls, msg):
        match=re.search(r'(?P<user>.+)? left the chat.', msg)
        return cls.__isMatch(match)
        pass
    
    @classmethod
    def isLeftGroup(cls, msg):
        match=re.search(r'(?P<user>.+)? left the group.', msg)
        return cls.__isMatch(match)
        pass
    
    @classmethod
    def isChangeName(cls, msg):
        match=re.search(r'(?P<user>.+)? changed the group name to (?P<newname>.+)?', msg)
        return cls.__isMatch(match)
        pass
    
    @classmethod
    def __isMatch(cls,match):
        if match:
            return True
        else:
            return False
        
class ParsingError(Exception):
    def __init__(self, msg):
        super(ParsingError,self).__init__(msg)
        pass