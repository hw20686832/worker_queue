#encoding:utf-8
'''
Created on 2012-4-23

@author: James
'''
import re
import urllib2,urllib
import json
import os,sys
import sqlite3
import types

import Chinese

segment_service_addr='192.168.2.232'
segment_service_port=8088
segment_service_portal='ictclas4j/segment'
segment_service_request_url='http://%s:%s/%s'%(segment_service_addr,segment_service_port,segment_service_portal)
segment_service_request_headers = {}
segment_service_request_headers['Content-Type'] = 'application/x-www-form-urlencoded'#application/json
segment_service_request_headers['Accept']= 'text/plain'
import itertools
def log(message):
    pass
    #print '[debug] %s'%message

def _58_fetch_purchase_price_from_car_price(src):
    '''
    从car_price提取价格信息补充到purchase
    '''
    tar = ''
    regex    = u'^.*\u65B0\u8F66\u4EF7\u683C\uFF1A([\d\uFF10-\uFF19\u002E\u002C\u3002\uFF0C\uFF1B\u00B7\u005C\u3001\u2022\u002F\u0027\u002A\u002D]+).*$'
    if src is not None and src!='':
        try:
            matchObj = re.compile(regex)
            m = matchObj.match(src)
        except TypeError,e:
            return tar
        
        if m is not None:
            tar = m.group(1)
            tar = ''.join(unichr(0x0020 if c == 0x3000 else c-0xfee0 if 0xff00 < c < 0xff80 else c) for c in map(ord, tar))#全角转半角
            tar = re.sub(u'^(\d+)([^\d]+)(\d+)$',r'\1.\3',tar)#替换数字中间的标点符号为标准点号
            tar = re.sub(u'(.*\d+)([\u002E\u002C\u3002\uFF0C\uFF1B\u00B7\u005C\u3001\u2022\u002F\u0027\u002D]+)$', r'\1', tar)#去掉末尾的点号
            tar = re.sub(r'^\.([\d\uFF10-\uFF19\u002E\u002C\u3002\uFF0C\uFF1B\u00B7\u005C\u3001\u2022\u002F\u0027\u002A\u002D]+)$',r'0.\1',tar)#第一位为点号的在之前补零
            tar = re.sub(r'^\.(\d+.*)$',r'\1',tar)#如果第一位仍为点号则去掉
            try:
                result = float(tar)
            except ValueError,e:
                result = 0
            
            if result > 1000:
                result = result / 10000
                    
            if result<=0.1:
                tar = ''   
            else:
                tar = result     
    return tar

def _car_price(src):
    '''
    car_price规整化
    '''
    tar = 0
    if type(src) is types.IntType or type(src) is types.FloatType:
        return float(src)
    
    regex    = u'^[^\d\uFF10-\uFF19\u002E\u002C\u3002\uFF0C\uFF1B\u00B7\u005C\u3001\u2022\u002F\u0027\u002A\u002D]*([\d\uFF10-\uFF19\u002E\u002C\u3002\uFF0C\uFF1B\u00B7\u005C\u3001\u2022\u002F\u0027\u002A\u002D]+).*$'
    if src is not None and src!='':
        
        flag=False
        if src.endswith("000") or src.count(",")>0:
            flag=True
        src=src.replace(",","")
        matchObj = re.compile(regex)
        try:
            m = matchObj.match(src)
        except TypeError,e:
            return tar
        if m is not None:
            tar = m.group(1)
            tar = ''.join(unichr(0x0020 if c == 0x3000 else c-0xfee0 if 0xff00 < c < 0xff80 else c) for c in map(ord, tar))#全角转半角
            tar = re.sub(u'^(\d+)([^\d]+)(\d+)$',r'\1.\3',tar)#替换数字中间的标点符号为标准点号
            tar = re.sub(u'(.*\d+)([\u002E\u002C\u3002\uFF0C\uFF1B\u00B7\u005C\u3001\u2022\u002F\u0027\u002D]+)$', r'\1', tar)#去掉末尾的点号
            tar = re.sub(r'^\.([\d\uFF10-\uFF19\u002E\u002C\u3002\uFF0C\uFF1B\u00B7\u005C\u3001\u2022\u002F\u0027\u002A\u002D]+)$',r'0.\1',tar)#第一位为点号的在之前补零
            tar = re.sub(r'^\.(\d+.*)$',r'\1',tar)#如果第一位仍为点号则去掉
            try:
                result = float(tar)
            except ValueError,e:
                result = 0
                
            if flag:
                result = result / float(10000)
            else:
                if result > 10000:
                    result = result / float(10000)
                    
            if result<=0.01:
                tar = 0   
            else:
                tar = result
    return round(float(tar),2)

