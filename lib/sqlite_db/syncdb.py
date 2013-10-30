#!/usr/bin/env python
#coding: utf-8
"""
字典数据与本地sqlite同步工具
"""
import os
import json
import urllib
import sqlite3

_LOCATE = os.path.dirname(os.path.realpath(__file__))
_DBFILE = os.path.join(_LOCATE, "dict.db")
_CAR_ALL_URL = "http://admin.365auto.com:8080/provider/dict/car/*"
_CAR_DATA_URL = "http://admin.365auto.com:8080/provider/dict/cardata"
_CAR_ALL_URL_V = "http://admin.365auto.com:8080/provider/dict/version/car"
_CAR_DATA_URL_V = "http://admin.365auto.com:8080/provider/dict/version/cardata"
_CREATE_STMT = """
        create table if not exists car_datas(warranty varchar(500),
                               camshaft_zh varchar(500),
                               acceleration_time varchar(500),
                               transmission_ratio_2nd varchar(500),
                               front_hip_space varchar(500),
                               maximum_speed_4torque varchar(500),
                               voltage varchar(500),
                               engine_position_zh varchar(500),
                               front_tire_model varchar(500),
                               charging_mode_zh varchar(500),
                               drive_form_zh varchar(500),
                               transmission_ratio_3rd varchar(500),
                               fuel_type_zh varchar(500),
                               battery_type varchar(500),
                               warranty_mileage varchar(500),
                               overhaul_limit_1st varchar(500),
                               suburbs_fuel_consumption varchar(500),
                               emission_standards_zh varchar(500),
                               logo_zh varchar(500),
                               family_code varchar(500),
                               vehicle_class varchar(500),
                               reducer_transfer_ratio varchar(500),
                               fuel_injection_zh varchar(500),
                               emission_standards varchar(500),
                               hybrid_torque varchar(500),
                               hybrid_maximum_speed_4power varchar(500),
                               engine_casing_mate varchar(500),
                               front_track varchar(500),
                               urban_fuel_consumption varchar(500),
                               hybrid_starting_speed_4power varchar(500),
                               transmission varchar(500),
                               stalls_position_zh varchar(500),
                               steering_zh varchar(500),
                               font_hang_des_zh varchar(500),
                               front_wheel_brake varchar(500),
                               supplement varchar(500),
                               rim_material varchar(500),
                               starting_speed_4power varchar(500),
                               battery_type_zh varchar(500),
                               seats_num varchar(500),
                               transmission_ratio_5th varchar(500),
                               tare_weight varchar(500),
                               engine_speci varchar(500),
                               rear_head_space varchar(500),
                               displacement varchar(500),
                               fuel_transfer_zh varchar(500),
                               variable_timing_sys_zh varchar(500),
                               stroke_zh varchar(500),
                               starting_speed_4torque varchar(500),
                               bodywork varchar(500),
                               logo_2nd varchar(500),
                               engine_top_mate varchar(500),
                               category varchar(500),
                               door_num varchar(500),
                               stalls_position varchar(500),
                               manufacturer_code varchar(500),
                               valves_num_1cylinder varchar(500),
                               maximum_fording varchar(500),
                               pattern varchar(500),
                               fuel_type varchar(500),
                               rear_leg_space varchar(500),
                               origin_zh varchar(500),
                               maximum_speed varchar(500),
                               bodywork_config varchar(500),
                               original_country varchar(500),
                               overhaul_mileage_1st varchar(500),
                               imports_zh varchar(500),
                               rear_hang_des varchar(500),
                               four_wheel_drive_zh varchar(500),
                               luggage_volume varchar(500),
                               front_leg_space varchar(500),
                               rear_tire_model varchar(500),
                               maintenance_time_interval varchar(500),
                               steering varchar(500),
                               ground_clearance varchar(500),
                               warranty_years varchar(500),
                               font_hang_des varchar(500),
                               wheelbase varchar(500),
                               series_num varchar(500),
                               length varchar(500),
                               sequence_num varchar(500),
                               transmission_ratio_1st varchar(500),
                               fuel_grade varchar(500),
                               bodywork_zh varchar(500),
                               front_overhang varchar(500),
                               drag_coefficient varchar(500),
                               low_transfer_ratio varchar(500),
                               engine_form varchar(500),
                               engine_speci_zh varchar(500),
                               hybrid_drive_form varchar(500),
                               engine_casing_mate_zh varchar(500),
                               current_form_zh varchar(500),
                               front_wheel_brake_zh varchar(500),
                               height varchar(500),
                               fuel_capacity varchar(500),
                               hybrid_max_power varchar(500),
                               rear_hip_space varchar(500),
                               limited_edition varchar(500),
                               front_shoulder_space varchar(500),
                               camshaft varchar(500),
                               vehicle_code varchar(500) primary key,
                               fuel_transfer varchar(500),
                               ramp_breakover_angle varchar(500),
                               unknown2 varchar(500),
                               car_body_zh varchar(500),
                               hybrid_maximum_speed_4torque varchar(500),
                               rear_wheel_brake_zh varchar(500),
                               engine_top_mate_zh varchar(500),
                               rear_track varchar(500),
                               rear_wheel_rim varchar(500),
                               announcement_code varchar(500),
                               engine varchar(500),
                               engine_position varchar(500),
                               manufacturer_name_zh varchar(500),
                               cylinder_diameter varchar(500),
                               stalls_num varchar(500),
                               full_weight varchar(500),
                               rear_hang_des_zh varchar(500),
                               car_body varchar(500),
                               piston_stroke varchar(500),
                               hybrid_drive_form_zh varchar(500),
                               transmission_zh varchar(500),
                               loaded_weight varchar(500),
                               rear_shoulder_space varchar(500),
                               rear_overhang varchar(500),
                               four_wheel_drive varchar(500),
                               series_num_zh varchar(500),
                               fuel_grade_zh varchar(500),
                               transmission_ratio_4th varchar(500),
                               current_form varchar(500),
                               aspiration varchar(500),
                               stroke varchar(500),
                               maximum_torque varchar(500),
                               rim_material_zh varchar(500),
                               engine_num varchar(500),
                               fuel_consumption varchar(500),
                               engine_type_zh varchar(500),
                               imports varchar(500),
                               turning_diameter varchar(500),
                               maximum_gradability varchar(500),
                               id_code varchar(500),
                               origin varchar(500),
                               producted_month varchar(500),
                               average_mileage varchar(500),
                               logo varchar(500),
                               engine_config_zh varchar(500),
                               logo_2nd_zh varchar(500),
                               compression_ratio varchar(500),
                               manufacturer_name varchar(500),
                               front_wheel_rim varchar(500),
                               transmission_ratio_6th varchar(500),
                               new_listing varchar(500),
                               best_mileage varchar(500),
                               indicative_price varchar(500),
                               original_country_zh varchar(500),
                               engine_type varchar(500),
                               engine_model varchar(500),
                               drive_form varchar(500),
                               producted_year varchar(500),
                               engine_form_zh varchar(500),
                               vehicle_class_zh varchar(500),
                               supplement_zh varchar(500),
                               variable_timing_sys varchar(500),
                               approach_angle varchar(500),
                               maintenance_mileage_interval varchar(500),
                               front_head_space varchar(500),
                               engine_config varchar(500),
                               high_transfer_ratio varchar(500),
                               self_weight varchar(500),
                               bodywork_config_zh varchar(500),
                               maximum_power varchar(500),
                               transmission_ratio_rev varchar(500),
                               max_drag_weight varchar(500),
                               pattern_zh varchar(500),
                               warranty_zh varchar(500),
                               aspiration_zh varchar(500),
                               departure_angle varchar(500),
                               fuel_injection varchar(500),
                               cylinders_num varchar(500),
                               nbr_drag_weight varchar(500),
                               charging_mode varchar(500),
                               width varchar(500),
                               rear_wheel_brake varchar(500));
        create table if not exists cars(vid varchar(10) primary key,
                          series varchar(100) COLLATE NOCASE,
                          brand varchar(50));
        create table if not exists brand_synonyms(custom_name varchar(100) primary key,
                                    real_name varchar(100));
        create table if not exists series_synonyms(custom_name varchar(100) primary key,
                                    real_name varchar(100));
        create table if not exists car_brand(name varchar(100) primary key,
                               pinyin varchar(100),
                               py varchar(10),
                               letter varchar(2));
        create table if not exists car_series(name varchar(100) COLLATE NOCASE primary key,
                                pinyin varchar(100),
                                py varchar(10),
                                letter varchar(2));
        create table if not exists car_version(category varchar(20), version_code varchar(20));
    
        create index if not exists index_cars on cars(vid,series,brand);
        create index if not exists index_brand_synonyms on brand_synonyms(custom_name);
        create index if not exists index_series_synonyms on series_synonyms(custom_name);
        create index if not exists index_car_datas on car_datas(vehicle_code);
    """
    
