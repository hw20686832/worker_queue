#coding: utf-8
"""
直辖市区域转换
"""
from base import ProcesserBase

_CITY = [u'北京', u'上海', u'天津', u'重庆']

class Processer(ProcesserBase):
    seq = "p87"
    
    def process(self, item):
        if item.get('source_province') in _CITY:
            item['source_zone'] = item['source_province']

        return item


if __name__ == '__main__':
    p = Processer()
    p.work()
