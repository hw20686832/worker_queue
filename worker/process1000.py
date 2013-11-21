#coding:utf-8
import redis
import pymongo

from lib import solr
from base import ProcessBase

class Processer(ProcessBase):
    seq = "p1000"
    
    def __init__(self):
        ProcesserBase.__init__(self)
        self.db = pymongo.Connection("192.168.2.229", 2291).dcrawler_final
        
    def process(self, item):
        solr.add(data)
        self.logger.info("item %s push ok." % data['url'])
        
        #self.rd.zadd("avurls:%s" % data['domain'], data['url'], time.time())
        is_exists = self.db.car_info.find_one({'url': data['url']})
        if is_exists:
            self.logger.debug('(%s) old item append %s (%s) to queues.' % (data['domain'], data['url'], data['id']))
        else:
            self.logger.debug('(%s) new item append %s (%s) to queues.' % (data['domain'], data['url'], data['id']))