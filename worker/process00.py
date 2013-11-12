#coding:utf-8
"""
清除Field数量不足69个的数据
"""
from base import ProcesserBase

class processer(ProcesserBase):
    """数据清洗初步准备"""
    seq = "p00"
    
    def process(self,data):
        self.logger.info("(%s) Item start processing." % data['domain'])
        
        keys = ["car_title","car_brand","car_series","contact_phone","contact_mobile","car_price",
                "source_province","source_zone","car_mileage","car_emission","car_transmission","car_type",
                "car_seats","car_cylinder","car_doors","car_drive_type","car_outer_color","car_inner_color",
                "car_birth","purchase_date","car_reg_time","car_enter_time","car_images","car_img_thumb",
                "car_keywords","car_description","source_birth","contact","car_broker","car_age",
                "car_insur_validity","car_inspection_date","car_style","car_engine","car_frame",
                "car_fuel_type","car_fule_mode","car_steering","car_origin","car_repaired","car_usage",
                "car_modified","car_appearance","car_interior","car_chassis","car_condition",
                "purchase_price_refer","source_validity","contact_mail","contact_qq","contact_addr",
                "car_insurance","car_driv_license","car_invoice","car_surcharge","car_tax_valid",
                "car_license","car_license_type","car_license_at"]

        full_item = dict.fromkeys(keys, "")
        full_item.update(data)

        return full_item
        