def __common_str(src):
    '''
    过滤中文（标点）、数字、英文（标点）以外的字符
    '''
    reobj = re.compile(u'[^\u4e00-\u9fa5a-zA-Z0-9\pP\u3000-\u303F\uFF08\uFF09\uFF1F\uFF0C\u2014\uFF5E\uFF01]',re.IGNORECASE)
    result,number = reobj.subn(r'', src)
    return result

def __fetch_category_from_segment(str):
    '''
    整理分词结果为 类别：[词语]格式的key-value字典
    '''
    try:
        data = json.loads(str,encoding='utf-8')
    except:
        data = json.loads(str)
    #data = json.loads(str)
    mydict = {}
    otherstr=""
    for x in data:
        for y in x[1]:
            key = y
            if not mydict.has_key(key):
                mydict[key]=[]
            mydict[key].append(x[0])
            if key!="cb" and key!="cf":
                otherstr+=x[0]
    mydict["otherstr"]=otherstr
    return mydict

def guess_car(stri, CarDict, car_brand=None, car_series=None, car_manufacturer=None):
    '''
    根据分词结果猜解汽车制造商、品牌、系列
    '''
    category_arr = __fetch_category_from_segment(stri)
     
    cc = __guess_car_f_d(category_arr,CarDict,car_brand,car_series,car_manufacturer)
    
    return cc

def __guess_car_f_d(mydict,CarDict,car_brand=None,car_series=None,car_manufacturer=None):
    '''
    根据分词结果猜解汽车制造商、品牌、系列。功能实现函数
    查询依据是sqlite中的car_spec表中各项组合的统计
    '''
    brand=""
    if mydict.has_key('cb'):
        number=len(mydict['cb'])
        brand  =   mydict['cb'][0] 
        if brand==u"北京" and number>1:
            brand=mydict['cb'][number-1] 
         
    series          =   mydict['cf'][0] if mydict.has_key('cf') else ''
    
    if brand==u"汽":
        try:
            brand=mydict['cb'][1] if mydict.has_key('cb') else ''
        except:
            brand=""
            
    if series == u"汽":
        try:
            series = mydict['cf'][1] if mydict.has_key('cf') else ''
        except:
            series = ""
            
    if brand == '':
        brand = car_brand if car_brand is not None else ''
        
    if series == '':
        series = car_series if car_series is not None else ''
    
    #分词结果有系列没有品牌的情况下，通过系列反推品牌
    if brand=='' and mydict.has_key('cf') and len(mydict['cf'])>0:
        _tmp_series = mydict['cf'][0]
        if _tmp_series!='' and CarDict.has_series(_tmp_series):
            brand = CarDict.get_brand_by_series(_tmp_series)
     
    if  (not mydict.has_key('cf')) or len(mydict['cf'])==0:
        otherstr=mydict["otherstr"]
#        print otherstr
        mydict['cf']=[]
        for s in itertools.combinations(otherstr,3):
            mydict['cf'].append("".join(s))
            
        for s in itertools.combinations(otherstr,2):
            mydict['cf'].append("".join(s))
    #分词结果有很多系列的情况下选择比较恰当的一个
    if mydict.has_key('cf') and len(mydict['cf'])>1 and car_series is None:
        if brand!='' and CarDict.has_brand(brand):
            for val in mydict['cf'] :
                if val in CarDict.get_series_by_brand(brand) and val != brand:
                    series = val
                    break

    '''
    返回字典，值有可能为空
    '''
    final_result = {
            'brand':brand if brand is not None else '',
            'series':series if series is not None else ''
           }
#    print final_result
    return final_result
    


def segmentRequest(src):
    '''
    remote request for segment
    '''
    words = __common_str(src)
    if words is None or words=='' or words.strip() == '':
        return ''
    try:
        if isinstance(words, unicode):
            words=words.encode("gbk")
        else:
            words=words.decode('utf-8').encode("gbk")
    except UnicodeEncodeError,e:
        pass
    
    segment_service_request_data={
              'w':words,
              'f':'json',
              'r':'true'
              }

    segment_service_request_para=urllib.urlencode(segment_service_request_data)
    segment_service_request=urllib2.Request(segment_service_request_url,segment_service_request_para,segment_service_request_headers)
    
    f=urllib2.urlopen(segment_service_request) 
    response=f.read()
    f.close()
