#coding:utf-8
from base import ProcesserBase

class Processer(ProcesserBase):
    seq = "%(seq)s"

    def process(self, data):
        return data