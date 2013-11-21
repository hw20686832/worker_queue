#coding: utf-8
from optparse import OptionParser

import pymongo

from mq import MessageClient
import settings

mq_config = {attr: settings.__getattribute__(attr) for attr in dir(settings)
             if attr.startswith("RABBITMQ") and attr.startswith("MQ")}

def test(infoid):
    mq_client = MessageClient(mq_config)
    mongo = pymongo.Connection('192.168.2.228', 2281)
    db = mongo.dcrawler

    datas = db.car_info.find({"id": infoid})
    for data in datas:
        mq_client.send(data)
        print "Data %s emit." % data["id"]


if __name__ == "__main__":
    parser = OptionParser(usage)
    parser.add_option("-i", "--id", dest="infoid",
                      help="given a info id.")
    (options, args) = parser.parse_args()
    test(options.infoid)