#encoding:utf-8
"""
清除Field数量不足69个的数据
"""
import hashlib

from base import ProcesserBase
from lib.droping_rabbitmq import dr

class processer(ProcesserBase):
    """数据清洗初步准备"""
    seq = "p00"
    def __init__(self):
        ProcesserBase.__init__(self)        
        self.sites={'cdtaoche': u'成都淘车网',
                    'ihcar': u'换车网',
                    '4c27': u'换车网',
                    '1car1': u'一车一网',
                    '21che': u'苏州二手车网',
                    'nj2sc': u'南京二手车交易网',
                    'yzjdc': u'扬州机动车交易网',
                    'che168': u'二手车之家',
                    'yescar': u'亚迅车网',
                    'cheshi': u'网上车市',
                    '51auto': u'51汽车网',
                    'socars': u'搜车网',
                    'hx-car': u'互信二手汽车网',
                    'hx2car': u'华夏二手车网',
                    'usedcar': u'我卖我车',
                    'zg2sc': u'中国二手车网',
                    'cn2che': u'中国二手车城',
                    'webcars': u'万车网',
                    'taotaocar': u'淘淘二手车',
                    'tzqiche': u'台州二手汽车网',
                    'qcwe': u'搜车网',
                    'sc2car': u'四川二手车',
                    'ln2car': u'辽宁二手车',
                    'kuche': u'酷车网',
                    'qiche': u'第一二手汽车网',
                    '2duche': u'二度车网',
                    'db2car': u'东北二手车网',
                    'baixing': u'百姓网',
                    'ganji': u'赶集网',
                    'car668': u'中国二手车市场',
                    '273': u'中国二手车交易网',
                    '1775': u'二手车网',
                    'che2': u'二手车之家',
                    'iautos': u'第一车网',
                    '58': u'58同城',
                    'taoche': u'淘车网',
                    '9che': u'旧车网'}
    def process(self,data):
        self.logger.info("(%s) Item start processing." % data['domain'])
        # 缺少url字段的为严重残缺数据
        if not data.has_key('url'):
            self.logger.debug('Item ignore, document lacks of url field, drop it')
            return None
        # 补充id
        if not data.has_key('id'):
            md5 = hashlib.md5()
            md5.update(data['url'])
            id = md5.hexdigest().upper()
            data['id'] = id
        if data["domain"]=="2s.qiche.com":
            data["spider"]="qiche"
        else:
            data["spider"]=data["domain"].split(".")[0]
        if self.sites.has_key(data["spider"]):
            data["site"]=self.sites[data["spider"]]
        keys=["car_title","car_brand","car_series","contact_phone","contact_mobile","car_price",
              "source_province","source_zone","car_mileage","car_emission","car_transmission","car_type",
              "car_seats","car_cylinder","car_doors","car_drive_type","car_outer_color","car_inner_color",
              "car_birth","purchase_date","car_reg_time","car_enter_time","car_images","car_img_thumb",
              "car_keywords","car_description","source_birth","contact","car_broker","car_age",
              "car_insur_validity","car_inspection_date","car_style","car_engine","car_frame",
              "car_fuel_type","car_fule_mode","car_steering","car_origin","car_repaired","car_usage",
              "car_modified","car_appearance","car_interior","car_chassis","car_condition",
              "purchase_price","source_validity","contact_mail","contact_qq","contact_addr",
              "car_insurance","car_driv_license","car_invoice","car_surcharge","car_tax_valid",
              "car_license","car_license_type","car_license_at"]
        for key in keys:
            if not data.has_key(key):
                data[key]=""

        return data

if __name__ == '__main__':
    ps=processer()
    ps.work()
    
