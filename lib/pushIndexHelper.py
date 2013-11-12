#encoding:utf-8
'''
Created on 2012-11-21

@author: James
'''
class PushIndexHelper():
    __TYPE_STRING = 0
    __TYPE_INT    = 1
    __TYPE_LONG   = 2
    __TYPE_FLOAT  = 3

    _DataPattern =  {
        'id'                :   __TYPE_STRING,  #唯一的数据标记
        'created'           :   __TYPE_LONG,    #记录创建时间;数据类型:long
        'updated'           :   __TYPE_LONG,    #更新时间;数据类型:long
        'domain'	        :	__TYPE_STRING,  #域名标识
        'url'               :   __TYPE_STRING,  #信息来源网址
        'car_title'         :   __TYPE_STRING,  #信息标题
        'car_brand'         :   __TYPE_STRING,  #车辆品牌
        'car_series'        :   __TYPE_STRING,  #品牌序列
        'car_style'         :   __TYPE_STRING,  #车辆类型
        'car_type'          :   __TYPE_STRING,  #车型，如2013款 豪华版 2.0T
        'car_publish_logo'  :  __TYPE_STRING,  #年款，2010款
        'standard_title'    :     __TYPE_STRING,   #规整化标题
        'vehicle_code'      :   __TYPE_STRING,  #车型代码，对应redbook
        'car_type_score'    :   __TYPE_FLOAT,     #车型识别准确度
        'car_emission'      :   __TYPE_FLOAT,   #发动机排量;数据类型:float
        'car_transmission'  :   __TYPE_STRING,  #变速箱
        'car_outer_color'   :   __TYPE_STRING,  #车身颜色
        'car_inner_color'   :   __TYPE_STRING,  #内饰颜色
        'car_age'           :   __TYPE_INT,     #车龄/上牌时间(单位年);数据类型:int
        'car_enter_time'    :   __TYPE_LONG,    #首次上牌日期;数据类型:long
        'car_img_thumb'     :   __TYPE_STRING,  #车辆图片（小图）
        'car_images'        :   __TYPE_STRING,  #车辆图片（列表）
        'car_description'   :   __TYPE_STRING,  #详细介绍
        'car_mileage'       :   __TYPE_FLOAT,   #行驶里程;数据类型:float
        'car_price'         :   __TYPE_FLOAT,   #车辆报价;数据类型:float
        'purchase_price_refer': __TYPE_FLOAT,   #新车参考价;数据类型:float
        'source_province'   :   __TYPE_STRING,  #车辆所在地-省份
        'source_zone'       :   __TYPE_STRING,  #车辆所在地-地区
        'source_birth'      :   __TYPE_LONG,    #信息发布日期;数据类型:long
        'contact'           :   __TYPE_STRING,  #联系人
        'car_broker'        :   __TYPE_STRING,  #经销商
        'contact_phone'     :   __TYPE_STRING,  #联系人电话
        'contact_mobile'    :   __TYPE_STRING,  #联系人手机
        'contact_addr'      :   __TYPE_STRING,  #联系人地址
        'car_invoice'       :   __TYPE_STRING,  #购车发票
        'car_surcharge'     :   __TYPE_STRING,  #车辆购置附加税
        'car_tax_valid'     :   __TYPE_LONG,    #车船使用税有效期;数据类型:long
        'car_insur_validity':   __TYPE_LONG,    #保险到期日;数据类型:long
        'car_inspection_date':  __TYPE_LONG,    #车辆年检时间;数据类型:long
        'car_license_at'    :   __TYPE_STRING,  #车牌所在地
        
        'status': __TYPE_STRING,
        'car_vin_code': __TYPE_STRING,
        'car_transfer_times': __TYPE_INT,
        'shorturl': __TYPE_STRING,
        'process': __TYPE_STRING,
        'car_transaction_loc': __TYPE_STRING,
        'car_birth': __TYPE_LONG,
        'car_usage': __TYPE_STRING,
        'integrity': __TYPE_FLOAT,
        'car_care': __TYPE_STRING,
        'crawler': __TYPE_STRING,
        'car_img_server':__TYPE_STRING
        }
    
    def constructData(self,originalData):
        '''
        construct a data
        '''
        newData = {}
        for k in self._DataPattern:
            if self._DataPattern[k]==self.__TYPE_STRING:
                if originalData.has_key(k) and originalData[k] != '':
                    newData[k] = originalData[k]
            elif self._DataPattern[k]==self.__TYPE_LONG:
                if originalData.has_key(k):
                    if originalData[k] is None or originalData[k]=='':
                        newData[k] = 0L
                    else:
                        try:
                            newData[k] = long(originalData[k])
                        except:
                            newData[k] = 0L
            elif self._DataPattern[k]==self.__TYPE_FLOAT:
                if originalData.has_key(k):
                    if originalData[k] is None or originalData[k]=='':
                        newData[k] = 0
                    else:
                        try:
                            newData[k] = float(originalData[k])
                        except:
                            newData[k] = 0
            elif self._DataPattern[k]==self.__TYPE_INT:
                if originalData.has_key(k):
                    if originalData[k] is None or originalData[k]=='':
                        newData[k] = 0
                    else:
                        try:
                            newData[k] = int(originalData[k])
                        except:
                            newData[k] = 0                   
        return newData
               
                    
