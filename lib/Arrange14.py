#encoding:utf-8
'''
Created on 2012-4-23

@author: James
'''
import re
import urllib2,urllib
import json
import os
import sqlite3
import common
import datetime,time

def _car_title(src):
    '''
    car_title规整化,将信息标题前后的感叹号“（出售）...”过滤
    '''
    if src is not None and src!='':
        regex = u'(\(\u51FA\u552E\))'
        src=re.sub(u"\(\u51FA\u552E\)","",src)
        src=re.sub(u"\.\.","",src)
        src=re.sub(u"\,\,","",src)
        src=re.sub(u"\u3010\u51FA\u552E\u3011","",src)
        src=re.sub(u"\uFF01","",src)
        
        return src
    
def _source_birth(src):
    '''
    _source_birth是月日年时分秒的混合，信息发布日期，将其规整化为YYYY-MM-DD hh:mm:ss，如果值为url。需要http请求后获得日期。
    '''
#    current=time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())
#    print current
    current=datetime.datetime.now() - datetime.timedelta(days=1)
    current=current.strftime('%Y-%m-%d %H:%M:%S')
#    print current
    if src is None or src=='':
        return current
    
    src=re.sub(u"\u5E74|\u6708|\/","-",src)
    src=re.sub(u"\u65E5","",src)
#    print src
    YY = int(time.strftime('%Y'))
    MM = int(time.strftime('%m'))
    DD = int(time.strftime('%d'))
    HH=00
    MI=00
    SS=00
    YYYYMMDDHHMMSS    = u'^(\d+)-(\d+)-(\d+)\u0020(\d+)\:(\d+)\:(\d+)$' #YYYY-MM-DD
    YYYYMMDDHHMMSS2    = u'^(\d+)-(\d{2})-(\d{2}).*(\d{2})\:(\d+)$' #酷车网："2012-09-20 10:32"
    YYYYMMDD_v2 = u'^(\d+)-(\d+)\-$'#YYYY年MM月
    YYYYMMDD_v3 = u'^(\d+)-(\d+)-(\d+)[^0-9\-]+'#YYYY-MM-DD含中文字符
    YYYYMMDD      = r'(\d+)-(\d+)-(\d+)$'#YYYY-MM-DD
    YYYYMMDD_58= r'^(\d+)\.(\d+)\.(\d+)$'#YYYY.MM.DD
    MMDDHHMMSS      = u'^(\d+)-(\d+)\u0020(\d+)\:(\d+)$'#MM-DD HH:MM\
    MMDDHHMMSS_v2      = u'^(\d+)-(\d+)\u0020(\d+)\:(\d{2}).*'#MM-DD HH:MM
    YYYYMM_v4=u'^(\d+)-(\d{2})(\d{1,2})\:(\d+)$'#03-1823:47
    MMYYYY      = u'^(\d+)-(\d{2})(\d{1,2})\:(\d{2}).*'#03-2203:0403-2216:06
    YYYYMMDD_v4=r'^(\d+)-(\d+)-(\d{2})'#YYYY-MM-DD
    
    matchObj = re.compile(YYYYMMDDHHMMSS)
    m = matchObj.match(src)
    if m is not None:
        YY = int(m.group(1))
        MM = int(m.group(2))
        DD = int(m.group(3))
        HH = int(m.group(4))
        MI = int(m.group(5))
        SS = int(m.group(6))
    else:
        matchObj = re.compile(YYYYMMDDHHMMSS2)
        m = matchObj.match(src)
