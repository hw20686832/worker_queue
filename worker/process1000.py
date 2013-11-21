#coding:utf-8
import traceback

import redis
import pymongo
import pysolr

from base import ProcesserBase
from lib.index_port.client import pusher
from lib.pushIndexHelper import PushIndexHelper

class Processer(ProcesserBase):
    seq = "p1000"
    
    def __init__(self):
        ProcesserBase.__init__(self)
        self.db = pymongo.Connection("192.168.2.229", 2291).dcrawler_final

        self.solr = pysolr.Solr('http://192.168.2.233:1984/solr/', timeout=10)
        self.helper = PushIndexHelper()
        self.ipusher = pusher()
        
    def process(self, item):
        try:
            self.solr.add([self.helper.constructData(item), ])
        except:
            traceback.print_exc()

        assert self.ipusher.push(item)[0] == "{success:'T'}"
        self.logger.info("item %s push ok." % item['url'])
        
        #self.rd.zadd("avurls:%s" % data['domain'], data['url'], time.time())
        is_exists = self.db.car_info.find_one({'url': data['url']})
        if is_exists:
            self.logger.debug('(%s) old item append %s (%s) to queues.' % (item['domain'], item['url'], item['id']))
        else:
            self.logger.debug('(%s) new item append %s (%s) to queues.' % (item['domain'], item['url'], item['id']))