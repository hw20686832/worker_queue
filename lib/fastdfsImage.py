#encoding:utf-8
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from fastdfsTransfer import FastdfsTransfer

import socket
import errno
import json
import logging

logging.basicConfig(format='[%(levelname)s]: %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
logging.getLogger('paramiko.transport').setLevel(logging.ERROR)
logger.setLevel(logging.DEBUG)

class imagedb(object):
    '''
    远端fastdfs的图片操作，通过thrift
    '''
    def __init__(self):
        self.__initFDFS()

    def __initFDFS(self):
        self.fdfsTransport = TTransport.TBufferedTransport(TSocket.TSocket('122.192.66.45', 1988))#122.192.66.45
        self.fdfsClient = FastdfsTransfer.Client(TBinaryProtocol.TBinaryProtocol(self.fdfsTransport))
        self.fdfsAcKey = '52588777'
        self.fdfsTransport.open()
        logger.debug('FSDFS client in thrift inited.')

    def getImageInfo(self,filename,tryit=False):
        '''
        获取文件信息
        filename一般是md5字符串
        返回dict
        '''
        if not self.fdfsTransport.isOpen():
            self.fdfsTransport.open()
        img_info = None
        try:
            img_info = json.loads(self.fdfsClient.getInfo(self.fdfsAcKey,filename))#远程查询，是否抓取完成
        except socket.error,e:
            if e.errno == errno.EPIPE and not tryit:
                logger.error('Socket Error:%s, retry...'%e.message)
                if self.fdfsTransport.isOpen():
                    self.fdfsTransport.close()
                    self.__initFDFS()
                return self.getImageInfo(filename,True)
            else:
                raise
        except Exception,e:
            logger.error('Error:%s'%e.message)
            import sys
            sys.exit()
        return img_info