#        print m.group()
        if m is not None:
            YY = int(m.group(1))
            MM = int(m.group(2))
            DD = int(m.group(3))
            HH = int(m.group(4))
            MI = int(m.group(5))
            SS = 0
        else:
            matchObj = re.compile(YYYYMMDD_v2)
            m = matchObj.match(src)
            if m is not None:
                YY = int(m.group(1))
                MM = int(m.group(2))
                #print '%s match %s'%(src,YYYYMMDD_v2)
            else:
                matchObj = re.compile(YYYYMMDD_v3)
                m = matchObj.match(src)
                if m is not None:
                    YY = int(m.group(1))
                    MM = int(m.group(2))
                    DD = int(m.group(3))
                   # print '%s match %s'%(src,YYYYMMDD_v3)
                else:
                    matchObj = re.compile(YYYYMMDD)
                    m = matchObj.match(src)
                    if m is not None:
                        YY = int(m.group(1))
                        MM = int(m.group(2))
                        DD = int(m.group(3))
                    else:
                        matchObj = re.compile(YYYYMMDD_58)
                        m = matchObj.match(src)
                        if m is not None:
                            YY = int(m.group(1))
                            MM = int(m.group(2))
                            DD = int(m.group(3))
                            #print '%s match %s'%(src,YYYYMM)
                        else:
                            matchObj = re.compile(MMDDHHMMSS)
                            m = matchObj.match(src)
                            if m is not None:
                                MM = int(m.group(1))
                                DD = int(m.group(2))
                                HH = int(m.group(3))
                                MI = int(m.group(4))
                                #print '%s match %s'%(src,YYYYMM_v2)
                                #print YY,'-',MM
                            else:
                                matchObj = re.compile(MMDDHHMMSS_v2)
                                m = matchObj.match(src)
                                if m is not None:
                                    MM = int(m.group(1))
                                    DD = int(m.group(2))
                                    HH = int(m.group(3))
                                    MI = int(m.group(4))
                                    #print '%s match %s'%(src,YYYYMM_v3)
                                else:
                                    matchObj = re.compile(YYYYMM_v4)
                                    m = matchObj.match(src)
                                    if m is not None:
                                        MM = int(m.group(1))
                                        DD = int(m.group(2))
                                        HH = int(m.group(3))
                                        MI = int(m.group(4))
                                        #print '%s match %s'%(src,YYYYMM_v4)
                                    else:
                                        matchObj = re.compile(MMYYYY)
                                        m = matchObj.match(src)
                                        if m is not None:
                                            MM = int(m.group(1))
                                            DD = int(m.group(2))
                                            HH = int(m.group(3))
                                            MI = int(m.group(4))
                                            #print '%s match %s'%(src,MMYYYY)
                                        else:
                                            matchObj = re.compile(YYYYMMDD_v4)
                                            m = matchObj.match(src)
                                            if m is not None:
                                                YY = int(m.group(1))
                                                MM = int(m.group(2))
                                                DD = int(m.group(3))
                                                #print '%s match %s'%(src,YYYY)
    mm=int(time.strftime('%m'))
    dd=int(time.strftime('%d'))
    if MM>mm:
        YY=YY-1
    if MM==mm and DD>dd:
        YY=YY-1
    _src = '%d-%d-%d %s:%s:%s'%(YY,MM,DD,HH,MI,SS)   
    if src is None or src=='':
        return current 
    return _src
   
#_source_birth("")

def _contact_mobile_phone(src,type,spider): 
    phone=""
    mobile=""
#    print src
#    src=u"024-88886588"
#    print common.unicoding("-") 
    if src is None or src=='':
        return "",""
    if spider=="iautos":
        old_src=src[:8]
#        print old_src
#        print src
        if src.count(old_src)>1:
            src=src[:len(src)/2]
#        print src
    if (not src.startswith("http")) and (src.find("/plugs/pic/")>=0 or src.find("/plugs/phone/")>=0):
        src="http://www.sc2car.com%s"%src
        
    if (not src.startswith("http")) and src.find("/tel")>=0:
        src="http://www.ganji.com%s"%src
        
    if src.count("/tel/")>1:
        number= src.rfind("/tel/") 
        src=src[:number]
        
    if (not src.startswith("http")) and src.find("systems/codeimage")>=0:
        src="http://www.2duche.com%s"%src
        
    if (not src.startswith("http")) and src.find("upload/htmlImage")>=0:
        src="http://www.ln2car.com%s"%src
    
    if src.count("/")>=2:
        if type==1:
            return src,""
        else:
            return "",src

    src=common.strQ2B(src)
    reobj = re.compile(u'[^0-9\u002D]',re.IGNORECASE)
    result = reobj.sub(r' ', src)
