#coding:utf-8
import re
import time
import common

def _replace58Tinyimg(img):
    '''
    58同城的car_images存储的是缩略图地址，将其改为大图地址
    '''
    reobj = re.compile(r'/tiny/',re.IGNORECASE)
    result,number = reobj.subn(r'/big/', img)
    return result


def _arrange58img(img):
    '''
    58同城的car_img_thumb|car_images存储的多个图片地址之间没有分隔符，加入分隔符“###” 
    '''
    reobj = re.compile(r'.jpghttp',re.IGNORECASE)
    result,number = reobj.subn(r'.jpg###http', img)
    return result

def _drop9chesharp(str):
    '''
    旧车网的car_condition和car_description段落开头有多余的“###” 
    '''
    reobj = re.compile(r'^#{3,6}',re.IGNORECASE)
    result,number = reobj.subn('', str)
    return result

def _ucar_carbirth(str):
    '''
    car_birth是月日年的混合，顺序有可能颠倒为：MMYYYYDD、MMDDYYYY、MMYYYY，将其整理成：YYYY-MM-DD；
    '''
    MMYYYYDD = r'^(1[0-2]{1}|[0-9]{1})(20[0-1]{1}[0-9]{1}|19[8-9]{1}[0-9]{1})([1-3]?[0-9]{1})$'
    MMDDYYYY = r'^(1[0-2]{1}|[0-9]{1})([1-3]?[0-9]{1})(20[0-1]{1}[0-9]{1}|19[8-9]{1}[0-9]{1})$'
    YYYYMMDD = r'^(20[0-1]{1}[0-9]{1}|19[8-9]{1}[0-9]{1})(1[0-2]{1}|[1-9]{1}|0[1-9]{1})([1-3]?[0-9]{1})$'
    YYYYDDMM = r'^(20[0-1]{1}[0-9]{1}|19[8-9]{1}[0-9]{1})([1-3]?[0-9]{1})(1[0-2]{1}|[0-9]{1})$'
    DDMMYYYY = r'^([1-3]?[0-9]{1})(1[0-2]{1}|[0-9]{1})(20[0-1]{1}[0-9]{1}|19[8-9]{1}[0-9]{1})$'
    MMYYYY   = r'^(1[0-2]{1}|[0-9]{1})(20[0-1]{1}[0-9]{1}|19[8-9]{1}[0-9]{1})$'
    YYYY     = r'^(20[0-1]{1}[0-9]{1}|19[8-9]{1}[0-9]{1})$'
    
    matchObj = re.compile(MMYYYYDD)
    m = matchObj.match(str)
    YY = 0
    MM = 1
    DD = 1
    
    _str = str
    if m is not None:
        YY = int(m.group(2))
        MM = int(m.group(1))
        DD = int(m.group(3))
    else:
        matchObj = re.compile(MMDDYYYY)
        m = matchObj.match(str)
        if m is not None:
            YY = int(m.group(3))
            MM = int(m.group(1))
            DD = int(m.group(2))
        else:
            matchObj = re.compile(YYYYMMDD)
            m = matchObj.match(str)
            if m is not None:
                YY = int(m.group(1))
                MM = int(m.group(2))
                DD = int(m.group(3))
            else:
                matchObj = re.compile(YYYYDDMM)
                m = matchObj.match(str)
                if m is not None:
                    YY = int(m.group(1))
                    MM = int(m.group(3))
                    DD = int(m.group(2))
                else:
                    matchObj = re.compile(DDMMYYYY)
                    m = matchObj.match(str)
                    if m is not None:
                        YY = int(m.group(3))
                        MM = int(m.group(1))
                        DD = int(m.group(2))  
                    else:  
                        matchObj = re.compile(MMYYYY)
                        m = matchObj.match(str)
                        if m is not None:
                            YY = int(m.group(2))
                            MM = int(m.group(1))
                        else:
                            matchObj = re.compile(YYYY)
                            m = matchObj.match(str)
                            if m is not None:
                                YY = int(m.group(1))
    if YY !=0:
        MM=1 if MM==0 else 1
        DD=1 if DD==0 else 1
        _str = '%s-%s-%s'%(YY,MM,DD)                 
    return _str


