#encoding:utf-8
"""
提取新车价格
"""
import time,datetime
from base import ProcesserBase
from lib.brand_price import brand_price
from lib.Arrange44 import car_outer_color,car_style,car_inner_color
from lib import ArrangeMain

class processer(ProcesserBase):
    """提取新车价格"""
    seq = "p44"
    
    def __init__(self):
        ProcesserBase.__init__(self)
    
    def process(self,data):
        
        if data['spider']=='58':
            #从新车价格描述中提取原始购买价（仅58）
            purchase_price = ArrangeMain._58_fetch_purchase_price_from_car_price(data['car_price'])
            data['purchase_price'] = purchase_price
        
        car_price = ArrangeMain._car_price(data['car_price'])
        data['car_price'] = car_price
        
        #提取新车价格
        key=u"%s#%s"%(data["car_brand"],data["car_series"])
        if not data.has_key("purchase_price_refer"):
            data['purchase_price_refer']=0
        purchase_price_refer =brand_price[key] if brand_price.has_key(key) else 0
        data['purchase_price_refer'] = purchase_price_refer
        
        color=car_outer_color(data["car_outer_color"])
        data["car_outer_color"]=color
        
        color=car_inner_color(data["car_inner_color"])
        data["car_inner_color"]=color
       
        style=car_style(data["car_style"],data["car_type"])
        data["car_style"]=style
        
        return  data
    
if __name__ == '__main__':
    ps=processer()
    ps.work()
  
