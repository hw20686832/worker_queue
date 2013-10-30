#encoding:utf-8
"""
负责精确字段的数据清洗，例如：整数类型字段，时间类型字段
"""
from base import ProcesserBase
from lib import Process12Main

class processer(ProcesserBase):
    seq = "p12"
    
    def __init__(self):
        ProcesserBase.__init__(self)
    
    def process(self,data):
        
        if data.has_key("car_frame"):
            car_frame = Process12Main._car_frame(data['car_frame'])
            data['car_frame'] = car_frame
        
        if data.has_key("car_enter_time"):
            car_enter_time = Process12Main._date_time(data['car_enter_time'])
            data['car_enter_time'] = car_enter_time
        
        if data.has_key("car_inspection_date"):
            car_inspection_date =   Process12Main._date_time(data['car_inspection_date'])
            data['car_inspection_date'] = car_inspection_date
        
        if data.has_key("car_reg_time"):
            car_reg_time = Process12Main._date_time(data['car_reg_time'])
            data['car_reg_time'] = car_reg_time
        
        if data.has_key("car_insur_validity"):
            car_insur_validity = Process12Main._date_time(data['car_insur_validity']) 
            data['car_insur_validity'] = car_insur_validity
        
        if data.has_key("car_deadweight"):
            car_deadweight = Process12Main._car_deadweight(data['car_deadweight'])
            data['car_deadweight'] = car_deadweight
        
        if data.has_key("car_doors"):
            car_doors = Process12Main._car_doors(data['car_doors'])
            data['car_doors'] = car_doors
        
        if data.has_key("car_seats"):
            car_seats = Process12Main._car_seats(data['car_seats'])
            data['car_seats'] = car_seats
        
        if data.has_key("car_cylinder"):
            car_cylinder = Process12Main._car_cylinder(data['car_cylinder'])
            data['car_cylinder'] = car_cylinder
            
        if data.has_key("source_validity"):
            source_validity = Process12Main._source_validity(data['source_validity'])
            data['source_validity'] = source_validity

        return  data
    
if __name__ == '__main__':
    ps=processer()
    ps.work()
    
