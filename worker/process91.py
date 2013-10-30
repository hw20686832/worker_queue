#coding: utf-8
"""
年款，型款，排量提取和车型短描述生成
"""
import re

from base import ProcesserBase
from lib.simple_segment import segment
from lib.sqlite_db.syncdb import conn

class Processer(ProcesserBase):
    """
    年款，型款，排量提取和车型短描述生成
    car_publish_logo, 根据车型识别后的vehicle_code去对应redbook，补充年款说明。
      年款说明首先从车型描述中提取，在车型中没有的情况下再根据redbook中的生产年份补充
    car_publish_version 根据车型识别后的vehicle_code去对应redbook，补充版型说明。从车型描述中提取，例如：标准版、豪华型。
    standard_title 根据车型识别后的vehicle_code去对应redbook，生成车源标题短描述。
      车源短描述的组成（不含括号）：【品牌】【车系】【年款】【版型】【变速箱】【排量】
    其中的排量，有的是L有的是T，所以，首先应当从标题中提取排量全称，提取不到的情况下根据redbook。
    """
    seq = "p91"
    
    def __init__(self):
        ProcesserBase.__init__(self)

    def process(self, item):
        seg_rule = [("producted_year", u"(\d{2,4}).+[年款]?", 1),
                    ("logo_zh", u"^.+[版型级]", 0),
                    ("transmission_zh", u"(手动)|(自动)|(手波)|(手自一体)|(无极变速)|CVT|([AM]T)|(A[^T]+T)", 0),
                    ("engine", u"(\d\.\d?)(?![\d|万])(L|l|T|t|升|CVT|TSI|TFSI)?", 1),
                    ("imports_zh", u"(进口)|(国产)|([\u2E80-\u9FFF]+)国", 0)]
        vid = item['vehicle_code']
        seg_rule.extend([('car_brand', item['car_brand'], 0),
                         ('car_series', item['car_series'], 0)])
        sseg = segment(seg_rule, item['car_title'])
        cursor = conn.cursor()
        cursor.execute("select producted_year, logo_zh, engine, transmission_zh from car_datas where vehicle_code = ?", (vid, ))
        rb_rs = cursor.fetchone()
        rb = dict(zip([i[0] for i in cursor.description], rb_rs))
        
        #年款
        car_publish_logo = sseg['producted_year']['content']
        if not car_publish_logo:
            car_publish_logo = rb['producted_year']

        def repl(obj):
            num = obj.group()
            inum = int(num)
            if inum < 1000:
                if inum < 80:
                    y = inum + 2000
                else:
                    y = inum + 1900
            else:
                y = inum

            if 1985 < y < 2014:
                return str(y)

        if car_publish_logo:
            car_publish_logo = re.sub('\d+', repl, car_publish_logo)
        #版型
        car_publish_version = sseg['logo_zh']['content']
        if not car_publish_version:
            car_publish_version = rb['logo_zh'] or ''
        #排量
        car_emission = sseg['engine']['content']
        if not car_emission:
            car_emission = rb['engine']
        #车型短描述
        keywords = [item['car_brand'],
                    item['car_series'],
                    car_publish_logo,
                    car_publish_version,
                    rb['transmission_zh'],
                    car_emission]
        
        standard_title = ' '.join([k for k in keywords if k])

        item['car_publish_logo'] = car_publish_logo
        item['car_publish_version'] = car_publish_version
        item['standard_title'] = standard_title

        return item
        

if __name__ == '__main__':
    ps = Processer()
    ps.work()
            
