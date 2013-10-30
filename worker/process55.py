#encoding:utf-8
"""
主要对所有的时间进行长整型转化
"""
from base import ProcesserBase
import time,datetime 

class processer(ProcesserBase):
    """主要对所有的时间进行长整型转化"""
    seq = "p55"
    
    def __init__(self):
        ProcesserBase.__init__(self)        
    
    def process(self,data):
        now = datetime.datetime.now()
        now = now.strftime('%Y')
        keys=["car_enter_time","car_reg_time","purchase_date","car_birth"]
        car_age=0
        for key in keys:
            if  data.has_key(key) and (data[key] is not None and data[key]!=""):
                try:
                    car_age=data[key][:4]
                except:
                    continue
                break
            else:
                continue
        if car_age==0:
            data["car_age"]=0
        else:
            data["car_age"]=(int(now)-int(car_age))
        
  
        return  data
    
if __name__ == '__main__':
    ps=processer()
    ps.work()
    
    
    
    
    
