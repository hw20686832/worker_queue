#encoding:utf-8
"""
文本字段的规整化
"""
from base import ProcesserBase
from lib.common import switch
from lib import FieldArrange

class processer(ProcesserBase):
    seq = "p13"
    
    def process(self,data):        
        spider = data['domain']
        for case in switch(spider):
            if case('58.com'):
                car_images = FieldArrange._replace58Tinyimg(data['car_images'])
                data['car_images'] = car_images
                
                car_images = FieldArrange._arrange58img(data['car_images'])
                data['car_images'] = car_images
                
                car_img_thumb = FieldArrange._arrange58img(data['car_img_thumb'])
                data['car_img_thumb'] = car_img_thumb
                
            if case('9che.com'):
                car_condition = FieldArrange._drop9chesharp(data['car_condition'])
                data['car_condition'] = car_condition
                
                car_description = FieldArrange._drop9chesharp(data['car_description'])
                data['car_description'] = car_description
            if case():
                pass 
            
        #车辆外观规整化
        car_appearance = FieldArrange.arg_car_appearance(data['car_appearance'])
        data['car_appearance'] = car_appearance
        
        #车辆类型规整化
        car_style = FieldArrange.arg_car_style(data['car_style'])
        data['car_style'] = car_style
        
        #车辆行驶证规整化  
        car_driv_license = FieldArrange._car_driv_license(data['car_driv_license'])
        data['car_driv_license'] = car_driv_license
        
        #发动机号形式
        car_engine = FieldArrange._car_engine(data['car_engine'])
        data['car_engine'] = car_engine
        
        #车辆驱动形式
        car_drive_type = FieldArrange._car_drive_type(data['car_drive_type'])
        data['car_drive_type'] = car_drive_type
        
        #燃油类型规整化
        car_fuel_type = FieldArrange._car_fuel_type(data['car_fuel_type']) 
        data['car_fuel_type'] = car_fuel_type
        
        #燃油供给方式规整化   
        car_fule_mode = FieldArrange._car_fule_mode(data['car_fule_mode'])
        data['car_fule_mode'] =  car_fule_mode
        
        #是否带车牌规整化
        car_license = FieldArrange._car_license(data['car_license'])
        data['car_license'] = car_license
        
        #传动方式规整化
        car_steering = FieldArrange._car_license(data['car_steering'])
        data['car_steering'] = car_steering
         
        return  data
    
if __name__ == '__main__':
    ps=processer()
    ps.work()
    
