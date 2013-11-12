#coding: utf-8
from lib.sqlite_db import CarSpecification

class BrandSeriesAnalysis(object):
    """本类主要负责品牌与车系和车型的校验与分词提取
    """
    def __init__(self, item):
        self.item = item
        self.cars = CarSpecification()
        self.seg_rs = None

    @property
    def seg(self):
        from lib.seg import split
        self.seg_rs = self.seg_rs or split(self.item['car_title'])
        return self.seg_rs

    def verify_segment(self):
        if u"别克" in self.seg["cf"]:
            self.seg["cb"] = {u"别克"}
            self.seg["cf"].remove(u"别克")
        for cb in self.seg['cb']:
            for cf in self.seg['cf']:
                if self.verify_brandseries(cb, cf):
                    return {'brand': cb, 'series': cf}

        for cf in self.seg['cf']:
            return {'series': cf}

        for cb in self.seg['cb']:
            return {'brand': cb}

        return {}

    def verify_brand(self):
        # 品牌校验
        brand = self.item["car_brand"]
        brand = self.cars.trans_synonyms_brand(brand)
        return self.cars.has_brand(brand)

    def verify_series(self):
        # 车系校验
        serie = self.item["car_series"]
        serie = self.cars.trans_synonyms_series(serie)
        return self.cars.has_series(serie)

    def verify_brandseries(self, b, s):
        brand = self.cars.get_brand_by_series(s)
        return brand == b

    def verify_type(self, t):
        return self.cars.has_type(self.item["car_type"])

    def verify_emission(self, e):
        # 排量校验
        return self.cars.has_emission(e)

