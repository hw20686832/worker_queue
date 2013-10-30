#encoding:utf-8
'''
Created on 2012-5-14

@author: yj
'''

import re
import time
import common
#
#def _replace58Tinyimg(img):
#    '''
#    58ͬ�ǵ�car_images�洢��������ͼ��ַ�������Ϊ��ͼ��ַ
#    '''
#    reobj = re.compile(r'/tiny/',re.IGNORECASE)
#    result,number = reobj.subn(r'/big/', img)
#    return result
#
#
#def _arrange58img(img):
#    '''
#    58ͬ�ǵ�car_img_thumb|car_images�洢�Ķ��ͼƬ��ַ֮��û�зָ������ָ���###�� 
#    '''
#    reobj = re.compile(r'.jpghttp',re.IGNORECASE)
#    result,number = reobj.subn(r'.jpg###http', img)
#    return result

def _is_car_title_lose(str):
    '''
          判断是否缺少car_title，如果缺少则返回true，否则返回false
    '''
    if (str is None or str == ''):
        return True
    
    str = str.strip()
    
    if (str is None or str == ''):
        return True
    
    return False

def _is_car_brand_car_series_lose(car_brand,car_series):
    '''
          判断是否同时缺少car_brand和car_series，如果缺少则返回true，否则返回false
    '''
    
    if (car_brand is None or car_brand == '') and (car_series is None or car_series == ''):
        return True
    
    if (car_brand is not None and  car_brand != ''):
        car_brand=car_brand.strip()      
    if (car_series is not None and  car_series != ''):
        car_series=car_series.strip()

    if (car_brand is None or car_brand=='' or car_brand==u'其它') and (car_series is None or car_series==u'其它' or car_series==''):
        return True
    
    return False


def _is_car_mileage_lose(mileage):
    '''
           判断是否缺少car_mileage，如果缺少则返回true，否则返回false
    '''
    
    if (mileage is None or mileage=='' or mileage == 0):
        return True

    return False

def _is_car_price_lose(price):
    '''
           判断是否缺少car_price，如果缺少则返回true，否则返回false
    '''
    if (price is None or price < 0.0):
        return True

    return False

def _is_contact_phone_contact_mobile_contact_mail_contact_qq_lose(contact_phone,
                                                                  contact_mobile,
                                                                  contact_mail,
                                                                  contact_qq):
    '''
          判断是否同时缺少contact_phone、contact_mobile、contact_mail、contact_qq，
          如果缺少则返回true，否则返回false
    '''
     
    if (contact_phone is None or contact_phone == '' or contact_phone.strip() == '') and (contact_mobile is None or contact_mobile == '' or contact_mobile.strip() == '') and (contact_mail is None or contact_mail == '' or contact_mail.strip() == '') and (contact_qq is None or contact_qq == '' or contact_qq.strip() == ''):
        return True
 
    return False

def _is_source_province_source_zone_lose(source_province,source_zone):
    '''
          判断是否同时缺少source_province、source_zone，
          如果缺少则返回true，否则返回false
    ''' 
    if (source_province is None or source_province == '') and (source_zone is None or source_zone == ''):
        return True
    
    if (source_province is not None and  source_province != ''):
        source_province=source_province.strip()      
    if (source_zone is not None and  source_zone != ''):
        source_zone=source_zone.strip()

    if (source_province is None or source_province=='') and (source_zone is None or source_zone==''):
        return True

    return False