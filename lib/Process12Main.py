#encoding:utf-8
'''
Created on 2012-5-10

@author: yj
'''

import re
import time
import common
import datetime


def _get_date_by_regex(src):

    '''
          提取日期时间，将其整理成：YYYY-MM-DD；
    '''
    if src is None or src=='' or src.strip()=="" or src.strip()=="-" or src.strip()=="--":
        return ''
    
    src=src.strip()
    
    result = ''

    pattern = re.compile(u'\d{2,4}.{0,4}\u5e74.{0,4}\d{1,2}.{0,4}\u6708.{0,4}\d{1,2}.{0,4}\u65e5')   
    patternDate11 = re.compile(u'\D{0,4}\u5e74\D{0,4}')
    patternDate12 = re.compile(u'\D{0,4}\u6708\D{0,4}')
    patternDate13 = re.compile(u'\D{0,4}\u65e5')
#    patternDate2 = re.compile(r'(\d{2,4}\s{0,5}年\s{0,5}\d{1,2}\s{0,5}月)')
    patternDate2 = re.compile(u'(\d{2,4}\s{0,5}\u5e74\s{0,5}\d{1,2}\s{0,5}\u6708)')
    patternDate21 = re.compile(u'(\s{0,5}\u5e74\s{0,5})')      
    patternDate22 = re.compile(u'(\s{0,5}\u6708)') 
    patternDate3 = re.compile(u'(\d{4}.{0,4}\u5e74)')
    patternDate31 = re.compile(u'\d{4}') 


    patternDate6 = re.compile(r'\d{2,4}.{0,4}-.{0,4}\d{1,2}.{0,4}-.{0,4}\d{1,2}')   
    patternDate61 = re.compile(r'(\D{0,5}-\D{0,5})')
    patternDate7 = re.compile(r'(\d{2,4}\s{0,5}-\s{0,5}\d{1,2})')   
    patternDate8 = re.compile(r'\d{4}')  

    match = pattern.search(src)   

    if match:      
        result = match.group()
#        print  result
        tempResult1 = patternDate11.sub("-", result)
        tempResult2 = patternDate12.sub("-", tempResult1)
        result = patternDate13.sub("", tempResult2)
    else:  
        match = patternDate2.search(src)
        if match: 
            result = match.group() 
            tempResult1 = patternDate21.sub("-", result)
            tempResult2 = patternDate22.sub("-", tempResult1)
            result = tempResult2 + '01'
        else:
            match = patternDate3.search(src)   
            if match:
                result = match.group() 
                match = patternDate31.search(result) 
                if match:
                    result = match.group()
                    result = result + '-01-01'
            else:
                match = patternDate6.search(src)   
                if match:
                    result = match.group() 
                    result = patternDate61.sub("-", result)
                else:
                    match = patternDate7.search(src)   
                    if match:
                        result = match.group() 
                        tempResult1 = patternDate61.sub("-", result)
                        result = tempResult1 + '-01'
                    else:
                        match = patternDate8.search(src)   
                        if match:
                            result = match.group() 
                            result = result + '-01-01'
#    print  '---------------'+result+'---------------------'      
    if result is None or result=='':
        return ''      
    yyyymmdd=result.split('-')
    yyyy=yyyymmdd[0]
    yyold=yyyy
    yy=int(time.strftime('%Y'))
    if len(yyyy)==2:
        yyyy='20'+yyyy
    if int(yyyy)>=(yy+5):
        yyyy='19'+yyold
    mm=yyyymmdd[1]
    if len(mm)==1:
        mm='0'+mm
    dd=yyyymmdd[2]
    if len(dd)==1:
        dd='0'+dd
    result=yyyy+'-'+mm+'-'+dd
    
    return result

#print _get_date_by_regex(u"12年12月")

def _is_match_regex(src,regex):
    '''
    car_type规整化
    '''
    flag=False
    
    matchObj = re.compile(regex)
    match = matchObj.search(src)
    if match:
        flag=True 
        
    return flag

def _car_frame(src):
    '''
    car_frame规整化
    '''
    flag=False
    tar = ''  
    if src is not None and src!='':
        src=src.strip()
        if src is not None and src!='':
            if len(src)<=1:
                return ''
            tar=src
            regex    = u'^(\d*.?\d*|[\uff10-\uff19]*[\u2e00\u3002]?[\uff10-\uff19]*)$'
            flag=_is_match_regex(src,regex)        
            if not flag:
