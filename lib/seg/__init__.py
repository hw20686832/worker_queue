#coding: utf-8
import os, sys
import re
import json

import requests
import jieba

CAR_ALL_URL = 'http://admin.365auto.com:8080/provider/dict/car/'
CAR_ALL_URL_V = "http://admin.365auto.com:8080/provider/dict/version/car"
ZONE_URL = 'http://admin.365auto.com:8080/provider/dict/district'
ZONE_VERION_URL = 'http://admin.365auto.com:8080/provider/dict/version/district'

locate = os.path.dirname(os.path.realpath(__file__))

def flush_dict():
    with open(os.path.join(locate, 'mydict_version')) as v:
        vo = json.loads(v.read())

    try:
        br_v = requests.get(CAR_ALL_URL_V, timeout=60).content
        ze_v = requests.get(ZONE_VERION_URL, timeout=60).content
    except:
        return

    categories = [('brand', 'cb'), ('brand_synonyms', 'cb'),
                  ('series', 'cf'), ('series_synonyms', 'cf'),
                  ('style_standard', 'ctp'), ('style_extend', 'ctp'),
                  ('transmission_standard', 'ctm'), ('transmission_extend', 'ctm'),
                  ('appearance_standard', 'cc'), ('appearance_extend', 'cc')]

    city_map = {'province': 'pr', 'city': 'cty', 'county': 'dtr', 'synonyms': 'zny'}

    lines = []
    if (vo['car_brand_series'], vo['province_city_county']) != (br_v, ze_v):
        for c, tp in categories:
            data = json.loads(requests.get(CAR_ALL_URL + c).content)
            lines.extend(['%s %d %s\n' % (re.sub('\s', '', x.encode('utf-8')), 35000 if tp == 'cb' else 30000, tp) for x in data if not x.isdigit()])

        zonedata = json.loads(requests.get(ZONE_URL).content)
        for z, d in zonedata.items():
            lines.extend(['%s 30000 %s\n' % (re.sub('\s', '', x.encode('utf-8')), city_map[z]) for x in d if re.match(u'^[\u4E00-\u9FA5]+$', x)])

        with open(os.path.join(locate, 'userdict.txt'), 'w') as ud, \
                 open(os.path.join(locate, 'mydict_version'), 'w') as v:
#                 open(os.path.join(locate, 'orig_dict.txt')) as orig:
#            lines.extend(orig.readlines())
            ud.writelines(lines)
            json.dump({'car_brand_series': br_v, 'province_city_county': ze_v}, v)

flush_dict()
jieba.load_userdict(os.path.join(locate, "userdict.txt"))

from segment import *

