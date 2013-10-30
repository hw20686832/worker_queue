#encoding:utf-8
"""
生成短url、删除90天以前的信息、判断新旧数据
"""
from base import ProcesserBase
import pymongo,redis,datetime
from time import time
import lib.ShortUrl as ShortUrl
import hashlib

class processer(ProcesserBase):
    seq = "p89"
    
    def __init__(self):
        ProcesserBase.__init__(self) 
        mongodb_host = '192.168.2.229'
        mongodb_dbname = 'dcrawler_final'
        conn = pymongo.Connection(mongodb_host,2291)
        self.db = conn[mongodb_dbname]
        self.data_queues = [] #data queues preparing index

    
    def process(self,data):
        #删除_id，如果没有id就添加
        if data.has_key('_id'):
            if not data.has_key('id'):
                data['id']=data['_id']
            del data['_id']
        #生成短url
        myshorturl = ShortUrl.shorturl(data['url'])
        if myshorturl is None:
            md5 = hashlib.md5()
            md5.update(data['url'])
            myshorturl = md5.hexdigest()
        data['shorturl'] = myshorturl
#        self.logger.debug('short url: %s --> %s '%(data['url'],myshorturl))
        updated = int(time()*1000)
        data['updated'] = updated

#        car_info=self.db['car_info'].find_one({'url':data['url']})
#        if car_info:
##            statisdata.deal_info_updated(data["spider"])
#            self.logger.info('%s processed %s' % (self.getCallerModuleName(),data['id']),extra={'id':data['id'],'url':data['url'],'processer': self.getCallerModuleName(),"spider":data["spider"],"flow":data["process"],'category':'deal_update'})
#        else:
##            statisdata.deal_info_inserted(data["spider"])
#            self.logger.info('%s processed %s' % (self.getCallerModuleName(),data['id']),extra={'id':data['id'],'url':data['url'],'processer': self.getCallerModuleName(),"spider":data["spider"],"flow":data["process"],'category':'deal_insert'})
        data['process'] = 'indexed'
        return  data
        
if __name__ == '__main__':
    ps=processer()
    ps.work()
    