#    log("segment result: "+response.decode('gbk','ignore'))
    try:
#        log("segment result: "+response.decode('gbk','ignore'))
        content=response.decode('gbk','ignore')
    except:
        try:
            content=response.encode('gbk','ignore')
        except:
            content=None
    return content

    
def _car_brand(doc, cardict):
    '''
    车辆品牌规整化
    '''
    src = doc['car_brand']
    title = doc['car_title']
    brand = doc['car_brand']
    tar = u"其它"
    gc={"series":"","brand":""}
    if src:
        if len(src)>20:
            src=src[:20]
        src = ''.join(src.split())
        src = cardict.washWord(src)

        if cardict.has_brand(src):
            gc['brand'] = src
            return gc

        values = cardict.findBrandByPinyin(Chinese.pinyin(src))
        if values:
            gc['brand'] = values[0]
            return gc
        
        fenci = segmentRequest(src)
        gc = guess_car(fenci,cardict)
        if gc is not None and gc["brand"]!="":  
            if not cardict.has_brand(gc["brand"]):
                gc['brand']=""
        return gc       
             
    return gc

def _car_series(doc,CarDict,):
    '''
    车辆系列规整化
    '''
    src = doc['car_series']
    title = doc['car_title']
    brand = doc['car_brand']
    tar = u"其它"
    gc={"series":"","brand":""}
    if src is not None and src!='':
        src = ''.join(src.split())
        if len(src)>20:
            src=src[:20]
        src = CarDict.washWord(src)
        if CarDict.has_series(src):
            gc["series"]= src
            gc["brand"]=CarDict.get_brand_by_series(src)
            return gc
        
        srcre=src.replace(doc['car_brand'],"").strip()
        if CarDict.has_series(srcre):
            gc["series"] = srcre
            gc["brand"]=CarDict.get_brand_by_series(srcre)
            return gc

#        if CarDict.getCarSpecification()['series_synonyms'].has_key(src):
#            gc['series'] = CarDict.getCarSpecification()['series_synonyms'][src]
#            gc["brand"]=CarDict.getCarSpecification()['series'][gc['series']]["brand"]
#            return gc
        
        values=CarDict.findSeriesByPinyin(Chinese.pinyin(src))
        if values and len(values)>0:
            gc["series"] = values[0]
            gc["brand"]=CarDict.get_brand_by_series(values[0])
            return gc
        
        fenci=segmentRequest(src)
        gc = guess_car(fenci,CarDict,doc['car_brand'])
        if gc is not None and gc["brand"]!="":  
            if not CarDict.has_brand(gc["brand"]):
                gc['brand']=""
    return gc
        
def _car_ttitle_bs(title,CarDict):
    gc={"series":"","brand":""}
    if title is not None and title!='':
        title=title.replace("200","")
        if len(title)>20:
            title=title[:20]
        fenci=segmentRequest(title)
        gc = guess_car(fenci,CarDict)
        if gc is not None and gc["brand"]!="":  
            if not CarDict.getCarSpecification()['brand'].has_key(gc["brand"]):
                gc['brand']=""
        return gc
    return gc

def getBrandBySeries(src,CarDict):
    if CarDict.getCarSpecification()['series'].has_key(src):
        return  CarDict.getCarSpecification()['series'][src]['brand']
    else:
        return u"其它"
    
def getSeriesBySeries(src,CarDict,old_series):
    if CarDict.getCarSpecification()['brand'].has_key(src):
        series=CarDict.getCarSpecification()['brand'][src]['series']
        old_series=old_series.replace(" ","").lower()
        for serie in series:
        #    print title,serie.lower()
            if (old_series).count(serie.replace(" ","").lower())>0:
                return serie
        for serie in CarDict.getCarSpecification()["series_synonyms"].keys():
            if (old_series).count(serie.replace(" ","").lower())>0:
                return CarDict.getCarSpecification()["series_synonyms"][serie]
    return ""

def getSeriesByTitle(src,CarDict,title):
    if CarDict.getCarSpecification()['brand'].has_key(src):
        series=CarDict.getCarSpecification()['brand'][src]['series']
        title=title.replace(" ","").lower()
        for serie in series:
        #    print title,serie.lower()
            if (title).count(serie.replace(" ","").lower())>0:
                return serie
        for serie in CarDict.getCarSpecification()["series_synonyms"].keys():
            if (title).count(serie.replace(" ","").lower())>0:
                return CarDict.getCarSpecification()["series_synonyms"][serie]
                
    return ""
