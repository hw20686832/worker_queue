#!/usr/bin/env python
#coding: utf-8
from optparse import OptionParser

from base import ProcessManager

def gen_processer(seq):
    pm = ProcessManager()
    if seq in pm.get_list():
        raise Exception(u"指定的处理序列已经存在.")
    default_filename = "worker/process%s.py" % seq[1:]
    with open("process.tpl") as t:
        content = t.read()

    content %= {'seq': seq}
    with open(default_filename, "w") as f:
        f.write(content)

    print "processer已经创建在 %s" % default_filename

def list_sequence():
    pm = ProcessManager()
    print ', '.join(pm.get_list())

if __name__ == '__main__':
    import sys
    usage = "Usage: %prog [run|gen|list] [options] arg"
    parser = OptionParser(usage)
    try:
        cmd = sys.argv[1]
    except IndexError:
        parser.error("incorrect number of arguments")
    parser.add_option("-s", "--seq", dest="seq",
                      help="given a sequence.")
    (options, args) = parser.parse_args(args=sys.argv[1:])
    
    if len(args) < 1 and cmd != "list":
        parser.error("incorrect number of arguments")
    if cmd == "run":
        pm = ProcessManager()
        processer = pm.create(options.seq)
        processer.work()
    elif cmd == "gen":
        gen_processer(options.seq)
    elif cmd == "list":
        list_sequence()
    else:
        parser.error("unknow argument '%s'" % cmd)
        
