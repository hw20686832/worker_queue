#encoding:utf-8
"""
推送图片抓取队列
"""
import os
import re
import hashlib

import redis
import pymongo
from lib.fastdfsImage import imagedb
from base import ProcesserBase

_sites = {"51huanche.com": "http://51huanche.com",
          "usedcar.com": "http://www.55usedcar.com",
          "tzqiche.com": "http://tzqiche.com",
          "yzjdc.com": "http://yzjdc.com"}

class Processer(ProcesserBase):
    """This process handles image download."""
    seq = "p99"
    
    def __init__(self):
        ProcesserBase.__init__(self)
        redis_host = '122.192.66.45'  #将图片队列放入远程
        redis_port = 6379

        self.server_img = redis.Redis(redis_host, redis_port, 1)
        self.server_img3 = redis.Redis(redis_host, redis_port, 3)
        conn229 = pymongo.Connection('192.168.2.229',2291)
        self.db = conn229['dcrawler_final']

        self.remoteImagedb = imagedb()#查询远程图片信息的thrift客户端


    def process(self, data):
        page = data['url']
        self.logger.debug('incoming: %s'%page)
        self.number = 0
        if data['car_images']=="" and data['car_img_thumb']!="":
            data['car_images']= data['car_img_thumb']
            
        img_urls = self.extract_image_urls(data['car_images'])
        new_img_urls=[]
        if "iautos" in data['domain']:
            for url in img_urls:
                if url.endswith(".gif") or url.endswith("noPic.jpg"):
                    continue
                try:
                    if not url.startswith("http://"):
                        url = "http://photo.iautos.cn/carupload/photo/%s/%s/%s"%(url[:4],url[4:8],url)
                    new_img_urls.append(url)
                except:
                    continue
        elif data['domain'] in _sites:
                for url in img_urls:
                    if url.endswith(".gif") or url.endswith("noPic.jpg"):
                        continue
                    try:
                        if not url.startswith("http://"):
                            url = ''.join(_sites[data["domain"]], url.replace("..",""))
                        new_img_urls.append(url)
                    except:
                        continue
        else:
            img_urls = [self.translate_url(url) for url in img_urls]
            for url in img_urls:
                if url.endswith(".gif") \
                       or url.endswith("noPic.jpg") \
                       or url.endswith("images/zwtp.jpg") \
                       or url.endswith("car_defaultmaxpic.jpg") \
                       or url.endswith("car/images/car.jpg") \
                       or url.endswith("images/car_img.jpg") \
                       or url.endswith("images/16.jpg") \
                       or url.endswith("tupianban.jpg"):
                    continue
                new_img_urls.append(url)

        image_seq = 0
        for url in new_img_urls:
            md5 = hashlib.md5()
            md5.update(url)
            url_md5 = md5.hexdigest()
            filename = url_md5.upper()
            if not (self.server_img.exists(filename) or self.remoteImagedb.getImageInfo(filename)):#正在抓取的不重复加入队列#抓取成功的不加入队列
                self.logger.debug('%s is not crawled'%url)
                self.process_img_url(url, data['url'], data['domain'], data['process'], data['id'], seq=image_seq)
            else:
                self.logger.debug('%s is in crawling queue or crawled'%url)
            if image_seq == 0:
                img_url = self.get_default_thumbnail_filename(url)
                data["car_img_thumb"] = img_url
            image_seq += 1
        
        if not data["car_img_thumb"].count("_thumb")>0:
            data["car_img_thumb"] = ""
        new_img_urls = "###".join(new_img_urls)   
        data["car_images"] = new_img_urls

        #存储到数据库，因为接下来的步骤是图片抓取等待的队列
        original_data = {}
        original_data= data.copy()
        self.db.car_info.update({'url': data['url']}, data, True, True)
        return original_data
    
    def get_default_thumbnail_filename(self, filename):
        path, ext = os.path.splitext(filename)
        return "%s_thumb%s" % (path,ext)

    def extract_image_urls(self, url_str):
        s = re.split('#+', url_str)
        return [url for url in s if url]
    
    repl_patterns = (
        (r'http://pic.kuche.com/(.*)/small/(.*)', r'http://pic.kuche.com/\1/big/\2'),
        (r'http://(.*).pic.58control.cn/(.*)/tiny/(.*)', r'http://\1.pic.58control.cn/\2/big/\3'),
        (r'http://www.2duche.com/picture/(.*)/thumb/(.*)', r'http://www.2duche.com/picture/\1/normal/\2'),
        (r'http://img.273.com.cn/(.*)_266x200(.*)',r'http://img.273.com.cn/\1\2'),
        (r'http://www.273.cn/(.*)_266x200(.*)',r'http://www.273.cn/\1\2'),
        (r'/picture/(.*)/thumb/(.*)', r'http://www.2duche.com/picture/\1/normal/\2'),
        (r'/upload/(.*)/mid_img/(.*)', r'http://www.9che.com/upload/\1/mid_img/\2'),
        (r'http://www.9che.com/upload/(.*)/cache_img/(.*)', r'http://www.9che.com/upload/\1/mid_img/\2'),
        (r'http://(.*)baixing.net/(.*)_sm(.*)', r'http://\1baixing.net/\2\3'),
        (r'http://image.ganjistatic1.com/(.*)\_(.*)\-(.*)\_(.*)', r'http://image.ganjistatic1.com/\1_800-600_\4'),
        (r'http://www.hx-car.com/(.*)small(.*)', r'http://www.hx-car.com/\1large\2'),
        (r'^/zd/carsphoto/(.*)', r'http://www.socars.cn/zd/carsphoto/\1'),
        (r'(.*)taotaocar.com/UploadFile_/(.*)\_sml(.*)', r'http://upload.taotaocar.com/UploadFile_/\2\3'),
        (r'http://www.zg2sc.cn/upfile/carpo/(.*)sm(.*)', r'http://www.zg2sc.cn/upfile/carpo/\1wm\2'),
        (r'/upload/(\d+)/s(\d+)\.(.*)', r'http://www.4c27.com/upload/\1/\2.\3'),
    )
    
    def translate_url(self, url):
        # special rules to translate url into a good one
        for pat in self.repl_patterns:
            url = re.sub(pat[0], pat[1], url)
        return url
    
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


if __name__ == '__main__':
    ps = Processer()
    ps.work()