#                regex    = u'^([\u002a\u002d\u002c]+)$'
                regex    = u'^([\u002a\u002d]+)$'
                flag=_is_match_regex(src,regex)
                if not flag:
                    regex    = u'(\u4e0d(\u660e\u767d|\u77e5\u9053))|(\u4fdd\u5bc6)|(\u51fa\u552e)'
                    flag=_is_match_regex(src,regex)
    if flag:
        return ''          
    return tar


def _car_cylinder(str):
    '''
          提取日期时间，将其整理成：YYYY-MM-DD；
    '''
   
    result = '';

    regex1=u'[\u0031-\u0039]{1,3}'
    regex2=u'[\u4e00\u4e8c\u4e09\u56db\u4e94\u516d\u4e03\u516b\u4e5d\u5341]{1,5}'
    regex3=u'[\u5355\u53cc]'
    pattern1 = re.compile(regex1)
    patternRelace = re.compile(r'[lL]\d{1,3}')    
    ustr = patternRelace.sub("", str)
#    ustr=unicode(str,'utf8') 

    match = pattern1.search(ustr)   
    if match: 
        result = match.group()
        return result
    else:
        pattern2 = re.compile(regex2)
        match = pattern2.search(ustr)
        if match:      
            result = match.group()
            if result==u'一':
                result='1'
            elif result==u'二': 
                result='2'
            elif result==u'三': 
                result='3'
            elif result==u'四': 
                result='4'
            elif result==u'五': 
                result='5'
        elif result==u'六': 
            result='6'
        elif result==u'七': 
            result='7'
        elif result==u'八': 
            result='8'
        elif result==u'九': 
            result='9'
        elif result==u'十': 
            result='10'
        else:
            pattern3 = re.compile(regex3)
            match = pattern3.search(ustr)
            if match: 
                result = match.group()
                if result==u'单':
                    result='1'     
                else:
                    result='2' 
        return result

def _date_time(src):
    '''
          提取日期时间，将其整理成：YYYY-MM-DD；
    '''
    return _get_date_by_regex(src)


def _source_validity(src):
 
    '''
        信息有效期为整数（默认单位‘天’），将值规整化为整数。含有日期的，要将日期推算为整数
    '''
    
    if src is None or src=='' or src.strip()=='':
        return ''
    
    src=src.strip()
    
    result = ''

    regex=u'[1-9]{1}\d*\u5929'
    pattern = re.compile(regex) 
    match = pattern.search(src)   
    if match:      
        result = match.group()
        length=len(result)
        return result[0:length-1]
    if len(src)<=4:
        regex=r'[1-9]{1}\d{0,3}'
        pattern = re.compile(regex) 
        match = pattern.search(src)   
        if match:      
            result = match.group()
            return result
    
    result=_get_date_by_regex(src)
    if result is None or result=='' or src.strip()=="":
        return ''
    results= result.split('-')
    if len(results)<=1:
        return ''
    year=int(results[0])
    mon=int(results[1])
    day=int(results[2])
    SourceValidityDate=datetime.date(year,mon,day)
    currTime=time.strftime('%Y-%m-%d',time.localtime(time.time()))
    currTimes=currTime.split('-');
    year=int(currTimes[0])
    mon=int(currTimes[1])
    day=int(currTimes[2])
    currDate=datetime.date(year,mon,day)
    result= (SourceValidityDate-currDate).days
    
    return result
    

def _car_deadweight(str):
    '''
        载重量应该是数字型（默认单位‘吨’）
    '''
    result = '';
    
    pattern = re.compile(r'\d*.\d+|[1-9]{1}\d*')   
    match = pattern.search(str)   

    if match:      
        result = match.group()  
    return result


def _car_doors(str):
    '''
        整理车辆座位数为整数类型
    '''
    result = '';
    
    pattern = re.compile(r'[1-9]{1}\d*')   
    match = pattern.search(str)   
    if match:      
        result = match.group()  
        
    return result

def _car_seats(str):
    '''
        整理车辆座位数为整数类型
    '''
    result = '';
    
    pattern = re.compile(r'[1-9]{1}\d*')   
    match = pattern.search(str)   
    if match:      
        result = match.group()  
        
    return result
