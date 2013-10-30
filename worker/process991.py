#coding: utf-8
"""
向lucene发送数据索引，如果图片还在抓取中则传给下一个
"""
import re
import time
from hashlib import md5

import pymongo
import redis

from base import ProcesserBase
from lib.index_port.client import pusher
from lib.RabbitMQ import MessageClient
from lib.integrity import get_integrity
from lib.fastdfsImage import imagedb

class Processer(ProcesserBase):
    seq = "p991"
    
    def __init__(self):
        ProcesserBase.__init__(self)

        self.rdb3 = redis.Redis(host='122.192.66.45', db=3)
        self.rd = redis.Redis(host="192.168.2.228", db=6)
#        self.mdb = redis.Redis(host="192.168.2.233")
        conn = pymongo.Connection('192.168.2.229', 2291)
        self.db = conn.dcrawler_final
        self.remoteImagedb = imagedb()#查询远程图片信息的thrift客户端
        self.ipusher = pusher()#推送索引

        self.sendMyself = MessageClient({'server': self.rabbitmq_server,
                                         'vhost': self.rabbitmq_virtual_host,
                                         'user': self.rabbitmq_auth_user,
                                         'password': self.rabbitmq_auth_pwd,
                                         'exchange': self.exchange_name,
                                         'outKey': self.in_routing_key,
                                         'outQueue': self.in_queue_name})

    def atlst1imageCrawled(self,img_urls):
        '''
        判断至少有一张图片抓取完成
        '''
        ret = False
        for url in img_urls:
            filename = md5(url).hexdigest().upper()
            if self.remoteImagedb.getImageInfo(filename):#查询远端的fastdfs图片数据库
                ret = True
                break
        return ret

    def atlstNImagesCrawled(self,img_urls,n):
        '''
        判断至少有n张图片抓取完成
        '''
        ret = False
        c = 0
        for url in img_urls:
            filename = md5(url).hexdigest().upper()
            if self.remoteImagedb.getImageInfo(filename):#查询远端的fastdfs图片数据库
                c += 1
                if c>=n:
                    ret = True
                    break
            if n > len(img_urls) == c:
                ret = True
        return ret

    def process(self, data):
        # detect whether one picture downloaded at least
        img_urls = [url for url in re.split('#+', data['car_images']) if url]
        # 只有图片队列还有值的时候才有必要判断本条数据的图片是否已经抓完
        if self.rdb3.exists('image:queue'):
            hasImg = ''
            if data.has_key('car_images'):
                hasImg = data['car_images']
            if data.has_key('car_img_thumb'):
                hasImg = hasImg + data['car_img_thumb']
            if hasImg:
                if not self.atlstNImagesCrawled(img_urls,4):#下载的图片少于4张
                    if int(time.time()*1000) - data['updated'] >= 1000*3600*24*3:
                        self.logger.debug('%s picture crawling expired!' % data['url'])
                        data['car_images'] = ''
                        data['car_img_thumb'] = ''
                    else:
                        self.logger.debug('%s still in image crawling, ignore it.' % data['url'])
                        self.sendMyself.send(data)
                        return
                else:
                    self.logger.debug('%s has picture ,nice!' % data['url'])
            else:
                self.logger.debug('%s has no image. ' % data['url'])
        else:
            self.logger.debug("Queue(image:queue) no exists, url: %s." % data['url'])

        # 临时增补
        data['car_img_server'] = 'AUTO'
        real_img_count = None
        if data['car_images'] == '':
            real_img_count = 0
        else:
#            real_img_count = len([img for img in img_urls if self.mdb.exists(md5(url).hexdigest().upper())])
            real_img_count = len(img_urls)
        data['integrity'] = get_integrity(data, real_img_count)

        if data['integrity'] == 0:
            self.logger.warning("Integrity is 0!!!, url: %s" % data['url'])
        if self.ipusher.push(data)[0] != "{success:'T'}":
            self.sendMyself.send(data)
        
        self.logger.info("item %s push ok." % data['url'])
        self.rd.zadd("avurls:%s" % data['domain'], data['url'], time.time())
        is_exists = self.db.car_info.find_one({'url': data['url']})
        if is_exists:
            self.logger.debug('(%s) old item append %s (%s) to queues.' % (data['domain'], data['url'], data['id']))
        else:
            self.logger.debug('(%s) new item append %s (%s) to queues.' % (data['domain'], data['url'], data['id']))


if __name__ == '__main__':
    ps = Processer()
    ps.work()

