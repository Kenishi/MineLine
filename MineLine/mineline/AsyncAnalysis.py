'''
Created on Mar 20, 2014

@author: Kei
'''
from threading import Thread


class PoSTagger(Thread):
    '''
    Class that provides some functions/operations in multi-threads
    '''
    def __init__(self, data):
        self.kwargs = data
        Thread.__init__(kwargs=data)
    
    def run(self):
        import nltk
        if not self.kwargs["sent"]:
            raise RuntimeError("PosTagger expected 'sent' in the arguments, but it didn't find it.")
        
        sent = self.kwargs["sent"]
        self.result = nltk.pos_tag(sent)
        pass