#    print result
    phone=""
    mobile=""
    if result.count(" ")>0:
        results= result.split(" ")
        for result1 in results:
            if len(result1)==11:
                mobile=result1
            elif len(result1)>8:
                phone=result1
        if phone!="" or mobile!="":
            return phone,mobile          
                
    
    if result.startswith(u"400"):
        phone=result[:12]
    else:
        result=re.sub(u"\u0020", "",result)
        phone_v = u'(\d{8}\u002D\d+)$' #0757-83966080
        matchObj = re.compile(phone_v)
        m = matchObj.match(result)
        if m is not None:
            phone = m.group(1)
        else:
            phone_v = u'.*(\d{4}\u002D\d+)$' #0757-83966080
            matchObj = re.compile(phone_v)
            m = matchObj.match(result)
            if m is not None:
                phone = m.group(1)
                
            else:
                phone_v = u'.*(\d{3}\u002D\d+)$' #0757-83966080
                matchObj = re.compile(phone_v)
                m = matchObj.match(result)
                if m is not None:
                    phone = m.group(1)
                    
                else:
                    phone_v = u'(0\d+)' #0757-83966080
                    matchObj = re.compile(phone_v)
                    m = matchObj.match(result)
                    if m is not None:
                        phone = m.group(1)
                    else:
                        if len(result)>=6 and len(result)<=10:
                            phone=result
                
    mobile_v=u"([1][0-9]{10})"
    matchObj = re.compile(mobile_v)
    m = matchObj.match(result)
    if m is not None:
        mobile=m.group(1)
        
    if mobile!="":
        phone=mobile
    return phone,mobile

#print _contact_mobile_phone("/tel_img/?c=ktyIal-x0Y.CxByrFJbwiKoRunk4Q__PtQyX","phone","ganji")

def _contact_mail(src):  
    if src is None or src=='':
        return ''
    src=common.strQ2B(src)
    mail_v=u"(.*)\u79FB\u52A8"
    matchObj = re.compile(mail_v)
    m = matchObj.match(src)
    if m is not None:
        src = m.group(1)
#        print src   
    reobj = re.compile(u'[\u3002]',re.IGNORECASE)
    
    result = reobj.sub(r'.', src)#替换。为.
    reobj = re.compile(u'[^\_\-\u002E\u0040a-zA-Z\d]',re.IGNORECASE)
    result = reobj.sub(r'', result)#替换非.整形@字符类数据
    result=result.replace("www.","")
#    print result
    mail_v=u"(.*)\u0040(\w+)\u002E(.*)"
    matchObj = re.compile(mail_v)
    m = matchObj.match(result)
    if m is not None:
        name = m.group(1)
        com = m.group(3)
        yu = m.group(2)
        reobj = re.compile(u'[^\w\d\_\-]',re.IGNORECASE)
        name = reobj.sub(r'', name)#替换非.整形@字符类数据
        reobj = re.compile(u'[^\w\d\u002E]',re.IGNORECASE)
        com = reobj.sub(r'', com)#替换非.整形.字符类数据
        result=name+"@"+yu+"."+com
        return result
    else:
        return ""
    
def _contact_qq(src):  
    if src is None or src==''or src.find("1234")==0:
        return ''
    src=common.strQ2B(src)
    if src.find("58.com")>0:
        return src
    
    if (not src.startswith("http")) and src.find("/plugs/pic/")>=0:
        src="http://www.sc2car.com%s"%src
        
    if (not src.startswith("http")) and src.find("/tel/")>=0:
        src="http://www.ganji.com%s"%src
        
    if (not src.startswith("http")) and src.find("upload/htmlImage")>=0:
        src="http://www.ln2car.com%s"%src
        
    reobj = re.compile(u'[^0-9]',re.IGNORECASE)
    result = reobj.sub(r'', src)
    qq_v = u'([1-9]{1}\d{4,11})$' #0757-83966080
    matchObj = re.compile(qq_v)
    m = matchObj.match(result)
    if m is not None:
        result = m.group(1)
        return result
    else:
        return ""
    
