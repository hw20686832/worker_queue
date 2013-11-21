#coding:utf-8
import pysolr

from lib.pushIndexHelper import PushIndexHelper

solr = pysolr.Solr('http://localhost:8983/solr/', timeout=10)
helper = PushIndexHelper()

def add(item):
    return solr.add(helper.constructData(item))


__all__ = ["add"]