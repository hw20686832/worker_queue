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
from lib.integrity import get_integrity
from lib.fastdfsImage import imagedb

class Processer(ProcesserBase):
    seq = "p990"
    
    def __init__(self):
        ProcesserBase.__init__(self)
        self.rdb3 = redis.Redis(host='122.192.66.45', db=3)
        # 查询远程图片信息的thrift客户端
        self.remoteImagedb = imagedb()
        # 推送索引
        self.ipusher = pusher()

    def atlst1imageCrawled(self,img_urls):
        """判断至少有一张图片抓取完成"""
        ret = False
        for url in img_urls:
            filename = md5(url).hexdigest().upper()
            # 查询远端的fastdfs图片数据库
            if self.remoteImagedb.getImageInfo(filename):
                ret = True
                break
        return ret

    def atlstNImagesCrawled(self,img_urls,n):
        """判断至少有n张图片抓取完成"""
        ret = False
        c = 0
        for url in img_urls:
            filename = md5(url).hexdigest().upper()
            # 查询远端的fastdfs图片数据库
            if self.remoteImagedb.getImageInfo(filename):
                c += 1
                if c >= n:
                    ret = True
                    break
            if n > len(img_urls) == c:
                ret = True
        return ret

    def process(self, data):
        # detect whether one picture downloaded at least
        # 只有图片队列还有值的时候才有必要判断本条数据的图片是否已经抓完
        img_urls = [url for url in re.split('#+', data['car_images']) if url]
        if self.rdb3.exists('image:queue'):
            if data.get('car_images') or data.get('car_img_thumb'):
                # 下载的图片少于4张
                if not self.atlstNImagesCrawled(img_urls, 4):
                    self.logger.debug('%s still in image crawling, ignore it.' % data['url'])
                    if int(time.time()*1000) - data['updated'] >= 1000*3600*24*3:
                        self.logger.debug('%s picture crawling expired!' % data['url'])
                        data['car_images'] = ''; data['car_img_thumb'] = ''
                    else:
                        self.logger.debug('%s still in image crawling, ignore it.' % data['url'])
                        data['updated'] = int(time.time()*1000)
                        self.sendMyself.send(data)
                        return
                else:
                    self.logger.debug('%s has picture . nice ~' % data['url'])
            else:
                self.logger.debug('%s has no image. ' % data['url'])
        else:
            self.logger.debug("Queue(image:queue) no exists, url: %s." % data['url'])

        # 临时增补
        data['car_img_server'] = 'AUTO'
        #real_img_count = len([img for img in img_urls if self.mdb.exists(md5(url).hexdigest().upper())])
        real_img_count = len(img_urls)
        data['integrity'] = get_integrity(data, real_img_count)

        return data
