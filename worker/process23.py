#encoding:utf-8
"""
省份地区规整化
"""
import sys,os
JIEBA_LOCATION = os.path.realpath(os.path.join(os.path.dirname(__file__),"lib","segment"))
sys.path.append(JIEBA_LOCATION)
from base import ProcesserBase
from lib import Process23Main
from lib.Process23Main import CarSpecification

class processer(ProcesserBase):
    """主要字段的规整化、涉及到分词提取"""
    seq = "p23"
    
    def __init__(self):
        ProcesserBase.__init__(self) 
        self.mydict =  CarSpecification()       
    
    def process(self,data):
        _o_car_origin = data['car_origin']
        data['car_origin'] = Process23Main._car_origin(data['car_origin'])
        
        _o_car_license_at = data['car_license_at']
        pc= Process23Main._source_province(data["car_license_at"],self.mydict)
        data['car_license_at'] =pc[0]+pc[1]+pc[2]

        pc1=Process23Main._source_province(data["source_province"],self.mydict)
        pc2=Process23Main._source_province(data["source_zone"],self.mydict)
        pc=pc2
        if pc1[0]!="" and pc1[1]!="":
            pc=pc1
        if pc1[1]=="" and pc2[0]!="":
            pc=pc2
        if pc2[0]==data["source_province"]:
            pc=pc2
        data["source_province"]=pc[0]
        data["source_zone"]=pc[1]
        
        return  data
    
if __name__ == '__main__':
    ps=processer()
    ps.work()