class SqliteConn(object):
    def __init__(self, dbfile):
        self.dbfile = dbfile
        self.db = sqlite3.connect(self.dbfile)
        
    def load_data(self, url):
        try:
            up = urllib.urlopen(url)
            v = json.loads(up.read())
        except:
            v = 0

        return v
    
    def refresh(self):
        """刷新数据
        先获取最新版本信息，与当前版本进行比较，不匹配则进行更新
        """
        self.initdb()
        self.carall_v = self.load_data(_CAR_ALL_URL_V)
        self.cardata_v = self.load_data(_CAR_DATA_URL_V)
                
        rs = dict(self.db.execute("select * from car_version").fetchall())
        if not rs:
            self.db.execute("insert into car_version values('car_all', '0')")
            self.db.execute("insert into car_version values('car_data', '0')")
            self.db.commit()
            self.sync()
        else:
            if rs['car_all'] < self.carall_v:
                self.sync_carall()
            if rs['car_data'] < self.cardata_v:
                self.sync_cardata()

    def sync_carall(self):
        self.truncate('cars', 'brand_synonyms', 'series_synonyms', 'car_brand', 'car_series')
        car_all = self.load_data(_CAR_ALL_URL)
        
        for k, d in car_all["vehicle"].items():
            self.db.execute("insert into cars(vid, series, brand) values(?, ?, ?)",
                            (k, d["series"]["name"], d["brand"]["name"]))
        for i in car_all["brand_synonyms"].items():
            self.db.execute("insert into brand_synonyms(custom_name, real_name) values(?, ?)", i)
        for i in car_all["series_synonyms"].items():
            self.db.execute("insert into series_synonyms(custom_name, real_name) values(?, ?)", i)
                    
        for brand, d in car_all['brand'].items():
            self.db.execute("insert into car_brand(name, pinyin, py, letter) values(?, ?, ?, ?)",
                            (brand, d[0]['pinyin'], d[0]['py'], d[0]['letter']))
            
        for series, d in car_all['series'].items():
            self.db.execute("insert into car_series(name, pinyin, py, letter) values(?, ?, ?, ?)",
                            (series, d[0]['pinyin'], d[0]['py'], d[0]['letter']))

        self.db.execute("update car_version set version_code = ? where category = 'car_all'",
                        (self.carall_v, ))
        self.db.commit()
        del car_all

    def sync_cardata(self):
        self.truncate('car_datas')
        car_data = self.load_data(_CAR_DATA_URL)
        
        columns = set()
        for _, d in car_data.items():
            columns = columns.union(d.keys())
        columns = [c.strip() for c in columns]
            
        insert_sql = "insert into car_datas(%s) values(%s)"
        cols = ", ".join(columns)
        sql = insert_sql % (cols, ", ".join(["?"] * len(columns)))
        for _, d in car_data.items():
            self.db.execute(sql, [d.get(c) for c in columns])

        self.db.execute("update car_version set version_code = ? where category = 'car_data'",
                        (self.cardata_v, ))
        self.db.commit()
        del car_data
            
    def sync(self):
        self.sync_carall()
        self.sync_cardata()
        
    def get_connection(self):
        return self.db

    def initdb(self):
        self.db.executescript(_CREATE_STMT)

    def flush(self):
        sql = """
        drop index if exists index_cars;
        drop table if exists cars;
        drop index if exists index_brand_synonyms;
        drop table if exists brand_synonyms;
        drop index if exists index_series_synonyms;
        drop table if exists series_synonyms;
        drop index if exists index_car_datas;
        drop table if exists car_datas;
        drop table if exists car_brand;
        drop table if exists car_series;"""
        self.db.execute(sql)
        
    def truncate(self, *tables):
        for table in tables:
            self.db.execute("delete from %s" % table)

        self.db.commit()


if __name__ == "__main__":
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("", "--force", dest="force", action="store_true",
                      help="Force to reload dict from webservice and save to sqlite dbfile.")
        
    options, _ = parser.parse_args()
    if options.force:
        os.remove(_DBFILE)


sqlite = SqliteConn(_DBFILE)
sqlite.refresh()
conn = sqlite.get_connection()
