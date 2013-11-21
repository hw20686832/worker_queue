#coding:utf-8
import os
import sys
import time
import json
import traceback
import inspect
from pkgutil import iter_modules

import pika

import settings
from lib.log4mongo.logger import logger

class ProcessManager(object):
    def __init__(self):
        self.process_module = 'worker'
        self._processes = {}
        for module in self.walk_modules(self.process_module):
            self._filter_processes(module)
            
    def _filter_processes(self, module):
        for pscls in self.iter_process_classes(module):
            self._processes[pscls.seq] = pscls
            
    def iter_process_classes(self, module):
        for obj in vars(module).itervalues():
            if inspect.isclass(obj) and \
                   issubclass(obj, ProcesserBase) and \
                   obj.__module__ == module.__name__ and \
                   getattr(obj, 'seq', None):
                yield obj

    def walk_modules(self, path, load=False):
        mods = []
        mod = __import__(path, {}, {}, [''])
        mods.append(mod)
        if hasattr(mod, '__path__'):
            for _, subpath, ispkg in iter_modules(mod.__path__):
                fullpath = path + '.' + subpath
                if ispkg:
                    mods += self.walk_modules(fullpath)
                else:
                    submod = __import__(fullpath, {}, {}, [''])
                    mods.append(submod)
        return mods
                
    def create(self, process_seq, **process_kwargs):
        try:
            pscls = self._processes[process_seq]
        except KeyError:
            raise KeyError("Processer not found: %s" % process_seq)
        
        return pscls(**process_kwargs)
    
    def get_list(self):
        seqs = self._processes.keys()
        seqs.sort(key=lambda x: int(x[1:]))
        return seqs

class ProcesserBase(object):
    """processer的基类"""
    seq = None
    
    def __init__(self):
        self.logger = logger(logfilepath='log/%s.%s.log' % (self.seq, os.getpid())).getLogger()

        self.logrd = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=5)
        
        self.rabbitmq_server = settings.RABBITMQ_SERVER
        self.rabbitmq_port = settings.RABBITMQ_PORT
        self.rabbitmq_virtual_host = settings.RABBITMQ_VHOST
        self.rabbitmq_auth_user = settings.RABBITMQ_USER
        self.rabbitmq_auth_pwd = settings.RABBITMQ_PASS
        
        self.rabbitmq_credentials = pika.PlainCredentials(self.rabbitmq_auth_user, self.rabbitmq_auth_pwd)
        self.exchange_name = 'processing_exchange'
        self.in_queue_name = 'processing_queue'
        self.out_queue_name = 'processing_queue'
        self.exchange_type = 'direct'
        # 是否传给下一个
        self.passing = True
        #self.initlog()
        self.recv_connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                credentials=self.rabbitmq_credentials,
                host=self.rabbitmq_server,
                port=self.rabbitmq_port,
                virtual_host=self.rabbitmq_virtual_host,
                channel_max=1,
                frame_max=131072
            )
        )
        self.send_connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                credentials=self.rabbitmq_credentials,
                host=self.rabbitmq_server,
                port=self.rabbitmq_port,
                virtual_host=self.rabbitmq_virtual_host,
                channel_max=1,
                frame_max=131072
            )
        )
        self.recv_channel = self.recv_connection.channel()
        self.send_channel = self.send_connection.channel()
        self.loadSequence()

    def loadSequence(self):
        pm = ProcessManager()
        sequence = pm.get_list()
        self.logger.info('init sequence...')
        current_order = sequence.index(self.seq)
        if current_order == 0:
            self.in_routing_key = 'enroll'
            self.in_queue_name = 'enroll_queue'
            self.logger.info('%s->enroll' % self.seq)
        else:
            self.in_routing_key = self.seq
            self.in_queue_name = self.seq
            
        if current_order < len(sequence)-1:
            self.out_routing_key = sequence[current_order+1]
            self.out_queue_name = sequence[current_order+1]
            self.passing = True
        else:
            self.out_routing_key = 'undefined'
            self.out_queue_name = 'undefined'
            self.passing = False
        
        # Chanel Configuration
        self.recv_channel.exchange_declare(exchange=self.exchange_name,
                                           type=self.exchange_type,
                                           durable=True)        
        self.recv_channel.queue_declare(queue=self.in_queue_name, durable=True)        
        self.recv_channel.queue_bind(exchange=self.exchange_name,
                                     queue=self.in_queue_name,
                                     routing_key=self.in_routing_key)
        self.send_channel.exchange_declare(exchange=self.exchange_name,
                                           type=self.exchange_type,
                                           durable=True)        
        self.logger.info('init sequence successful')

    def work(self):
        """开始运行"""
        self._recevie()
        
    def _recevie(self):
        """接收信息"""
        def callback(ch, method, properties, body):
            new_data = None
            data = json.loads(body, encoding='utf-8')
            log_data = {
                "url": data["url"], "domain": data["domain"],
                "processer": self.seq
            }
            if self.seq == 'p00':
                self.logrd.zadd("log:processing:in", json.dumps(log_data), time.time())
            try:
                new_data = self.process(data)
                if not new_data and not self.seq in ('p990', 'p991'):
                    self.logrd.zadd("log:processing:ignore", json.dumps(log_data), time.time())
            except Exception, e:
                exc_tuple = sys.exc_info()
                d_info = ''.join(traceback.format_tb(exc_tuple[2], 3)[1:])
                log_data["msg"] = e.message
                self.logrd.zadd("log:processing:exception", json.dumps(log_data), time.time())
                self.logger.error("An error occurred while %s processing the data [%s].%s\n%s\n%s" \
                                  % (self.seq, data.get("id", "unknow"), exc_tuple[0], exc_tuple[1], d_info))
            finally:
                pass
                
            if self.passing and new_data:
                self._emit(new_data)
            ch.basic_ack(delivery_tag=method.delivery_tag)
        
        self.recv_channel.basic_qos(prefetch_count=20)
        self.recv_channel.basic_consume(callback, queue=self.in_queue_name)
        self.recv_channel.start_consuming()
    
    def process(self, data):
        """对信息进行处理，data为json格式"""
        raise NotImplementedError("Have no subprocesser to handler this step.")
    
    def _emit(self, data):
        """发送消息"""
        try:
            message = json.dumps(data, encoding='utf-8')
            self.send_channel.basic_publish(
                exchange=self.exchange_name,
                routing_key=self.out_routing_key,
                body=message,
                properties=pika.BasicProperties(delivery_mode=2)
            )
        except Exception,ex:
            exc_tuple = sys.exc_info()
            d_info = ''.join(traceback.format_tb(exc_tuple[2], 3)[1:])
            self.logger.error("An error occurred while %s emit the data [%s].%s\n%s\n%s" \
                              % (self.seq, data.get("id", "unknow"), exc_tuple[0], exc_tuple[1], d_info))
        
