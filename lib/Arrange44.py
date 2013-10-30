#encoding:utf-8
import pymongo

import urllib2,urllib,redis,datetime
import json, marshal,time,bson,re, gridfs
import time,datetime
from bson.objectid import ObjectId
    
def car_tag(car_brand,car_series):
    return ""

colors={u"蝴蝶紫":u"紫色",u"珠光黑":u"黑色",u"紫红":u"紫色",u"黑曜珍珠黑":u"黑色",u"紫":u"紫色",
        u"桔":u"橙色",u"黑":u"黑色",u"藏蓝":u"蓝色（兰）",u"德兰黑":u"黑色",u"金色":u"香槟色",
        u"栗色":u"咖啡色",u"暗樱红色":u"红色",u"沙黄色":u"香槟色",u"各种颜色":u"其它",u"北极白":u"白色",
        u"幻红":u"红色",u"奶黄":u"黄色",u"黄":u"黄色",u"纯白":u"白色",u"枣红":u"红色",u"铁灰":u"灰色",
        u"青蓝":u"蓝色（兰）",u"深蓝":u"蓝色（兰）",u"新波多尔红":u"红色",u"臻栗色":u"咖啡色",u"酷银":u"银色",
        u"墨绿":u"绿色",u"橙":u"橙色",u"米黄":u"黄色",u"橘":u"橙色",u"钛灰":u"灰色",u"马赛灰":u"灰色",
        u"水蓝":u"蓝色（兰）",u"五彩":u"其它",u"太空黑":u"黑色",u"雅典银":u"银色",u"咖啡":u"咖啡色",
        u"梅红色":u"红色",u"乳白色":u"白色",u"太子灰":u"灰色",u"冰蓝色":u"蓝色（兰）",u"晶灰色":u"灰色",
        u"金米色":u"香槟色",u"栗":u"咖啡色",u"亮银色":u"银色",u"沙滩金":u"香槟色",u"湖蓝":u"蓝色（兰）",
        u"酱紫":u"紫色",u"珍珠绸缎白":u"白色",u"沙黄":u"黄色",u"草绿":u"绿色",u"宝石蓝":u"蓝色（兰）",
        u"米":u"白色",u"驼色":u"咖啡色",u"橙红色":u"橙色",u"映灰色":u"灰色",u"爱琴海蓝":u"蓝色（兰）",
        u"暗红":u"红色",u"水晶银":u"银色",u"蓝灰":u"灰色",u"蓝黑色":u"蓝色（兰）",u"解放蓝":u"蓝色（兰）",
        u"淡蓝":u"蓝色（兰）",u"香槟色":u"香槟色",u"琥珀金":u"香槟色",u"巴赫蓝":u"蓝色（兰）",u"珠白":u"白色",
        u"深灰色":u"灰色",u"浅香槟":u"香槟色",u"浅蓝":u"蓝色（兰）",u"蔚蓝":u"蓝色（兰）",u"紫蓝":u"紫色",
        u"曜石黑":u"黑色",u"浅绿色":u"绿色",u"经典红":u"红色",u"深红":u"红色",u"朱红":u"红色",u"浅黄色":u"黄色",
        u"黑蓝色":u"蓝色（兰）",u"香槟":u"香槟色",u"银白":u"银色",u"白灰":u"灰色",u"紫罗兰":u"紫色",
        u"墨橘色":u"橙色",u"古铜色":u"咖啡色",u"珍珠白":u"白色",u"巧克力色":u"咖啡色",u"蓝色":u"蓝色（兰）",
        u"棕":u"咖啡色",u"灰":u"灰色",u"灰绿":u"绿色",u"蓝":u"蓝色（兰）",u"香槟金":u"香槟色",u"深绿":u"绿色",
        u"银":u"银色",u"褐":u"咖啡色",u"深海蓝":u"蓝色（兰）",u"银灰色":u"灰色",u"钛银":u"银色",
        u"宝蓝":u"蓝色（兰）",u"军绿":u"绿色",u"桔黄":u"橙色",u"奶白色":u"白色",u"淡绿":u"绿色",u"浅紫":u"紫色",
        u"炫幻蓝":u"蓝色（兰）",u"翠绿":u"绿色",u"浅紫灰":u"灰色",u"拉力蓝":u"蓝色（兰）",u"紫晶檀":u"紫色",
        u"灰色":u"灰色",u"铜":u"咖啡色",u"红":u"红色",u"土黄色":u"黄色",u"香槟银":u"银色",u"浅金":u"香槟色",
        u"橘黄":u"橙色",u"玫瑰红":u"红色",u"粉":u"其它",u"深紫":u"紫色",u"米色":u"白色",u"法兰红":u"红色",
        u"珠光海洋蓝":u"蓝色（兰）",u"不限":u"其它",u"其他颜色":u"其它",u"卡其色":u"咖啡色",u"浅红":u"红色",
        u"深灰":u"灰色",u"天蓝":u"蓝色（兰）",u"棕色":u"咖啡色",u"黑灰色":u"灰色",u"金属灰":u"灰色",
        u"金属色":u"香槟色",u"深褐":u"咖啡色",u"青灰":u"灰色",u"中黄":u"黄色",u"米白色":u"白色",u"棕红":u"咖啡色",
        u"巧克力":u"咖啡色",u"酒红色":u"红色",u"橘红":u"橙色",u"金黄":u"香槟色",u"淡黄":u"黄色",u"粉红":u"其它",
        u"褐色":u"咖啡色",u"墨色":u"黑色",u"海洋蓝":u"蓝色（兰）",u"冰海蓝":u"蓝色（兰）",u"驼":u"咖啡色",
        u"金":u"香槟色",u"深灰绿":u"绿色",u"玫红色":u"红色",u"绿":u"绿色",u"珍珠银":u"银色",u"卡其":u"咖啡色",
        u"白":u"白色",u"炭灰":u"灰色",u"黄绿色":u"绿色",u"橘红色":u"橙色",u"钛金色":u"香槟色",u"绚彩橙":u"橙色",
        u"浅灰":u"灰色",u"橙红":u"橙色",u"富贵蓝":u"蓝色（兰）",u"沙金色":u"香槟色",u"醇魅红色":u"红色",
        u"恒金色":u"香槟色"}