def _car_birth(str):
    '''
    整理出厂日期格式
    '''
    YY = 0
    MM = 1
    DD = 1
    
    YYYYMMDD    = r'(20[0-1]{1}[0-9]{1}|19[8-9]{1}[0-9]{1})-(1[0-2]{1}|[0-9]{1})-([1-3]?[0-9]{1})' #YYYY-MM-DD
    YYYYMMDD_v2 = u'(20[0-1]{1}[0-9]{1}|19[8-9]{1}[0-9]{1})\u5E74(1[0-2]{1}|[0-9]{1})\u6708([1-3]?[0-9]{1})'#YYYY年MM月DD
    YYYYMMDD_v3 = r'(20[0-1]{1}[0-9]{1}|19[8-9]{1}[0-9]{1})\.(1[0-2]{1}|[0-9]{1})\.([1-3]?[0-9]{1})'#YYYY.MM.DD
    
    YYYYMM      = r'(20[0-1]{1}[0-9]{1}|19[8-9]{1}[0-9]{1})-(1[0-2]{1}|[0-9]{1})'#YYYY-MM
    YYYYMM_v2   = u'(20[0-1]{1}[0-9]{1}|19[8-9]{1}[0-9]{1})\u5E74(1[0-2]{1}|[0-9]{1})'#YYYY年MM
    YYYYMM_v3   = r'(20[0-1]{1}[0-9]{1}|19[8-9]{1}[0-9]{1})\.(1[0-2]{1}|[0-9]{1})'#YYYY.MM
    YYYYMM_v4   = r'(20[0-1]{1}[0-9]{1}|19[8-9]{1}[0-9]{1})[^\d]+(1[0-2]{1}|[0-9]{1})'#YYYY()MM
    
    YYYY        = r'^(20[0-1]{1}[0-9]{1}|19[8-9]{1}[0-9]{1})$'#YYYY
    YYYY_v2     = u'^(20[0-1]{1}[0-9]{1}|19[8-9]{1}[0-9]{1})\u5E74$'#YYYY年
    
    YC          = u'^(\d+)\u5E74$'#n年
    
    matchObj = re.compile(YYYYMMDD)
    m = matchObj.match(str)
    if m is not None:
        YY = int(m.group(1))
        MM = int(m.group(2))
        DD = int(m.group(3))
    else:
        matchObj = re.compile(YYYYMMDD_v2)
        m = matchObj.match(str)
        if m is not None:
            YY = int(m.group(1))
            MM = int(m.group(2))
            DD = int(m.group(3))
        else:
            matchObj = re.compile(YYYYMMDD_v3)
            m = matchObj.match(str)
            if m is not None:
                YY = int(m.group(1))
                MM = int(m.group(2))
                DD = int(m.group(3))
            else:
                matchObj = re.compile(YYYYMM)
                m = matchObj.match(str)
                if m is not None:
                    YY = int(m.group(1))
                    MM = int(m.group(2))
                else:
                    matchObj = re.compile(YYYYMM_v2)
                    m = matchObj.match(str)
                    if m is not None:
                        YY = int(m.group(1))
                        MM = int(m.group(2))
                    else:
                        matchObj = re.compile(YYYYMM_v3)
                        m = matchObj.match(str)
                        if m is not None:
                            YY = int(m.group(1))
                            MM = int(m.group(2))
                        else:
                            matchObj = re.compile(YYYYMM_v4)
                            m = matchObj.match(str)
                            if m is not None:
                                YY = int(m.group(1))
                                MM = int(m.group(2))
                            else:
                                matchObj = re.compile(YYYY)
                                m = matchObj.match(str)
                                if m is not None:
                                    YY = int(m.group(1))
                                else:
                                    matchObj = re.compile(YYYY_v2)
                                    m = matchObj.match(str)
                                    if m is not None:
                                        YY = int(m.group(1))
                                    else:
                                        matchObj = re.compile(YC)
                                        m = matchObj.match(str)
                                        if m is not None:
                                            cr_year=time.strftime('%Y',time.localtime(time.time()))
                                            YY = int(cr_year)-int(m.group(1))
                                        else:
                                            pass
    if YY !=0:
        MM=1 if MM==0 else MM
        DD=1 if DD==0 else DD
        _str = '%s-%s-%s'%(YY,MM,DD)   
    else:
        _str=''#str              
    return _str

