#coding:utf-8
import os
import time
import json
import traceback

import pika

import settings
from processmgr import ProcessManager
from log4mongo.logger import logger

class ProcesserBase(object):
    """processer的基类"""
    seq = None
    
    def __init__(self):
        self.logger = logger(logfilepath='log/%s.%s.log' % (self.seq, os.getpid())).getLogger()
        
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
        self.initlog()
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
        self.logger.info('[%s] Waiting for message. To exit press CTRL+C' % self.seq)
        def callback(ch, method, properties, body):
            new_data = None
            data = json.loads(body, encoding='utf-8')
            if self.seq == 'process00':
                self.logger.info("[%s] New process item received %s" % (data['domain'], data['url']))
            try:
                new_data = self.process(data)
            except Exception:
                exc_tuple = sys.exc_info()
                d_info = ''.join(traceback.format_tb(exc_tuple[2], 3)[1:])
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
        
