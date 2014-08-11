'''
Created on Mar 7, 2014

@author: Kei
'''
import re
import time

from PyQt4 import QtCore
from mineline.Events import *



class PreProcessLog(QtCore.QObject):
    '''
    This class is used for importing LINE text log files. This class does the bulk parsing of the log.
    
    The main access to this class should be through processLog()
    '''
    
    
    """
    When the edge case limit is reached during log processing, a ParsingError will be fired
    and indicate that the file is likely not a log.
    """
    EDGECASE_LIMIT = 10  
    
    @classmethod
    def processLog(cls, data, saveTimeZone, progressCallback=None):
        '''
        Takes a log from LINE and parses it into a list of events.
        
        data should be the log as a string.
        saveTimeZone should be a tzinfo representing the timezone of the phone/computer at the time the log
            was created. Without this its impossible to know the timezone and impossible to correctly change
            the times to UTC.
        
        Returns a tuple which contains a list() of events and a string noting the time when the log was saved
            based on the timestamp present at the start of the log.
        '''
        cls.saveTimeZone = saveTimeZone
        cls.progressCallback = progressCallback
        
        log_list = cls.splitLines(data)
        log_list = cls.splitTabsAndCleanBlanks(log_list)
        log_list = cls.convertTimes(log_list)
        
        processed_log, logSaveTime = cls.processLines(log_list)
        
        return (processed_log, logSaveTime)
        pass
    
    @classmethod
    def splitLines(cls, data_str):
        '''
        Breaks the string at CRLFs and builds a list
        
        Returns a list where each entry is an event.
        '''
        cls.updateProgress("Splitting lines. Sorry no progress for this. Please wait.", 99, 100)
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
        
        Returns the modified log_list with each entry in the log_list being a list for the parts of the event.
        '''
        split_lines = list()
        progressCount = 0
        for line in log_list:
            progressCount += 1
            cls.updateProgress("Splitting at Tabs.", progressCount, len(log_list))
            
            if len(line) > 0: # Only add lines with content
                split_lines.append(line.split('\t'))
        return split_lines
    
    @classmethod
    def convertTimes(cls, log_list):
        '''
        Goes through the list adding the date to each event/line and converting each time to UTC. This function will fail
            if splitLines() and splitTabs..() have not been called on it already.
        
        log_list: This is a list with lines and tabs already split
        saveTimeZone: This is a tzinfo representing the timezone of the phone/computer at the time this log was saved.
        
        Returns the modified log_list with all times converted.
        '''
        current_date = None
        expanded_list = []
        progressCount = 0
        for line in log_list:
            progressCount += 1
            cls.updateProgress("Converting Times", progressCount, len(log_list))
            
            if re.search('^[0-9]{,4}/[0-9]{,2}/[0-9]{,2}\(.+?\)', line[0]): # Check for start of new day
                current_date = time.strptime(line[0],"%Y/%m/%d(%A)")
                continue
            if re.search('^[0-9]{1,2}:[0-9]{1,2}', line[0]) != None:
                if current_date == None:
                    raise ParsingError("Current date was not set.")
                else:
                    fixed_hour = cls.__fixHour(line[0])
                    line[0] = time.strftime("%Y/%m/%d",current_date) + " " + fixed_hour
                    line[0] = cls.__convertToUTC(line[0])
            expanded_list.append(line)
        
        return expanded_list
        pass
    
    @classmethod
    def __convertToUTC(cls, time):
        '''
        Convert the current string time from the specified timze zone into UTC timezone.
        
        time: This is a string with a time in format %Y/%m/%d %H:%M
        saveTimeZone: This is a tzinfo for the timezone of the computer/phone that the log file was saved on.
                        Ex: If the phone is set for EST at save, then this needs to be the EST tzinfo.
        '''
        import pytz, datetime
        time_fmt = "%Y/%m/%d %H:%M"
        
        saved_time = datetime.datetime.strptime(time, time_fmt)
        savedWithTZ = cls.saveTimeZone.localize(saved_time)
        saved_dt_utc = savedWithTZ.astimezone(pytz.utc)
        return saved_dt_utc
    
    @classmethod
    def __fixHour(cls,time_str):
        '''
        LINE saves times in the nonstandard form of 1-24 hours. This simply changes 24 to 0
        
        time_str: The time as a string, to fix. Format "HH:MM"
        
        Returns a string with the time fixed if it needed it. Otherwise, its just the same string. 
        '''
        match = re.search(r'(?P<hour>[0-9]{,2})(?P<rest>:[0-9]{,2})',time_str)
        hour = match.group("hour")
        rest = match.group("rest")
        if hour == "24":
            hour = "0"
        return hour + rest
    
    @classmethod    
    def processLines(cls, log_list):
        '''
        This function processes the log_list convertin each event into its representative Event object.
        
        This function will fail if splitLines(), splitTabs..(), and convertTimes() have not already
            been called (in that order).
            
        Returns a list where the strings have been converted into their Events.
        '''
        processed_list = []
        saveTime = None
        progressCount = 0
        edge_count = 0
        for line in log_list:
            progressCount += 1
            cls.updateProgress("Processing log", progressCount, len(log_list))
            
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
                if edge_count < cls.EDGECASE_LIMIT:
                    print "Edge case detected: [" + str(log_list.index(line)) +'] ' + str(line)
                else:
                    raise ParsingError("Edge case limit reached. Please check the file you selected, it may not be a LINE log." +
                                       " If this is incorrect, please file a bug report and include the log file.")
            
            if processed_line != None:
                processed_list.append(processed_line)
        return (processed_list, saveTime)
    
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
        time_dt = cls.__convertToUTC(timeStr)
        return time_dt
    
    @classmethod
    def updateProgress(cls, msg, cur, finish):
        if cls.progressCallback:
            cls.progressCallback.update(msg, cur, finish)
    
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