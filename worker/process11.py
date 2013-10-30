#encoding:utf-8
"""
负责精确字段的数据清洗，例如：整数类型字段，时间类型字段
"""
from base import ProcesserBase
from lib.common import switch
from lib import FieldArrange

class processer(ProcesserBase):
    seq = "p11"
    
    def __init__(self):
        ProcesserBase.__init__(self)        
    
    def process(self,data):
        spider = data['spider']
        for case in switch(spider):
            if case('58'):
                pass
            if case('9che'):
                pass
            if case('ucar'):
                #data['car_birth']=FieldArrange._ucar_carbirth(data['car_birth'])
                pass
            if case():
                pass 
        
        if data.has_key("car_birth"):
            #汽车出厂日期规整化
            car_birth = FieldArrange._car_birth(data['car_birth'])
            data['car_birth'] = car_birth
        
        #汽车排量规整化，隐含单位：L
        if data.has_key("car_emission"):
            car_emission = FieldArrange._fitch_emission(data['car_emission'])
            data['car_emission'] = car_emission
        
        #汽车里程数规整化，隐含单位：万公里
        if data.has_key("car_mileage"):
            car_mileage = FieldArrange._fitch_emission(data['car_mileage'])
            data['car_mileage'] = car_mileage
        
        #新车购买价规整化，隐含单位：万元
        if data.has_key("purchase_price"):
            purchase_price = FieldArrange._fitch_purchase_price(data['purchase_price'])
            data['purchase_price'] = purchase_price
       
        #原车购买日期规整化 
        if data.has_key("purchase_date"):
            purchase_date = FieldArrange.arg_purchase_date(data['purchase_date'])
            data['purchase_date'] = purchase_date   
        return  data
    
if __name__ == '__main__':
    ps=processer()
    ps.work()
    
