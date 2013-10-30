#coding: utf-8
from lib.sqlite_db import CarSpecification
from lib.seg import split

class BrandSeriesAnalysis(object):
    """本类主要负责品牌与车系和车型的校验与提取
    """
    def __init__(self, item):
        self.item = item
        self.cars = CarSpecification()
        self.seg_rs = None

    @property
    def seg(self):
        self.seg_rs = self.seg_rs or split(self.item['car_title'])
        return self.seg_rs

    def verify_segment(self):
        for cb in self.seg['cb']:
            for cf in self.seg['cf']:
                if self.verify_brandseries(cb, cf):
                    return {'brand': cb, 'series': cf}

        for cf in self.seg['cf']:
            return {'series': cf}

        for cb in self.seg['cb']:
            return {'brand': cb}

        return {}

    def extract_brand(self):
        # 品牌分词提取
        brand = None
        for w in self.seg['cb']:
            brand = self.verify_brand(w)
            if brand:
                break
            
        return brand

    def extract_series(self):
        # 车系分词提取
        series = None
        for w in self.seg['cf']:
            series = self.verify_series(w)
            if series:
                break

        return series

    def verify_brand(self, b):
        # 品牌校验
        brand = b
        brand = self.cars.trans_synonyms_brand(brand)
        return self.cars.has_brand(brand)

    def verify_series(self, s):
        # 车系校验
        serie = s
        serie = self.cars.trans_synonyms_series(serie)
        return self.cars.has_series(serie)

    def verify_brandseries(self, b, s):
        brand = self.cars.get_brand_by_series(s)
        return brand == b

    def verify_type(self, t):
        car_type = self.cars.has_type(t)
        return car_type

    def verify_emission(self, e):
        # 排量校验
        return self.cars.has_emission(e)

