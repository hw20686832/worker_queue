#coding:utf-8
"""
推送图片抓取队列
"""
import os
import re
from hashlib import md5

import redis
import pymongo

from lib.fastdfsImage import imagedb
from base import ProcesserBase

class Processer(ProcesserBase):
    """This process handles image download."""
    seq = "p99"
    
    def __init__(self):
        ProcesserBase.__init__(self)
        # 远程图片队列
        redis_host = '122.192.66.45'
        redis_port = 6379

        self.server_img = redis.Redis(redis_host, redis_port, 1)
        self.server_img3 = redis.Redis(redis_host, redis_port, 3)
        conn229 = pymongo.Connection('192.168.2.229',2291)
        self.db = conn229['dcrawler_final']

        # 查询远程图片信息的thrift客户端
        self.remoteImagedb = imagedb()

    def process(self, data):
        self.number = 0
        if data['car_images'] == "" and data['car_img_thumb'] != "":
            data['car_images'] = data['car_img_thumb']
            
        img_urls = self.extract_image_urls(data['car_images'])
        new_img_urls = [self.translate_url(url) for url in img_urls]
        
        image_seq = 0
        for url in new_img_urls:
            filename = md5(url).hexdigest().upper()
            # 正在抓取的不重复加入队列#抓取成功的不加入队列
            if not (self.server_img.exists(filename) or self.remoteImagedb.getImageInfo(filename)):
                self.logger.debug('%s is not crawled' % url)
                self.process_img_url(url, data['url'], data['domain'], data['process'], data['id'], seq=image_seq)
            else:
                self.logger.debug('%s is in crawling queue or crawled' % url)
            if image_seq == 0:
                img_url = self.get_default_thumbnail_filename(url)
                data["car_img_thumb"] = img_url
            image_seq += 1
        
        if not data["car_img_thumb"].count("_thumb") > 0:
            data["car_img_thumb"] = ""
            
        new_img_urls = "###".join(new_img_urls)
        data["car_images"] = new_img_urls

        #存储到数据库，因为接下来的步骤是图片抓取等待的队列
        #original_data = {}
        #original_data= data.copy()
        #self.db.car_info.update({'url': data['url']}, data, True, True)
        return data
    
    def get_default_thumbnail_filename(self, filename):
        path, ext = os.path.splitext(filename)
        return "%s_thumb%s" % (path, ext)

    def extract_image_urls(self, url_str):
        s = re.split('#+', url_str)
        return [url for url in s if url]
    
    def push_redis(self, url, rec_url, referer):
        # 把图片加入redis
        url_md5 = hashlib.md5(url).hexdigest().upper()
        if self.server_img.hlen(url_md5) == 0:
            smap = {"url": url, "referer": referer, "page_url": rec_url}
            if self.number == 1:
                smap["thumb"] = True
            self.server_img.hmset(url_md5, smap)
            self.server_img.expire(url_md5, 24*3600)
            self.server_img3.rpush("image:queue", url)
            self.logger.debug("image url inqueue: %s" % url)

    def process_img_url(self, url, rec_url, domain, flow, id, seq):
        if url.startswith("http"):
            Referer = ""
            if domain == "che168.com":
                Referer = "http://www.autoimg.cn/"
            self.number += 1
            self.push_redis(url, rec_url, Referer)