def _fitch_emission(src):
    '''
    提取排量信息，范围：0.1L ～  20L
    '''
    tar = ''
    regex    = u'^[^\d\uFF10-\uFF19\u002E\u002C\u3002\uFF0C\uFF1B\u00B7\u005C\u3001\u2022\u002F\u0027\u002A\u002D]*([\d\uFF10-\uFF19\u002E\u002C\u3002\uFF0C\uFF1B\u00B7\u005C\u3001\u2022\u002F\u0027\u002A\u002D]+).*$'
    if src is not None and src!='':
        matchObj = re.compile(regex)
        m = matchObj.match(src)
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
            if result>100:
                result = result / 1000
                tar = result
            if result<0.1 or result>20:
                tar = ''     
    return tar


def _fitch_car_mileage(src):
    '''
    提取里程信息，范围：100（公里）～10000 （万公里）
    '''
    tar = ''
    regex    = u'^[^\d\uFF10-\uFF19\u002E\u002C\u3002\uFF0C\uFF1B\u00B7\u005C\u3001\u2022\u002F\u0027\u002A\u002D]*([\d\uFF10-\uFF19\u002E\u002C\u3002\uFF0C\uFF1B\u00B7\u005C\u3001\u2022\u002F\u0027\u002A\u002D]+).*$'
    if src is not None and src!='':
        matchObj = re.compile(regex)
        m = matchObj.match(src)
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
            
            if result > 10000:
                result = result / 10000
                    
            if result<=0.01:
                tar = ''
            else:
                tar = round(result,2)
                if str(tar).endswith(".0"):
                    tar=int(tar)
    return tar

def _fitch_car_price(src):
    '''
    提取汽车报价，范围：1000（元）～1000 （万元）
    '''
    tar = 0
    regex    = u'^[^\d\uFF10-\uFF19\u002E\u002C\u3002\uFF0C\uFF1B\u00B7\u005C\u3001\u2022\u002F\u0027\u002A\u002D]*([\d\uFF10-\uFF19\u002E\u002C\u3002\uFF0C\uFF1B\u00B7\u005C\u3001\u2022\u002F\u0027\u002A\u002D]+).*$'
    if src is not None and src!='':
        matchObj = re.compile(regex)
        m = matchObj.match(src)
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
                tar = 0   
            else:
                tar = result     
    return tar


def _fitch_purchase_price(src):
    '''
    提取新车购置价，范围：1000（元）～1000 （万元）
    '''
    tar = 0
    regex    = u'^[^\d\uFF10-\uFF19\u002E\u002C\u3002\uFF0C\uFF1B\u00B7\u005C\u3001\u2022\u002F\u0027\u002A\u002D]*([\d\uFF10-\uFF19\u002E\u002C\u3002\uFF0C\uFF1B\u00B7\u005C\u3001\u2022\u002F\u0027\u002A\u002D]+).*$'
    if src is not None and src!='':
        matchObj = re.compile(regex)
        m = matchObj.match(src)
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
                tar = 0   
            else:
                tar = round(result,2)
                if str(tar).endswith(".0"):
                    tar=int(tar)
    return tar

