#encoding:utf-8
"""
判断主要字段是否丢失
"""
from base import ProcesserBase
from lib import Process66Main
import pymongo
from lib.droping_rabbitmq import dr
import time

lucene_index_service = 'http://192.168.2.232:8080/solr/index/delete'
contact_keys=["contact_phone","contact_mobile","contact_mail","contact_qq"]#联系方式或查询
source_keys=["source_province","source_zone"]#地区或查询
brand_keys=["car_brand","car_series"]#地区或查询

class processer(ProcesserBase):
    """主要字段的规整化、涉及到分词提取"""
    seq = "p66"
    
    def __init__(self):
        ProcesserBase.__init__(self)

    def process(self, data):
 
        is_lose = Process66Main._is_car_title_lose(data['car_title'])  
        if is_lose:
            dr.insert_data(data)
            self.logger.debug("(%s) Item ignore, lose car_title." % data['domain'])
            return None
        
        is_lose = Process66Main._is_car_brand_car_series_lose(data['car_brand'], data['car_series'])  
        if is_lose:
            dr.insert_data(data)
            self.logger.debug("(%s) Item ignore, lose car_series." % data['domain'])
            return None
       
        is_lose = Process66Main._is_car_price_lose(data['car_price']) 
        if is_lose:
            dr.insert_data(data)
            self.logger.debug("(%s) Item ignore, lose car_price." % data['domain'])
            return None

        is_lose = Process66Main._is_contact_phone_contact_mobile_contact_mail_contact_qq_lose(data['contact_phone'], data['contact_mobile'], data['contact_mail'], data['contact_qq'])
        if is_lose:
            dr.insert_data(data)
            self.logger.debug("(%s) Item ignore, lose contact." % data['domain'])
            return None
        
        is_lose = Process66Main._is_source_province_source_zone_lose(data['source_province'], data['source_zone'])
        if is_lose:
            dr.insert_data(data)
            self.logger.debug("(%s) Item ignore, lose source." % data['domain'])
            return None
        time.sleep(0.08)

        return  data
    
if __name__ == '__main__':
    ps = processer()
    ps.work()
    