def _contact_addr(src):  
    """
    联系地址
    过滤中文（标点）、数字、英文（标点）以外的字符
    """
    if src is None or src=='':
        return ''
    reobj = re.compile(u'[^\u4e00-\u9fa5a-zA-Z0-9\pP\u3000-\u303F\uFF08\uFF09\uFF1F\uFF0C\u2014\uFF5E\uFF01]',re.IGNORECASE)
    result = reobj.sub(r'', src)
    addr_v = u'\d{11}([\u4e00-\u9fa5a-zA-Z0-9\pP\u3000-\u303F\uFF08\uFF09\uFF1F\uFF0C\u2014\uFF5E\uFF01]+)' #15868823208杭州市江干区艮山东路138号
    addr_v2 = u'\w+([\u4e00-\u9fa5a-zA-Z0-9\pP\u3000-\u303F\uFF08\uFF09\uFF1F\uFF0C\u2014\uFF5E\uFF01]+)' #http://www.nb2sc.com 宁波市江东区中兴北路6号
    matchObj = re.compile(addr_v)
    m = matchObj.match(result)
    if m is not None:
        result = m.group(1)
        #print '%s match %s'%(src,YYYYMMDD)
    else:
        matchObj = re.compile(addr_v2)
        m = matchObj.match(result)
        if m is not None:
            result = m.group(1)
    return result
    
def _contact(src,spider):  
    """
            联系人处理，除去非中文字符
    """
    if src is None or src=='':
        return ''
    src=common.strQ2B(src)
    contact_v = re.compile(u'([\u4e00-\u9fa5a]+)',re.IGNORECASE)
    matchObj = re.compile(contact_v)
    m = matchObj.match(src)
    result=""
    if m is not None:
        result = m.group(1)
    if spider=="iautos":
       old_result=result[:2]
#       print old_result
       if result.count(old_result)>1:
           result=result[:len(result)/2]
        
    return result
    
#print _contact(u"李先生李先生",u"iautos")

def _car_usage(src):  
    """
            车辆用途。将“车身颜色。。。”过滤掉。
    """
    if src is None or src=='':
        return ''
    result=src.replace(u"\u8F66\u8EAB\u989C\u8272\uFF1A","")
    return result

def _car_transmission(src):  
    """
        变速器。通俗上分为手动变速器(MT)，自动变速器(AT)， 手动/自动变速器，无级式变速器。格式上可以是×档+变速器类型
    """
    result_qita=u"不详"
    if src is None or src=='':
        return result_qita
    result=""
    result_at=u"\u81EA\u52A8"
    result_mt=u"\u624B\u52A8"
    result_am=u"\u624B\u81EA\u4E00\u4F53"
    ams=[u"手排档"]#手自一体
    mts=[u"手排",u"手动档",u"MT",u"m"]#手动
    ats=[u"自动档",u"序列",u"双离合",u"半自动",u"无级变速",u"AT",u"at"]#自动
    for am in  ams:
        if src.find(am)>=0:
            return result_am
    for mt in  mts:
        if src.find(mt)>=0:
            return result_mt
    for at in  ats:
        if src.find(at)>=0:
            return result_at
            
    transmission_v = re.compile(u'.*(\u65E0\u6781|\u65E0\u7EA7).*',re.IGNORECASE)
    matchObj = re.compile(transmission_v)
    m = matchObj.match(src)
    if m is not None:
        result = result_at
    else:
        if src.find(u"手")>=0 and src.find(u"自")>=0:
            result = result_am
        else:
            transmission_v = re.compile(u'.*(\u4E00\u4F53).*',re.IGNORECASE)
            matchObj = re.compile(transmission_v)
            m = matchObj.match(src)
            if m is not None:
                result = result_am
            else:
                transmission_v = re.compile(u'.*(\u81EA).*',re.IGNORECASE)
                matchObj = re.compile(transmission_v)
                m = matchObj.match(src)
                if m is not None:
                    result = result_at
                else:
                    transmission_v = re.compile(u'.*(\u624B).*',re.IGNORECASE)
                    matchObj = re.compile(transmission_v)
                    m = matchObj.match(src)
                    if m is not None:
                        result = result_mt
                    else:
                        result=result_qita
    return result

#print _contact_mobile_phone(u"/plugs/phone/number/eNozNzU1LghxMUz1Mq3KN_erTHQ0dNQv8E1zD8q18DZ0czbLrSop9i8uzKrMM0r1cXcJN_L2LU0HAMu6EXU=",1)