def arg_purchase_date(str):
    if str is None or str=='':
        return ''
    '''
    整理原车购买日期
    '''
    YY = 0
    MM = 1
    DD = 1
    
    YYYYMMDD    = r'^(20[0-1]{1}[0-9]{1}|19[3-9]{1}[0-9]{1})-(1[0-2]{1}|[0-9]{1})-([1-3]?[0-9]{1})$' #YYYY-MM-DD
    YYYYMMDD_v2 = u'^(20[0-1]{1}[0-9]{1}|19[3-9]{1}[0-9]{1})\u5E74(1[0-2]{1}|[0-9]{1})\u6708([1-3]?[0-9]{1})$'#YYYY年MM月DD
    YYYYMMDD_v3 = r'^(20[0-1]{1}[0-9]{1}|19[3-9]{1}[0-9]{1})\.(1[0-2]{1}|[0-9]{1})\.([1-3]?[0-9]{1})$'#YYYY.MM.DD
    
    YYYYMM      = r'^(20[0-1]{1}[0-9]{1}|19[3-9]{1}[0-9]{1})-(1[0-2]{1}|[0-9]{1})$'#YYYY-MM
    YYYYMM_v2   = u'^(20[0-1]{1}[0-9]{1}|19[3-9]{1}[0-9]{1})\u5E74(1[0-2]{1}|0[1-9]{1})\u6708$'#YYYY年MM月
    YYYYMM_v3   = r'^(20[0-1]{1}[0-9]{1}|19[3-9]{1}[0-9]{1})\.(1[0-2]{1}|0[1-9]{1})$'#YYYY.MM
    YYYYMM_v4   = r'^(20[0-1]{1}[0-9]{1}|19[3-9]{1}[0-9]{1})[^\d]+(1[0-2]{1}|[0-9]{1})$'#YYYY()MM
    
    MMYYYY        = r'^(1[0-2]{1}|[0-9]{1})\.(20[0-1]{1}[0-9]{1}|19[3-9]{1}[0-9]{1})$'#MM.YYYY
    
    YYYY        = r'^(20[0-1]{1}[0-9]{1}|19[3-9]{1}[0-9]{1})$'#YYYY
    YYYY_v2     = u'^(20[0-1]{1}[0-9]{1}|19[3-9]{1}[0-9]{1})\u5E74$'#YYYY年
    
    YC          = u'^(\d+)\u5E74$'#n年
    
    matchObj = re.compile(YYYYMMDD)
    m = matchObj.match(str)
    if m is not None:
        YY = int(m.group(1))
        MM = int(m.group(2))
        DD = int(m.group(3))
        #print '%s match %s'%(str,YYYYMMDD)
    else:
        matchObj = re.compile(YYYYMMDD_v2)
        m = matchObj.match(str)
        if m is not None:
            YY = int(m.group(1))
            MM = int(m.group(2))
            DD = int(m.group(3))
            #print '%s match %s'%(str,YYYYMMDD_v2)
        else:
            matchObj = re.compile(YYYYMMDD_v3)
            m = matchObj.match(str)
            if m is not None:
                YY = int(m.group(1))
                MM = int(m.group(2))
                DD = int(m.group(3))
                #print '%s match %s'%(str,YYYYMMDD_v3)
            else:
                matchObj = re.compile(YYYYMM)
                m = matchObj.match(str)
                if m is not None:
                    YY = int(m.group(1))
                    MM = int(m.group(2))
                    #print '%s match %s'%(str,YYYYMM)
                else:
                    matchObj = re.compile(YYYYMM_v2)
                    m = matchObj.match(str)
                    if m is not None:
                        YY = int(m.group(1))
                        MM = int(m.group(2))
                        #print '%s match %s'%(str,YYYYMM_v2)
                        #print YY,'-',MM
                    else:
                        matchObj = re.compile(YYYYMM_v3)
                        m = matchObj.match(str)
                        if m is not None:
                            YY = int(m.group(1))
                            MM = int(m.group(2))
                            #print '%s match %s'%(str,YYYYMM_v3)
                        else:
                            matchObj = re.compile(YYYYMM_v4)
                            m = matchObj.match(str)
                            if m is not None:
                                YY = int(m.group(1))
                                MM = int(m.group(2))
                                #print '%s match %s'%(str,YYYYMM_v4)
                            else:
                                matchObj = re.compile(MMYYYY)
                                m = matchObj.match(str)
                                if m is not None:
                                    YY = int(m.group(2))
                                    MM = int(m.group(1))
                                    #print '%s match %s'%(str,MMYYYY)
                                else:
                                    matchObj = re.compile(YYYY)
                                    m = matchObj.match(str)
                                    if m is not None:
                                        YY = int(m.group(1))
                                        #print '%s match %s'%(str,YYYY)
                                    else:
                                        matchObj = re.compile(YYYY_v2)
                                        m = matchObj.match(str)
                                        if m is not None:
                                            YY = int(m.group(1))
                                            #print '%s match %s'%(str,YYYY_v2)
                                        else:
                                            matchObj = re.compile(YC)
                                            m = matchObj.match(str)
                                            if m is not None:
                                                cr_year=time.strftime('%Y',time.localtime(time.time()))
                                                YY = int(cr_year)-int(m.group(1))
                                                #print '%s match %s'%(str,YC)
                                            else:
                                                pass
    if YY !=0:
        MM=1 if MM==0 else MM
        DD=1 if DD==0 else DD
        _str = '%d-%d-%d'%(YY,MM,DD)   
    else:
        _str=''#str              
    return _str


