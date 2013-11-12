#coding: utf-8
"""主要字段的规整化、涉及到分词提取，品牌、车系、车型识别
"""
import json

from base import ProcesserBase
from lib.bs_analyze import BrandSeriesAnalysis
from lib.simple_segment import segment
from lib.sqlite_db import CarSpecification
from lib.difflibext import DocumentCompare

class Processer(ProcesserBase):
    """主要字段的规整化、涉及到分词提取"""
    seq = "p22"
    
    def __init__(self):
        ProcesserBase.__init__(self) 

        self.cars = CarSpecification()
        self.seg_rule = [
            ("series_num_zh", u"(\d{2,4}).+[年款]?", 1),
            ("logo_zh", u"[\u2E80-\u9FFF]+[版型级]", 0),
            #("transmission_zh", u"(手动)|(自动)|(手波)|(手自一体)|(无极变速)|(双离合)", 0),
            #("transmission", u"([AM]T)|(A[^T]+T)|CVT|GSG", 0),
            ("engine", u"(\d\.\d?)(?![\d|万])(L|l|T|t|升|TSI|FSI|TFSI)?", 1),
            ("imports_zh", u"(进口)|(国产)|([\u2E80-\u9FFF]+)国", 0)]

        self.rule1 = [("car_type", "pattern_zh", 0.1, 'str'),
                      ("car_brand", "brand", 0.2, 'str'),
                      ("car_series", "series", 0.2, 'str'),
                      ("car_emission", "engine", 0.08, 'abs'),
                      ("car_transmission", "transmission_zh", 0.04, 'str'),
                      ("car_title", "logo_zh", 0.1, 'str'),
                      ("car_title", "pattern_zh", 0.13, 'str'),
                      ("car_title", "series_num_zh", 0.1, 'str'),
                      ("car_description", "pattern_zh", 0.023, 'str'),
                      ("car_birth", "producted_year", 0.03, 'str'),
                      ("purchase_price_refer", "indicative_price", 0.024, 'num'),]

    def _process(self, item, items, rule):
        """计算相似度，返回评分最高的一个
        """
        dc = DocumentCompare(rule)
        sim_rs = dc.mostsimilar(item, items)
        doc = sim_rs.get("doc")
        
        if doc:
            new_item = item.copy()
            new_item["car_type"] = doc["pattern_zh"]
            new_item["car_brand"] = doc["brand"]
            new_item["car_series"] = doc["series"]
            new_item["vehicle_code"] = doc["vehicle_code"]
            new_item["car_type_score"] = sim_rs["similarity"]
            self.logger.debug(repr(dc.opcodes))
            
            return new_item

    def simple_match(self, item, sseg, **kv):
        """主要评分算法，正则匹配提取，相似度计算
        1. 用正则提取标题里的年款，国别，车款描述，变速箱，排量信息
        2. 然后以提取出来的信息从数据库里查询匹配的车型，此时如果kv里面有品牌或者车系信息则加入到查询条件
        3. 最后将查询出来的车型与当前车源进行相似度计算
        返回评分最高的一个
        """
        results = sseg
        results.update(kv)
        datas = self.cars.get_car_data(**results)
        if not datas:
            datas = self.cars.get_car_data(**kv)
        try:
            f_item = self._process(item, datas, self.rule1)
            f_item['title_fetched'] = len(datas)
            self.logger.debug(repr(results))
            return f_item
        except:
            pass

    def simple_segment(self, title):
        """正则匹配提取
        """
        rs = segment(self.seg_rule, title)
        results = dict((k, v.get("content")) for k, v in rs.items() if v.get("content"))
        return results

    def process_final(self, item, **condition):
        """根据品牌(和排量)查询出该品牌下面所有的车型
        再将查询出来的车型与当前车源进行相似度计算
        返回评分最高的一个
        """
        vehicles = self.cars.get_vehicles_by_condition(**condition)
        f_item = self._process(item, vehicles, self.rule1)

        return f_item

    def process(self, data):
        data["car_brand_old"] = data['car_brand']
        data['car_series_old'] = data['car_series']
        data['car_type_old'] = data['car_type']

        def run(item):
            """主逻辑，如果识别成功，则返回更新过后的item
            否则返回(品牌, 车系)
            """
            # 一阶分数
            score_1 = 0
            # 二阶分数
            score_2 = 0
            # 三阶分数
            score_3 = 0

            bsa = BrandSeriesAnalysis(item)
            # 直接car_type与redbook里的parttern比较，
            if data['car_type']:
                car = bsa.verify_type(data['car_type'])
                if car:
                    item["car_type"] = car[3]
                    item["car_brand"] = car[1]
                    item["car_series"] = car[2]
                    item["vehicle_code"] = car[0]
                    item["car_type_score"] = 1
                    item['complete_step'] = u"车型完全匹配"
                    return item
            else:
                score_3 += 0.05
            
            # 验证当前品牌和车系，包括转换同义词
            new_brand = bsa.verify_brand()
            new_series = bsa.verify_series()
            if not new_brand and new_series:
                new_brand = self.cars.get_brand_by_series(new_series)

            sseg = self.simple_segment(item['car_title'])
            if item.get("car_emission"):
                sseg["engine"] = item["car_emission"]
            if item.get("car_publish_logo"):
                sseg["series_num_zh"] = item["car_publish_logo"]
            item['seg_title'] = json.dumps(sseg)
            new_displacement = sseg.get("engine") or bsa.verify_emission(item['car_emission'])

            if new_brand and new_series:
                smatched = self.simple_match(item, sseg, brand=new_brand, series=new_series)
                if smatched:
                    score_1 = 0.1
                    score_2 += 0.4
                    smatched['score_1'] = score_1
                    smatched['score_2'] = score_2
                    smatched['score_3'] = smatched['car_type_score']*40/100
                    smatched['car_type_score'] = (score_1 + score_2) + smatched['car_type_score']*40/100
                    smatched['complete_step'] = u"缺省品牌和车系校验通过"
                    return smatched
            # 如果以上步骤均未得出识别结果，则求助于jieba分词
            segs = bsa.verify_segment()
            seg_brand = segs.get("brand")
            seg_series = segs.get("series")
            if not seg_brand and seg_series:
                seg_brand = self.cars.get_brand_by_series(seg_series)
            if seg_brand and seg_series:
                score_1 = 0.1
                score_2 += 0.4
                smatched = self.simple_match(item, sseg, **segs)
                if smatched:
                    smatched['seg_brand'] = seg_brand
                    smatched['seg_series'] = seg_series
                    smatched['score_1'] = score_1
                    smatched['score_2'] = score_2
                    smatched['score_3'] = smatched['car_type_score']*40/100
                    smatched['car_type_score'] = (score_1 + score_2) + smatched['car_type_score']*40/100
                    smatched['complete_step'] = u"分词品牌和车系校验通过"
                    return smatched
                
            # 如果品牌通过验证，则进入主要评分算法如果算法有返回，则车型识别结束
            if new_brand:
                smatched = self.simple_match(item, sseg, brand=new_brand)
                if smatched:
                    score_1 = 0.05
                    score_2 += 0.4
                    smatched['score_1'] = score_1
                    smatched['score_2'] = score_2
                    smatched['score_3'] = smatched['car_type_score']*40/100
                    smatched['car_type_score'] = (score_1 + score_2) + smatched['car_type_score']*40/100
                    smatched['complete_step'] = u"缺省品牌校验通过"
                    return smatched

            if seg_brand:
                smatched = self.simple_match(item, sseg, brand=seg_brand)
                if smatched:
                    score_1 = 0.05
                    score_2 += 0.4
                    smatched['score_1'] = score_1
                    smatched['score_2'] = score_2
                    smatched['score_3'] = smatched['car_type_score']*40/100
                    smatched['car_type_score'] = (score_1 + score_2) + smatched['car_type_score']*40/100
                    smatched['complete_step'] = u"分词品牌校验通过"
                    return smatched

            # 最后补救，处理只有一个品牌被识别的情况，
            # 在品牌和车系都还未知的情况下，只根据正则提取出来的关键字从sqlite里查找相应的车型
            # 如果有记录，并且记录数小于100(为保证运行效率，只处理数量小于100的)，
            # 则进行评分，得到结果后直接返回，车型识别结束
            if len(sseg) > 2:
                datas = self.cars.get_car_data(**sseg)
                if 0 < len(datas) <= 100:
                    t_item = self._process(item, datas, self.rule1)
                    t_item['title_fetched'] = len(datas)
                    score_2 += 0.1
                    t_item['score_1'] = score_1
                    t_item['score_2'] = score_2
                    t_item['score_3'] = t_item['car_type_score']*40/100
                    t_item['car_type_score'] = (score_1 + score_2) + t_item['car_type_score']*40/100
                    t_item['complete_step'] = '标题关键字抽取后匹配'
                    return t_item

        ritem = run(data)
        if ritem:
            self.logger.info("Processed an item: %s, VID: %s, Score: %f, title fetched %d items." % \
                             (ritem["id"],
                              ritem["vehicle_code"],
                              ritem["car_type_score"],
                              ritem.get("title_fetched", 0)))

            if ritem['car_brand'] not in ritem['car_title']:
                self.logger.warning(u"@car_brand (%s) not in car_title (%s)!!!" % (ritem['car_brand'], ritem['car_title']))
            if ritem['car_series'] not in ritem['car_title']:
                self.logger.warning(u"@car_series (%s) not in car_title (%s)!!!" % (ritem['car_series'], ritem['car_title']))
            return ritem
        else:
            # 若此时品牌还没有被识别，则放弃该条车源 Just no idea!
            self.logger.warning('(%s) Item ignore, brand not found![id]: %s [brand]: %s, [series]: %s, [title]: %s' % \
                                (data.get('domain', 'None'), data['id'], data['car_brand'], data['car_series'], data['car_title']))


