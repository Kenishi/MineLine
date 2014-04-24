'''
Created on Mar 11, 2014

@author: Kei
'''
from mineline.LineLog import LineLog
from mineline.Events import *
import time, sys
from twisted.test.test_twistd import cProfile

dirpath = '/Users/Kei/Documents/'
filename = '[LINE] Chat in Literal Dickbutt'

class Analysis(object):
    def __init__(self):
        self.__MAX_THREADS = 10
    
    def printFullUserStats(self, linelog):
        user_stats, header = linelog.countUserEvents()
        
        # Print Header
        header_label = "User," + ','.join([x.getEventType() for x in header])
        print header_label
        
        # Print Stats
        for user in user_stats:
            sys.stdout.write(user + ",")
            for event in header:
                sys.stdout.write(str(user_stats[user][event]) + ",")
            sys.stdout.write("\n")

    def velocityOfPriorBins(self, bin_list, prior=1):
        '''
        Takes the average from n_prior to n-1. Shows difference from n and average.
        bin_list: List of bins
        prior: How many prior bins to take the average of when checking.
        
        Returns a list for the velocity of the bin, given the prior
        '''
        if prior < 1:
            raise ValueError("Prior most be >= 1.")
        
        start = end = 0
        output = [0] * len(bin_list)
        for index in range(len(bin_list)):
            start = index - prior
            if start < 0:
                prior_range = bin_list[start:] + bin_list[0:index]
            else:
                prior_range = bin_list[start:index]
            
            prior_avg = float(sum(prior_range))/len(prior_range) if len(prior_range) > 0 else float('nan')
            
            output[index] = bin_list[index] - prior_avg
        
        return output
            
        
    def createCountBinsFromTime(self, linelog, include_events=None, bins=144):
        '''
        Create a frequency count based on bin amount and time (in minutes).
        Ex1: Events counted for 10-min interval would be bin=144. 1440min in a day/10min
        Ex2: 30-min Interval would be bin=48. 1440min in a day/30min.
        
        events: List of events as type() to filter for. None means all events
        bins: Number of bins to create. Valid: 1-1440 
        Returns a list with a range(0,bin) of number of events that occured in that interval.
        ValueError: Thrown when bin number is outside valid range.
        '''
        if bins < 1 or bins > 1440:
            raise ValueError("Invalid range for bins (1-1440).")
        
        # Collect events
        events = []
        if include_events:
            events = linelog.getEvents(include_events)
        else:
            events = linelog.getEvents(EnumEvents.events)
        
        # Count events
        output = [0] * bins
        time_interval = 1440/bins
        for event in events:
            time_struc = time.strptime(event.getTime(), "%Y/%m/%d %H:%M")
            hour = int(time.strftime("%H", time_struc))
            minute = int(time.strftime("%M", time_struc))
            bin_index = ((hour*60) + minute)/time_interval
            output[bin_index] += 1
        
        return output
        
    def hoursOfDayTest(self,linelog):
        ## Hours of Day
        hour_count = analyze.createCountBinsFromTime(linelog, [MessageEvent,PhotoEvent,StickerEvent], 24)
       
        header = ""
        str_out = ""
        for x in range(24):
            header += str(x) + ","
            str_out  += str(hour_count[x]) + ","
        print "1-hour Bin Count"
        print header
        print str_out
        pass

    def tenMinBinCount(self, linelog):
        ## 10-min bins
        count = analyze.createCountBinsFromTime(linelog, [MessageEvent,PhotoEvent,StickerEvent], 144)
        header = ""
        str_out = ""
        for x in range(144):
            header += str(x) + ","
            str_out += str(count[x]) + ","
        print "10-Min Bin Count"
        print header
        print str_out

    def velocityTest(self, linelog):
        ## Velocity of 10-min intervals. Priors = 3
        count = analyze.createCountBinsFromTime(linelog, [MessageEvent, PhotoEvent, StickerEvent], 144)
        velocity = analyze.velocityOfPriorBins(count, 3)
        header = ""
        str_out = ""
        for x in range(len(count)):
            header += str(x) + ","
            str_out += str(velocity[x]) + ","
        print "Velocity of 10-Min Bin Count with Prior=3"
        print header
        print str_out

    def freqDisp(self, linelog):
        from nltk.probability import FreqDist
        from nltk import pos_tag
        import futures
        
        fdist = FreqDist()
        count = 0
        results = []
        taggerFutures = []
        # Tag the POS using threading
        for event in linelog.getEvents([MessageEvent]):
            samples = event.getMessage().lower().split()
                    
            with futures.ThreadPoolExecutor(max_workers=20) as executor:
                # Feed the sent to tag into executor
                taggerFutures.append(executor.submit(pos_tag, samples))
            if (count % 1000) == 0:
                print "Count: " + str(count)
            count += 1
        
                
        vocab = fdist.items()
        print str(vocab[:50])
        pass
    
    def freqDispByUsers(self, linelog, pos_tag=["NN"]):
        from nltk import pos_tag
        from nltk.probability import FreqDist
        
        users = {}
        for event in linelog.getEvents([MessageEvent]):
                if event.getUser not in users: 
                    users[event.getUser()] = FreqDist()
                words = event.getMessage().lower().split()
                words_tag = pos_tag(words)
                for word, tag in words_tag:
                    if tag == "NN":
                        users[event.getUser()].inc(word)
        return users
      
if __name__ == '__main__':
    linelog = None
    import os.path
    if os.path.isfile(dirpath + filename + ".data"):
        linelog = LineLog.fromPickle(dirpath + filename + ".data")
    else:
        linelog = LineLog.fromFilename(dirpath + filename + ".txt")
        linelog.pickleLog(dirpath + filename + ".data")
   
    analyze = Analysis() 

    ## Hours of Day
    #hoursOfDayTest(linelog)
    ## 10-min bins
    #tenMinBinCount(linelog)
    ## Velocity 
    #velocityTest(linelog)
    analyze.freqDisp(linelog)
    """
    fdistUsers = freqDispByUsers(linelog)
    data = fdistUsers["i am ok"].items()
    print data[:50]
    """
    

    