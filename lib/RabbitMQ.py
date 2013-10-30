#encoding:utf-8
'''
Created on 2012-4-5

@author: James
'''

import pika
import json

class MessageClient(object):

    def __init__(self,config):
        self.exchange_type = 'direct'
        self.receiving = True  #whether receive message
        self.passing = True #whether pass to next processer

        if config is not None:
            if config.has_key('server'):
                self.rabbitmq_server = config['server']

            if config.has_key('port'):
                self.rabbitmq_port = config['port']
            else:
                self.rabbitmq_port  = 5672

            if config.has_key('vhost'):
                self.rabbitmq_virtual_host = config['vhost']
            else:
                self.rabbitmq_virtual_host = '/'

            if config.has_key('user'):
                self.rabbitmq_auth_user = config['user']

            if config.has_key('password'):
                self.rabbitmq_auth_pwd = config['password']

            if config.has_key('exchange'):
                self.exchange_name = config['exchange']

            if config.has_key('inKey'):
                self.in_routing_key = config['inKey']

            if config.has_key('inQueue'):
                self.in_queue_name = config['inQueue']
            else:
                self.receiving = False

            if config.has_key('outKey'):
                self.out_routing_key = config['outKey']

            if config.has_key('outQueue'):
                self.out_queue_name = config['outQueue']
            else:
                self.passing = False





        self.rabbitmq_credentials = pika.PlainCredentials(self.rabbitmq_auth_user, self.rabbitmq_auth_pwd)
        self.recv_connection = pika.BlockingConnection(pika.ConnectionParameters(credentials=self.rabbitmq_credentials,
            host=self.rabbitmq_server,
            port=self.rabbitmq_port,
            virtual_host=self.rabbitmq_virtual_host,
            channel_max=2,
            frame_max=131072
        )
        )

        #Chanel Configuration
        if self.receiving:
            self.recv_channel = self.recv_connection.channel()
            self.recv_channel.exchange_declare(exchange=self.exchange_name,
                type=self.exchange_type,
                durable=True)
            self.recv_channel.queue_declare(queue=self.in_queue_name,durable=True)
            self.recv_channel.queue_bind(exchange=self.exchange_name,
                queue=self.in_queue_name,
                routing_key=self.in_routing_key)

        if self.passing:
            self.send_channel = self.recv_connection.channel()
            self.send_channel.exchange_declare(exchange=self.exchange_name,
                type=self.exchange_type,
                durable=True)


    def consuming(self,callbackfunc):
       '''
       consuming message useing callback function.
       '''
       self.callbackfunction = callbackfunc
       if not self.receiving:
           return None
       def callback(ch, method, properties, body):
           data = json.loads(body, encoding='utf-8')
           try:
               new_data = self.callbackfunction(data)
           except Exception,e:
               new_data=data
           if self.passing and new_data is not None:
               self.send(new_data)
           ch.basic_ack(delivery_tag = method.delivery_tag)
       self.recv_channel.basic_qos(prefetch_count=20)
       self.recv_channel.basic_consume(callback,
           queue=self.in_queue_name)
       self.recv_channel.start_consuming()

    def send(self,data):
        '''
        send message
        '''
        if not self.passing:
            return None
        message = json.dumps(data,encoding='utf-8')
        self.send_channel.basic_publish(exchange=self.exchange_name,
            routing_key=self.out_routing_key,
            body=message,
            properties=pika.BasicProperties(
                delivery_mode = 2, # make message persistent
            ))

#if __name__ == '__main__':
#    config0 = {
#        'server':'192.168.2.229',
#        'vhost':'/pushData2Lucene',
#        'user':'dcrawler',
#        'password':'123',
#        'exchange':'IndexPusher',
#        'outKey':'inKey',
#        'outQueue':'freshData'
#    }
#    config = {
#        'server':'192.168.2.229',
#        'vhost':'/pushData2Lucene',
#        'user':'dcrawler',
#        'password':'123',
#        'exchange':'IndexPusher',
#        'inKey':'inKey',
#        'inQueue':'freshData',
#        'outKey':'outKey',
#        'outQueue':'idleData'
#    }
#    config2 = {
#        'server':'192.168.2.229',
#        'vhost':'/pushData2Lucene',
#        'user':'dcrawler',
#        'password':'123',
#        'exchange':'IndexPusher',
#        'inKey':'outKey',
#        'inQueue':'idleData',
#    }
#    def callbackf(data):
#        print 'here: %s'%data['s']
#        return data
#    my_processer0 = processer(config0)
#    my_processer0.send({'s':'ok'})
#    my_processer = processer(config)
#    my_processer.consuming(callbackf)
#    print 'finish'