def arg_car_appearance(str):
    '''
    对车辆外观进行规整化
    '''
    if str is None or str=='':
        return ''
    result = ''
    matchObj = re.compile(u'^(\d?[\u4e00-\u9fa5]+)[^\u4e00-\u9fa5]*.*$',re.IGNORECASE)
    m = matchObj.match(str)
    if m is not None:
        result = m.group(1)
    return result

def arg_car_style(str):
    '''
    对车辆类型进行规整化
    '''
    if str is None or str=='':
        return ''
    result = ''
    reobj = re.compile(r'\d',re.IGNORECASE)
    result,number = reobj.subn(r'', str)
    return result


def _car_driv_license(str):
    '''
    对车辆行驶证规整化：有、没有、丢失   by yj
    '''
    
    result=None

    type_list = [u'有',u'齐全']
    not_type_list = [u'没']
    loss_type_list = [u'丢']

    for type in not_type_list:
        if str.find(type)>=0:
            result='没有'
            break;
    if result is None:
        for type in loss_type_list:
            if str.find(type)>=0:
                result='丢失'
                break;
    if result is None:
        for type in type_list:
            if str.find(type)>=0:
                result='有'
                break;   
    
    if result is None:
        result=''
            
    return result




def _car_fuel_type(str):
    '''
    对燃油类型时行规整化，分为：汽油、柴油、混合、双燃料、油电混合、电力  by yj
    '''
    result=None

    car_fuel_type_list = [u"汽油", u"柴油", u"油电混合", u"双燃料", u"混合", u"电力"]

    for type in car_fuel_type_list:
        if str.find(type)>=0:
            result=type
            break;
            
    return result


def _car_fule_mode(str):
    '''
         燃油供给方式，如果不含关键字“喷”或“电”或“油”将其过滤 by yj
    '''
    result=str

    type_list = [u"喷",u"电",u"油"]
    
    find=False
    for type in type_list:
        if str.find(type)>=0:
            find=True
            break
        
    if find==False:
        result=''
    return result


def _car_license(str):
    '''
    是否带车牌：有或没有。将其规整化  by yj
    '''
 
    result=None;

    type_list = [u'不',u'否',u'没']

    for type in type_list:
        if str.find(type)>=0:
            result='没有'
            break;
        
    if result is None:
        pattern = re.compile(u'[\u5305\u5e26\u542b].*\u724c|\u6709|\u662f|\u53ef\u4ee5|\u80fd')
        match = pattern.search(str)   
        if match:
            result = '有'
    
    if result is None:
        result=''
           
    return result   


