#!/usr/bin/env python
#coding: utf-8
import re
from optparse import OptionParser
from collections import defaultdict

from pymongo import Connection

def segment(rule, strs):
    """正则提取，根据指定的规则从字符串中提取相应的文字，规则格式为tuple list
    主要用来提取年款，国别，排量，变速箱，车款描述(如舒适型，豪华型之类)
    由于车款描述的字数不固定，所以当确定好其他的提取字段之后，找到左边离(级型款)
    等字眼最近的一个匹配的位置，从这个位置截断，然后再根据一些分割字符分割后，
    取最后一个就是车款描述
    规则说明：
    [('字段描述', '正则', 正则分组编号), ...]
    """
    if not strs:
        strs = ''
    rule = dict((k, (re.compile(v, re.I), p)) for k, v, p in rule)
    dd = defaultdict(lambda: defaultdict(str))
    
    try:
        logo_s = rule["logo_zh"][0].search(strs).end()
    except:
        logo_s = 0
    prev_pos = 0
    for k, (v, p) in rule.items():
        cur_pos = 0
        dd[k]['re'] = v.pattern
        smatch = v.search(strs)
        if smatch:
            cur_pos = smatch.end()
            dd[k]['pos'] = cur_pos
            dd[k]['content'] = smatch.group(p)
        if k != "logo_zh":
            # 得出logo_zh左边第一个匹配项的位置
            if logo_s > cur_pos > prev_pos:
                prev_pos = cur_pos

    # 从离logo_zh最近的一个匹配的位置截断
    logo = dd["logo_zh"]["content"][prev_pos:]
    new_logo = re.split(u",|，|\s+|/|'|\"|\(|\)", logo)[-1]
    dd["logo_zh"]["content"] = new_logo
        
    return dd

def test(seg_rule):
    mongo = Connection(host='192.168.2.219')
    db = mongo["dcrawler_final"]

    spiders = ['51auto', 'che168', 'iautos', 'ucar', '58', 'ganji', 
               '273', 'che668', 'qcwe', 'hx2car', 'qiche', '2duche']
    rs = {}
    for s in spiders:
        print "Loading %s." % s
        cursor = db.car_info.find({'spider': s}).limit(100)
        rs[s] = list(cursor)

    print "Get all data OK."
    for spider, items in rs.items():
        f = open("./result/%s.txt" % spider, 'w')
        for item in items:
            seg = segment(seg_rule, item['car_title'])
            line = u'[title]: %s \n>>> {%s}\n' % (item['car_title'],
                                                  ', '.join(["'%s': '%s'" % (k, v.get('content')) for k, v in seg.items() if v.get('content')]))
            f.write(line.encode('utf-8'))
        f.close()


if __name__ == "__main__":
    import sys

    #title = u"【上海】 奔驰 B级(进口) 2009款 B200 时尚型 2.0L"
    #title1 = u"【上海】 奔驰 ML级(进口) 2010款 ML350 4MATIC 豪华型特别版"
    seg_rule = [("producted_year", u"(\d{2,4}).+[年款]?", 1),
                ("logo_zh", u"^.+[版型级]", 0),
                ("transmission_zh", u"(手动)|(自动)|(手波)|(手自一体)|(无极变速)|([AM]T)|(A[^T]+T)", 0),
                ("engine", u"(\d\.\d?)(?![\d|万])(L|l|T|t|升|CVT|TSI)?", 1),
                ("imports_zh", u"(进口)|(国产)|([\u2E80-\u9FFF]+)国", 0)]

    parser = OptionParser()
    parser.add_option("-s", "--title", dest = "TITLE",
                      help = "Specify a title string for analyze.")
    parser.add_option("-t", "--test", action="store_true", dest = "TEST",
                      help = "Run test.")
    options, args = parser.parse_args()
    if options.TEST:
        test(seg_rule)
    elif options.TITLE:
        seg = segment(seg_rule, options.TITLE.decode("utf-8"))
        for k, v in seg.items():
            print k, "<<<", v.get("content")
    else:
        parser.print_help()
    
