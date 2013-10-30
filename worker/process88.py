#encoding:utf-8
"""
电话号码解析
"""
from base import ProcesserBase
import redis,json
from scrapy.http import Request
from scrapy.utils.reqser import request_to_dict
from lib.models import Flow

class processer(ProcesserBase):
    seq = "p88"
    
    def __init__(self):
        ProcesserBase.__init__(self) 
        redis_host = '192.168.2.219'  # change later
        redis_port = 6379
        redis_db = 4
        self.server = redis.Redis(redis_host, redis_port, redis_db)
        
    def dump_url(self,url,spider,rec_url):
         req = Request(url)
         flowid = "phoneflow-" + spider
         req.meta['flow'] = flowid
         req.meta['rule'] = 0
         req.meta['cd'] = {'rec_url': rec_url,
                           "spider": spider}  # client data
#        req.headers["Referer"] = "http://www.autoimg.cn/"
         d = request_to_dict(req)
         data = json.dumps(d)
         flow=Flow(self.server, flowid)
#         print 2132
         flow.q_push(data)
         
    def process(self,data):
        
        if data["contact_phone"].startswith("http"):
            self.dump_url(data["contact_phone"],data["spider"],data["url"])
        
        if data["contact_mobile"].startswith("http"):
            self.dump_url(data["contact_mobile"],data["spider"],data["url"])
        
        return  data

if __name__ == '__main__':
    ps=processer()
    ps.work()
    
