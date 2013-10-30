from pymongo import Connection
from pymongo.errors import AutoReconnect
import logging
import time,datetime
import socket
import pika,json,bson,pymongo

rabbitmq_server='192.168.2.229'
rabbitmq_port  = 5672
rabbitmq_virtual_host = '/dcrawler-del'
exchange_name = 'dropping_exchange'
queue_name = 'droping_queue'
exchange_type = 'direct'
out_routing_key = 'droping'

class MongoEncoder(json.JSONEncoder):
    def default(self, obj):
        # convert all iterables to lists
        if hasattr(obj, '__iter__'):
            return list(obj)
        # convert cursors to lists
        elif isinstance(obj, pymongo.cursor.Cursor):
            return list(obj)
        # convert ObjectId to string
        elif isinstance(obj, bson.objectid.ObjectId):
            return unicode(obj)
        # dereference DBRef
#        elif isinstance(obj, pymongo.dbref.DBRef):
#            return db.dereference(obj)
        # convert dates to strings
        elif isinstance(obj, datetime.datetime) or isinstance(obj, datetime.date) or isinstance(obj, datetime.time):
            return unicode(obj)
        return json.JSONEncoder.default(self, obj)
    
class Droping_rabbitmq():
    def __init__(self):
        rabbitmq_credentials = pika.PlainCredentials('dcrawler', '123')
        connection = pika.BlockingConnection(pika.ConnectionParameters(credentials=rabbitmq_credentials,
        host=rabbitmq_server,port=rabbitmq_port,virtual_host=rabbitmq_virtual_host,channel_max=1,frame_max=131072)                                )
        self.channel = connection.channel()
        self.channel.exchange_declare(exchange=exchange_name,type=exchange_type,durable=True)

    def insert_data(self,data):
        message = json.dumps(data,encoding='utf-8',cls=MongoEncoder)
        self.channel.basic_publish(exchange=exchange_name,
                              routing_key=out_routing_key,
                              body=message,
                              properties=pika.BasicProperties(delivery_mode = 2,))
dr=Droping_rabbitmq()


