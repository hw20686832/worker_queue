#encoding:utf-8
"""
文本字段的规整化,比如标题、变速器、车辆用途、联系方式、联系人，手机、邮件、QQ、地址、发布日期
"""
from base import ProcesserBase
from lib.common import switch
from lib import Arrange14

class processer(ProcesserBase):
    seq = "p14"
    
    def __init__(self):
        ProcesserBase.__init__(self)        
    
    def process(self,data):
        
        car_title = Arrange14._car_title(data['car_title'])
        data['car_title'] = car_title
        
      
        source_birth = Arrange14._source_birth(data)
        data['source_birth'] = source_birth
        
        
        phone,mobile = Arrange14._contact_mobile_phone(data['contact_phone'],1,data['spider'])
        
        
        contact_phone = Arrange14._contact_mobile_phone(data['contact_mobile'],2,data['spider'])
        data['contact_phone'],data['contact_mobile'] = contact_phone
        
        if data['contact_phone']=="" or data['contact_phone'] is None:
            data['contact_phone']=phone
            
        if data['contact_mobile']=="" or data['contact_mobile'] is None:
            data['contact_mobile']=mobile
        
        contact_mail = Arrange14._contact_mail(data['contact_mail'])
        data['contact_mail'] = contact_mail
        
        contact_qq = Arrange14._contact_qq(data['contact_qq'])
        data['contact_qq'] = contact_qq
        
        contact_addr = Arrange14._contact_addr(data['contact_addr'])
        data['contact_addr'] = contact_addr
        
        contact = Arrange14._contact(data['contact'],data['spider'])
        data['contact'] = contact
        
        car_usage = Arrange14._car_usage(data['car_usage'])
        data['car_usage'] = car_usage
        
        if data["spider"]=="58" or data["spider"]=="iautos" :
            car_transmission = Arrange14._car_transmission(data['car_keywords'])
        else:
            car_transmission = Arrange14._car_transmission(data['car_transmission'])

        data['car_transmission'] = car_transmission  
        return data
    
if __name__ == '__main__':
    ps=processer()
    ps.work()
    
