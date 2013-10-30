#encoding:utf-8
"""
主要对所有的时间进行长整型转化
"""
from base import ProcesserBase
import time,datetime 

class processer(ProcesserBase):
    """主要对所有的时间进行长整型转化"""
    seq = "p56"
    
    def __init__(self):
        ProcesserBase.__init__(self)        
    
    def process(self,data):
        
        car_birth = _date(data['car_birth'])
        data['car_birth'] = car_birth
        
        purchase_date = _date(data['purchase_date'])
        data['purchase_date'] = purchase_date
        
        car_reg_time = _date(data['car_reg_time'])
        data['car_reg_time'] = car_reg_time
        
        car_enter_time = _date(data['car_enter_time'])
        data['car_enter_time'] = car_enter_time
        
        source_birth = _date(data['source_birth'])
        data['source_birth'] = source_birth
        
        car_insur_validity = _date(data['car_insur_validity'])
        data['car_insur_validity'] = car_insur_validity
        
        car_inspection_date = _date(data['car_inspection_date'])
        data['car_inspection_date'] = car_inspection_date
        
        return  data

def _date(data):
    if (data is not None) or data!="":
        try:
            if len(data)<12:
                a=time.strptime(data,'%Y-%m-%d')
            else:
                a=time.strptime(data,'%Y-%m-%d %H:%M:%S')
            day=datetime.datetime(*a[:6]);
            long_time = int(time.mktime(day.timetuple())*1000)
        except:
            return 0
        return long_time
    else:
        return 0
    
if __name__ == '__main__':
    ps=processer()
    ps.work()
    
