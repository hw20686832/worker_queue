#coding:utf-8
import re
import urllib2,urllib
import json
import os
import sqlite3
import re,pymongo,time,itertools
import sys

from lib.seg import splitting

def _car_type(src):
    '''
    car_type规整化
    '''
    tar = ''
    regex    = u'^(\d*.?\d*|[\uff10-\uff19]*[\u2e00\u3002]?[\uff10-\uff19]*)$'
    if src is not None and src!='':
        src=src.strip()
        matchObj = re.compile(regex)
        match = matchObj.search(src)
        if not match:  
            tar=src 
    return tar

def __common_str(src):
    '''
    过滤中文（标点）、数字、英文（标点）以外的字符
    '''
    reobj = re.compile(u'[^\u4e00-\u9fa5a-zA-Z0-9\pP\u3000-\u303F\uFF08\uFF09\uFF1F\uFF0C\u2014\uFF5E\uFF01]',re.IGNORECASE)
    result,number = reobj.subn(r'', src)
    return result

cities=[u"重庆",u"天津",u"北京",u"上海"]
ends=[u"市",u"县",u"地区",u"区",u"新区"]

def deleteCity(src):
    if src.endswith(u"市") and len(src)>2:
        src=src[:len(src)-1]
    return src

class CarSpecification():
    
    def __init__(self):
        self.mydict={
                 'countys':{},
                 'provinces':[],
                 'citys':{}
                 }
        base_url="http://admin.365auto.com:8080/provider/dict/district"
        response_stream = urllib2.urlopen(base_url)
        result = response_stream.read()
        jsons = json.loads(result)
        countys={}
        provinces= []
        citys= {}
        for key in jsons["county"]:
            countys[key]=jsons["county"][key]["superior"]
        
        for key in jsons["province"]:
            provinces.append(key)
        
        for key in jsons["city"]:
            citys[key]=jsons["city"][key]["superior"]
            self.mydict["countys"]=countys
            self.mydict["provinces"]=provinces
            self.mydict["citys"]=citys
            
    def get_countys(self):
        return self.mydict["countys"]
    
    def get_provinces(self):
        return self.mydict["provinces"]
        
    def get_citys(self):
        return self.mydict["citys"]
        

#    print key
def getProvinceCity(data,mydict):
#    print mydict
    citys=mydict.get_citys()
    countys=mydict.get_countys()
    if data in cities:
        return data,"",""
    
    if citys.has_key(data):
        return citys[data],data,""
        
    if countys.has_key(data):
        return citys[countys[data]],countys[data],data

    return "","",""

def _source_province(src,mydict):   
    '''
         信息发布所在地-省。根据省级字典规整化数据。如果含有市（区）信息，将其补充到source_zone。
    '''
#    src=u"九龙坡"
    if src is not None and src!='':
        src = ''.join(src.split())
        words = __common_str(src)
        if words is None or words=='' or words.strip() == '':
            words=None
        else:
            try:
                if isinstance(words, unicode):
                    words=words.encode("gbk")
                else:
                    words=words.decode('utf-8').encode("gbk")
            except UnicodeEncodeError,e:
                pass
            datas=splitting(words)
            datas_list=[src]
            singals=[]
            for x in datas:
                if len(x[0])==1:
                    singals.append(x[0])
                else:
                    datas_list.append(x[0])
                    
            for s in itertools.combinations(singals,2):
#                print "".join(s)
                datas_list.append("".join(s))
            
            cityvalidate=False
            for x in datas_list:
                data=getProvinceCity(x,mydict)
                if data[0]=="":
                    for end in ends:
                        if len(x)>2 and x.endswith(end):#结尾删词
                            data=getProvinceCity(x.replace(end,""),mydict)
                            if data[0]!="":
                                cityvalidate=True
                                break 
                        else:#结尾补词
                            data=getProvinceCity(x+end,mydict)
                            if data[0]!="":
                                cityvalidate=True
                                break
                else:
                    cityvalidate=True
                if cityvalidate==True:
#                    print src,"==>",x,"==>",data[0],"==>",data[1]
                    return data
    return "","",""

#mydict=CarSpecification()
#pc1= _source_province(u"中山",mydict)
#print pc1[0],pc1[1]
#pc2= _source_province(u"东区",mydict)
#print pc2[0],pc2[1]
#pc=pc2
#if pc1[0]!="" and pc1[1]!="":
#    pc=pc1
#if pc1[1]=="" and pc2[0]!="":
#    pc=pc2
#if pc2[0]==u"中山":
#    pc=pc2
#print pc[0],pc[1]

def _car_origin(src):
    '''
          车辆产地。格式为厂商+出厂地。根据厂商字典和地区地点将其规整化。 
    '''  
    return src

def _car_license_at(src):
    '''
          车牌所在地：将其规整化为省（直辖市）-市（区）-县
    '''
    return src
    
