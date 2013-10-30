#coding: utf-8
import re
import json

class Model(dict):
    _category = "default"
    
    def __init__(self, rd, id):
        self._rd = rd
        self._id = id
        self._key = ":".join((self._category, id))
        
        _data = self._rd.hgetall(self._key)
        _d = _data.copy()
        for _k, _v in _data.items():
            try:
                _value = json.loads(_v)
            except:
                continue
            if type(json.loads(_v)) in (list, dict):
                _d[_k] = json.loads(_v)
        dict.__init__(self, **_d)
        
    def __setitem__(self, name, value):
        v = value
        if type(value) in (list, dict):
            value = json.dumps(value)
        self._rd.hset(self._key, name, value)
        dict.__setitem__(self, name, v)

    def __getitem__(self, name):
        dvalue = dict.__getitem__(self, name)
        rvalue = self._rd.hget(self._key, name)
        if type(dvalue) in (list, dict):
            if json.dumps(dvalue) != rvalue:
                self[name] = json.loads(rvalue)
            return dict.__getitem__(self, name)
        else:
            return rvalue
        
    def __iter__(self):
        return iter(self._rd.hkeys(self._key))
    
    def __delitem__(self, key):
        self._rd.hdel(self._key, key)
        dict.__delitem__(self, key)

    def update(self, ext, **kwargs):
        if ext:
            for k, v in ext.items():
                self[k] = v
        if kwargs:
            for k, v in kwargs.items():
                self[k] = v
                
    def incr(self, key, interval=1):
        self[key] = self._rd.incr(key, interval)
        return self[key]

class Queue(object):
    def __init__(self, rd, key, method="FIFO"):
        self.key = key
        self._rd = rd
        self.method = method

    def q_pop(self):
        req = None
        if self.method == 'LIFO':
            req = self._rd.rpop(self.key)
        elif self.method == 'FIFO':
            req = self._rd.lpop(self.key)

        # 过滤废弃URL
        if not req:
            return
        request = json.loads(req)
        regexs = self._rd.zrange('regex-trush', 0, -1)

        available = True
        for r in regexs:
            if re.match(r, request['url']):
                available = False
                break
        if available and not self._rd.zscore('url-trush', request['url']):
            return req

    def q_mpop(self, num):
        for _ in xrange(num):
            req = self.q_pop()
            if req:
                yield req
            else:
                continue

    def q_push(self, item):
        self._rd.rpush(self.key, item)

    def q_len(self):
        return int(self._rd.llen(self.key))

    def q_range(self, start=0, end=-1):
        return self._rd.lrange(self.key, start, end)

    def q_flush(self):
        self._rd.delete(self.key)

class Flow(Model, Queue):
    _category = 'flow'
    def __init__(self, rd, id):
        Model.__init__(self, rd, id)
        flow_key = 'q_%s' % self._key
        Queue.__init__(self, rd, flow_key, method=self.get('method', 'FIFO'))

    def reschedule(self):
        del self['start_time']
        self['state'] = 'stopped'
        self.q_flush()
    
    def reset(self):
        self._rd.delete(self._key)
        self.q_flush()

class Spider(Model, Queue):
    _category = 'spider'
    def __init__(self, rd, id):
        Model.__init__(self, rd, id)
        spider_key = 'q_%s' % self._key
        Queue.__init__(self, rd, spider_key, method=self.get('method', 'FIFO'))

    def reset(self):
        self._rd.delete(self._key)
        self.q_flush()
    
class Crawler(Model):
    _category = 'crawler'

    def reset(self):
        self._rd.delete(self._key)