def car_outer_color(outer_color):
    if outer_color is None or outer_color=="":
        return u"其它"
    for key in colors.keys():
        if outer_color.find(key)>=0:
            return colors[key]
    return u"其它"

inner_colors={u"深":u"深色",u"浅":u"浅色"}
def car_inner_color(inner_color):
    if inner_color is None or inner_color=="":
        return u"不详"
    for key in inner_colors.keys():
        if inner_color.find(key)>=0:
            return inner_colors[key]
    return u"不详"


styles={u"轿车":u"轿车",u"面包":u"面包车",u"货":u"货车/客车",u"客":u"货车/客车",
        u"越野":u"SUV/CUV",u"SUV":u"SUV/CUV",u"CUV":u"SUV/CUV",u"商务":u"MPV",
        u"MPV":u"MPV",u"跑车":u"跑车",u"皮卡":u"皮卡",u"中型":u"中/中大型车",
        u"中大型":u"中/中大型车",u"小轿":u"小型车",u"小型":u"小型车",
        u"微型":u"紧凑/微型车",u"紧凑":u"紧凑/微型车",u"豪华":u"豪华车",u"SV":u"SUV/CUV"}

def car_style(style,type):
    if (style is None or style=="") and (type is None or type==""):
        return u"其它"
#    print style,type
    for key in styles.keys():
        if style.find(key)>=0:
            return styles[key]
        elif type.find(key)>=0:
            return styles[key]
        
    return u"其它"
