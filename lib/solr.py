#coding:utf-8
import pysolr

from lib.pushIndexHelper import PushIndexHelper

solr = pysolr.Solr('http://192.168.2.233:1984/solr/', timeout=10)
helper = PushIndexHelper()

def add(item):
    return solr.add(helper.constructData(item))


__all__ = ["add"]