def test():
    import redis
    import pymongo

    from lib.index_port.client import pusher

    #rd = redis.Redis(host='192.168.2.228', db=14)

    #p = pusher()
    
    mconn = pymongo.Connection('192.168.2.228', 2281)
    mdb = mconn['dcrawler']
    
    #items = mdb.car_info.find({'car_series': '200'}, timeout=False)
    items = mdb.car_info.find({'id': 'ed659b4257b259e363739ad024a2001b'})
    #items = mdb.car_info.find({'shorturl': 'hxcf1isyb'})
    #items = mdb.car_info.find(timeout=False).skip(1000000)

    ps = Processer()
    for item in items:
        item["purchase_price_refer"] = 99300
        #if rd.sismember('car_type_push', unicode(item['_id'])):
        #    continue
        #item["car_brand"] = item.get("car_brand_old", item["car_brand"])
        #item['car_series'] = item.get('car_series_old', item['car_series'])
        #item['car_type'] = item.get('car_type_old', item['car_type'])
        #item['car_brand_old'] = ''
        #item['car_series_old'] = ''
        #item['car_type_old'] = ''

        try:
            rs = ps.process(item)
        except Exception, e:
            #rd.sadd('car_type_error', unicode(item['_id']))
            print "Error: item %s process error!!" % unicode(item['_id'])
            print e
            continue
        if rs:
            print "title: %s" % item['car_title']
            print "url: %s" % item['url']
            print "car_brand old: '%s'" % item['car_brand']
            print "car_brand new: '%s'" % rs['car_brand']
            print "car_series old: '%s'" % item['car_series']
            print "car_series new: '%s'" % rs['car_series']
            print "car_type old: '%s'" % item['car_type']
            print "car_type new: '%s'" % rs['car_type']
            print "vehicle_code: %s" % rs['vehicle_code']
            #print "score_1: %s, score_2: %s, score_3: %s" % (rs['score_1'], rs['score_2'], rs['score_3'])
            #print "score: %s" % rs['car_type_score']
            #print "complete step: %s" % rs['complete_step']
            #if rs.get("seg_title"):
            #    print u"标题提取结果:"
            #    for kv in json.loads(rs.get("seg_title")).items():
            #        print '[ %s ==> %s ]' % kv
            #print u"标题分词结果: brand = '%s', series = '%s'" % (rs.get('seg_brand', 'None'), rs.get('seg_series', 'None'))
            """
            if 'complete_step' in rs:
                del rs['complete_step']
            if 'seg_title' in rs:
                del rs['seg_title']
            if 'seg_brand' in rs:
                del rs['seg_brand']
            if 'seg_series' in rs:
                del rs['seg_series']
            """
            #try:
            #    push_rs = p.push(rs)
            #except:
            #    rd.sadd('car_type_error', unicode(item['_id']))
            #    print "Error: item %s push error!!" % unicode(item['_id'])
            #    continue
                
            #rd.sadd('car_type_push', unicode(item['_id']))
            #rd.srem('car_type_error', unicode(item['_id']))
            #print '### Push index ok with result: %s ###' % str(push_rs)
            
        else:
            print "[Warning!!!]item has been ignore, url: %s" % item['url']
        print "========================================================="

if __name__ == '__main__':
    #test()
    ps = Processer()
    ps.work()
