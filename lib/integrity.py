#coding: utf-8
def get_integrity(item, real_img_count=None):
    integrity = 0.0
    integrity += item.get('car_type_score',0.0) * 0.14 #车型准确度分值
    integrity += ( item.get('contact_phone','').isdigit() or item.get('contact_mobile','').isdigit() ) and 0.05 or 0.0 #联系电话
    integrity += item.get('car_usage') and 0.05 or 0.0 #车辆用途
    integrity += item.get('car_price') and 0.05 or 0.0 #预售价格
    integrity += item.get('car_mileage') and 0.05 or 0.0 #里程
    integrity += item.get('car_outer_color') and 0.05 or 0.0 #车身颜色
    integrity += item.get('car_inner_color') and 0.05 or 0.0 #内饰颜色
    integrity += item.get('car_vin_code') and 0.02 or 0.0 #vin码
    integrity += item.get('car_transfer_times') and 0.03 or 0.0 #过户次数
    integrity += item.get('car_description') and 0.05 or 0.0 #车主自述
    integrity += item.get('car_enter_time') and 0.05 or 0.0 #上牌日期
    integrity += item.get('car_birth') and 0.03 or 0.0 #出厂日期
    integrity += item.get('car_inspection_date') and 0.03 or 0.0 #车辆年审日期
    integrity += item.get('car_insur_validity') and 0.03 or 0.0 #交强险截止日期
    integrity += item.get('car_surcharge') and 0.02 or 0.0 #购置税
    integrity += item.get('car_invoice') and 0.03 or 0.0 #购车/过户发票
    integrity += item.get('car_care') and 0.02 or 0.0 #维护保养记录

    image_weight = 0.0
    if not real_img_count is None:
        image_count = real_img_count
    else:
        image_count = len(item.get('car_images','').split('###'))
    if 1 <= image_count <=3 : image_weight = 0.05   #1-3张
    elif 4 <= image_count <=9 : image_weight = 0.13  #4-9张
    elif 10 <= image_count : image_weight = 0.25    #10-14张
    if not item.get('car_images',''):
        image_weight = 0.0

    integrity += image_weight #图片加权

    return integrity
