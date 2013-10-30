#coding: utf-8
import json
import socket
import logging
import errno

from thrift import Thrift
from thrift.transport import THttpClient
from thrift.transport import TTransport
from thrift.protocol import TCompactProtocol
from service import TIndexService

from lib.pushIndexHelper import PushIndexHelper

logging.basicConfig(format='[%(levelname)s]: %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
logging.getLogger('paramiko.transport').setLevel(logging.ERROR)
logger.setLevel(logging.DEBUG)

class ServiceClient(object):

    def __init__(self, uri=None):
        if uri:
            self.remoteServerUrl = uri
        else:
            self.remoteServerUrl = "http://admin.365auto.com:8080/thrift/TIndexServiceImpl?51$SID=51SID"

        self.__init_index_client()

    def __init_index_client(self,uri=None):
        self.indexServiceTransport = TTransport.TBufferedTransport(THttpClient.THttpClient(self.remoteServerUrl))
        self.indexServiceProtocol = TCompactProtocol.TCompactProtocol(self.indexServiceTransport)
        self.indexServiceClient = TIndexService.Client(self.indexServiceProtocol)
        self.indexServiceTransport.open()

    def saveDoc(self,objstr,tryit=False):
        '''
        上传索引
        '''
        if not self.indexServiceTransport.isOpen():
            self.indexServiceTransport.open()
        ret = None
        try:
            ret = self.indexServiceClient.saveDoc(objstr)
        except socket.error,e:
            if e.errno == errno.EPIPE and not tryit:
                logger.error('Socket Error:%s, retry...'%e.message)
                if self.indexServiceTransport.isOpen():
                    self.indexServiceTransport.close()
                    self.__init_index_client()
                return self.saveDoc(objstr,True)
            else:
                raise
        except Exception,e:
            logger.error('Error:%s,exit!!!'%e.message)
            import sys
            import traceback
            traceback.print_exc()
            if self.indexServiceTransport.isOpen():
                self.indexServiceTransport.close()
            self.__init_index_client()
            return self.saveDoc(objstr,True)
#            sys.exit()
        return ret

class pusher(object):
    def __init__(self):
        remoteServerUrls = [
            'http://admin.365auto.com:8080/thrift/TIndexServiceImpl?51$SID=51SID',
            'http://192.168.2.233:8080/thrift/TIndexServiceImpl?51$SID=51SID'
        ]
        self.indexServiceClients = [ServiceClient(url) for url in remoteServerUrls]

    def push(self,obj):
        oitem = PushIndexHelper().constructData(obj)
        return [ins.saveDoc(json.dumps(oitem)) for ins in self.indexServiceClients]
