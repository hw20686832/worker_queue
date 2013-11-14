# coding: utf-8
"""
删除完全重复内容
"""
import hashlib

import redis

from lib.droping_rabbitmq import dr
from base import ProcesserBase
    
class processer(ProcesserBase):
    seq = "p77"
    
    def __init__(self):
        ProcesserBase.__init__(self)   
        redis_host = '192.168.2.228'
        redis_port = 6381
        self.rd7 = redis.Redis(redis_host, redis_port, db=7)

    def process(self, data):
        """
        经与周晔、技术讨论，对排重规则进行调整：
        定义在车源标题、车型、里程数、地区、联系方式、价格、车龄都完全相同的车源，为重复车源
        在前台隐藏不展示，但数据库中不删除，便于后续数据分析
        """
        keys = ("car_title", "car_type", "car_mileage",
                "car_price", "car_birth", "source_province", "source_zone")
        m = hashlib.md5()
        for key in keys:
            if type(data[key]) == unicode:
                mk = data[key].encode('utf-8')
            else:
                mk = str(data[key])
            m.update(mk)
        signature = m.hexdigest()

        if self.rd7.exists(signature):
            for contact in (data["contact_mobile"], data["contact_phone"]):
                if self.rd7.sismember(signature, contact):
                    dr.insert_data(data)
                    self.logger.debug("(%s) has been droped by process77 %s." % (data['domain'], data['url']))
                    return None

        self.rd7.sadd(signature, data["contact_mobile"], data["contact_phone"])
        return data

if __name__ == '__main__':
    ps = processer()
    ps.work()
    