def _car_engine(src):
    '''
          发动机号规整化
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

def _car_drive_type(str):
    '''
          车辆驱动形式  by yj
    '''
    if str is not None and str!='':
        str=str.strip()
        if str is None or str=='':
            return ''
        
    result=None
    
    if str.find(u'前轮驱动')>=0:
        return '前轮驱动'
    
    if str.find(u'后轮驱动')>=0:
        return '后轮驱动'
    
    type_list = [u'前置前驱',u'FF']
    for type in type_list:
        if str.find(type)>=0:
            return '前置前驱'
    
    type_list = [u'前驱',u'前轮']
    for type in type_list:
        if str.find(type)>=0:
            return '前轮驱动'

    type_list = [u'全时四驱',u'全时四轮驱动']
    for type in type_list:
        if str.find(type)>=0:
            return '全时四驱'  
    
    if str.find(u'前置四驱')>=0:
        return '前置四驱'
    
    if str.find(u'四轮驱动')>=0:
        return '四轮驱动'
    
    type_list = [u'前置后驱',u'FR']
    for type in type_list:
        if str.find(type)>=0:
            return '前置后驱'
        
    type_list = [u'适时四驱']
    for type in type_list:
        if str.find(type)>=0:
            return '适时四驱'  
    
    type_list = [u'分时四驱']
    for type in type_list:
        if str.find(type)>=0:
            return '分时四驱'
    
    type_list = [u'中置后驱',u'MR']
    for type in type_list:
        if str.find(type)>=0:
            return '中置后驱'
    
    type_list = [u'后置后驱','RR']
    for type in type_list:
        if str.find(type)>=0:
            return '后置后驱'
        
    type_list = [u'中置四驱']
    for type in type_list:
        if str.find(type)>=0:
            return '中置四驱'
    
    type_list = [u'后置四驱']
    for type in type_list:
        if str.find(type)>=0:
            return '后置四驱'
        
    type_list = [u'四驱',u'4驱',u'四轮',u'4轮']
    for type in type_list:
        if str.find(type)>=0:
            return '四轮驱动'
    
    type_list = [u'后驱',u'后轮',u'后区']
    for type in type_list:
        if str.find(type)>=0:
            return '后轮驱动'
        
    type_list = [u'双驱',u'两驱',u'2驱',u'２驱']
    for type in type_list:
        if str.find(type)>=0:
            return '两轮驱动'

#    regex    = u'\d{1,2}[\u58\u2a\u78\uff38\ud7\uff0a]\d'
    regex    = u'\d{1,2}[\u0058\u002a\u0078\uff38\u00d7\uff0a]\d'
    pattern = re.compile(regex)
    match = pattern.search(str)
    if match:
        matched=match.group()
        size=len(matched)
        num =matched[size-1:size]
        if num=='2':
            return '两轮驱动'
        if num=='4':
            return '四轮驱动'
    
    '''
           匹配纯粹数字的形式，如：2、4等
    '''
    if len(str)<=2:
        regex    = u'^(\d*.?\d*|[\uff10-\uff19]*[\u2e00\u3002]?[\uff10-\uff19]*)$'
        pattern = re.compile(regex)
        match = pattern.search(str)
        if match:
            matched=match.group()
            if matched=='2':
                return '两轮驱动'
            if matched=='4':
                return '四轮驱动'
                     
    if result is None:
        result=''
           
    return result     

def _car_steering(str):
    '''
          车辆驱动形式  by yj
    '''  
    if str is not None and str!='':
        str=str.strip()
        if str is None or str=='':
            return ''
        
    result=None
    
    regex    = u'\u81ea\u7136[\u5438\u8fdb]\u6c14'
    pattern = re.compile(regex)
    match = pattern.search(str)
    if match:
        return ''
        
    regex    = u'\u52a9\u529b|\u9f7f\u8f6e|\u9f7f\u6761'
    pattern = re.compile(regex)
    match = pattern.search(str)
    if match:
        return str
           
    if result is None:
        result=''
           
    return result     