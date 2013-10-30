#coding: utf-8
from syncdb import conn

class CarSpecification(object):
    """sqlite操作工具，提供各类查询
    """
    def __init__(self):
        self.db = conn

    def get_brands(self):
        cursor = self.db.cursor()
        cursor.execute("select name from car_brand")
        return [n for n, in cursor.fetchall()]
    
    def get_series(self):
        cursor = self.db.cursor()
        cursor.execute("select name from car_series")
        return [n for n, in cursor.fetchall()]

    def has_brand(self, brand):
        cursor = self.db.cursor()
        cursor.execute("select name from car_brand where name = ?", (brand, ))
        b = cursor.fetchone()
        if b:
            return b[0]

    def has_series(self, series):
        cursor = self.db.cursor()
        cursor.execute("select name from car_series where name = ?", (series, ))
        s = cursor.fetchone()
        if s:
            return s[0]

    def has_type(self, types):
        cursor = self.db.cursor()
        sql = "select d.vehicle_code, s.brand brand, s.series series, d.pattern_zh \
                 from car_datas d left join cars s on d.vehicle_code = s.vid \
               where d.pattern_zh = ?"
        cursor.execute(sql, (types, ))
        s = cursor.fetchone()
        return s

    def has_emission(self, emission):
        cursor = self.db.cursor()
        cursor.execute("select vehicle_code from car_datas where engine = ?", (emission, ))
        s = cursor.fetchone()
        if s:
            return s[0]

    def get_brand_by_series(self, series):
        cursor = self.db.cursor()
        cursor.execute("select brand from cars where series = ?", (series, ))
        brand = cursor.fetchone()
        if brand:
            return brand[0]
        
    def get_series_by_brand(self, brand):
        cursor = self.db.cursor()
        cursor.execute("select series from cars where brand = ?", (brand, ))
        
        return [s for s, in cursor.fetchall()]

    def get_series_by_str(self, brand, strs):
        cursor = self.db.cursor()
        if self.has_brand(src):
            series = self.get_series_by_brand(src)
            s = strs.replace(" ","").lower()
            for serie in series:
                if s.count(serie.replace(" ","").lower()):
                    return serie
                
            cursor.execute("select custom_name, real_name from series_synonyms")
            for serie, rname in cursor.fetchall():
                if s.count(serie.replace(" ","").lower()):
                    return rname
                
        return ""
    
    def get_brand_by_pinyin(self,value):
        '''
        find brand by pinyin , return string list
        '''
        if value:
            try:
                value=value.encode('utf-8')
            except:
                try:
                    value=value.decode('utf-8')
                except:
                    return None
                
        cursor = self.db.cursor()
        cursor.execute("select name from car_brand where pinyin = ?", (value, ))
        
        return [i for i, in cursor.fetchall()]
        
    def get_series_by_pinyin(self,value):
        '''
        find series by pinyin , return sting list
        '''
        if value:
            try:
                value=value.encode('utf-8')
            except:
                try:
                    value=value.decode('utf-8')
                except:
                    return None
                
        cursor = self.db.cursor()
        cursor.execute("select name from car_brand where pinyin = ?", (value, ))
        
        return [i for i, in cursor.fetchall()]
    
    def trans_synonyms_brand(self, brand):
        '''
        use standard word instead of extra word, based synonym dictionary.
        '''
        result = brand
        cursor = self.db.cursor()
        cursor.execute("select real_name from brand_synonyms where custom_name = ?", (brand, ))
        rs = cursor.fetchone()
        if rs:
            result = rs[0]

        return result

    def trans_synonyms_series(self, series):
        result = series
        cursor = self.db.cursor()
        cursor.execute("select real_name from series_synonyms where custom_name = ?", (series, ))
        rs = cursor.fetchone()
        if rs:
            result = rs[0]
            
        return result

    def get_vehicles_by_condition(self, **condition):
        base_sql = "select c.brand brand, c.series series, d.* from cars c left join car_datas d on c.vid = d.vehicle_code "
        f = lambda a: "c.%s = '%s'" % a if a[0] in ('brand', 'series') else "d.%s = '%s'" % a
        cluster = "where %s" % ' and '.join([f(args) for args in condition.items()])
        sql = base_sql + cluster
        cursor = self.db.cursor()
        cursor.execute(sql)
        rs = cursor.fetchall()
        data = [dict(zip([i[0] for i in cursor.description], x)) for x in rs]
        return data

    def get_vehicles_by_brand(self, brand):
        cursor = self.db.cursor()
        cursor.execute("select c.brand brand, c.series series, d.* from cars c inner join car_datas d on c.vid = d.vehicle_code where c.brand = ?", (brand, ))
        rs = cursor.fetchall()
        datas = [dict(zip([i[0] for i in cursor.description], x)) for x in rs]
        return datas

    def get_car_data(self, **kwargs):
        sql = "select s.brand brand, s.series series, d.* from car_datas d left join cars s on d.vehicle_code = s.vid %s"
        f = lambda a: "s.%s = '%s'" % a if a[0] in ('brand', 'series') else "d.%s like '%%%s%%'" % a
        #f = lambda a: "s.%s = '%s'" % a if a[0] in ('brand', 'series') else "d.%s = '%s'" % a
        
        where_cluster = "where %s" % ' and '.join([f(args) for args in kwargs.items()])
        final_sql = sql % where_cluster
        cursor = self.db.cursor()
        cursor.execute(final_sql)
        rs = cursor.fetchall()
        
        data = [dict(zip([i[0] for i in cursor.description], x)) for x in rs]
        return data
    
