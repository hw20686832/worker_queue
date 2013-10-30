#encoding:utf-8
'''
Created on 2012-7-3

@author: James
'''
import logging
import logging.handlers
import os
from handlers import MongoHandler

class logger(object):
    '''
    python logging, save to mongodb
    '''
    def __init__(self, loggername='track', logfile=True, logfilepath=None, logstream=True):
        
        logger = logging.getLogger('track')
        formatter = logging.Formatter('[%(asctime)s %(name)s %(levelname)s]=> %(message)s',datefmt="%Y-%m-%d %H:%M:%S")
        
        if logfile:
            if logfilepath is None:
                logfinaname = 'log/%s.%s.log' % (loggername, os.getpid())
            else:
                logfinaname = logfilepath
            hdlr = logging.handlers.TimedRotatingFileHandler(logfinaname, when='midnight',interval=1, backupCount=30, encoding=None, delay=0, utc=0)
            hdlr.setFormatter(formatter)
            logger.addHandler(hdlr)
            
        if logstream:
            hdst = logging.StreamHandler()
            hdst.setFormatter(formatter)
            logger.addHandler(hdst)
            
        logger.setLevel(logging.DEBUG)
        self.logger = logger
        
    def getLogger(self):
        '''
        return logger
        '''
        return self.logger
