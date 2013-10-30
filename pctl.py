#!/usr/bin/env python
#coding: utf-8
import subprocess
import json
import imp
import os
import sys
import signal

from processmgr import ProcessManager

class ProcessController(object):

    def __init__(self):
        self.processers = {}
        self.useage = {'help': self.help, 'start': self.start,
                       'status': self.status, 'stop': self.stop, 'exit': self.exit}
    
    def help(self, *args):
        """help - show this useage."""
        for _, v in self.useage.items():
            print v.__doc__
            
    def start(self, *args):
        """start [X|all] - Run the specified seq number process, X is [00, 11, 12...]."""
        if args[0] == 'all':
            params = args[1:]
            for x in self.processers.keys():
                cmd = ['python', 'processmgr.py']
                cmd.append(x.replace('process', ''))
                cmd.extend(params)
                p = subprocess.Popen(cmd,
                                     stdin=subprocess.PIPE,
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE,
                                     shell=False)
                self.processers[x] = p
                print 'run %s' % x
        else:
            cmd = ['python', 'processmgr.py']
            cmd.extend(args)
            p = subprocess.Popen(cmd,
                                 stdin=subprocess.PIPE,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 shell=False)
            
            self.processers['process%s' % args[0]] = p
            print 'run process%s.' % args[0]

    def stop(self, *args):
        """stop [X|all] - Stop the specified seq number process, X is [00, 11, 12...]."""
        if args[0] == 'all':
            for k, v in self.processers.items():
                if v:
                    try:
                        v.terminate()
                    except:
                        pass
                    print 'Killed %s.' % k

            self.processers = dict.fromkeys(self.processers.keys())
        else:
            seq = args[0]
            try:
                self.processers['process%s' % seq].terminate()
                self.processers['process%s' % seq] = None
                print 'Killed process%s.' % seq
            except:
                print 'Have no process%s.' % seq

    def status(self, *args):
        """status [seq] - Show all or specified processers status."""
        for k, v in self.processers.items():
            if v:
                if v.poll() is None:
                    status = 'running'
                else:
                    status = 'dead'
            else:
                status = 'stoped'
            print '%s - %s' % (k, status)
            
    def exit(self, *args):
        """exit - stop all processers and quit."""
        self.stop('all')
        sys.exit(1)
    

if __name__ == '__main__':
    def term(signal, frame):
        sys.exit(1)

    signal.signal(signal.SIGINT, term)
    pc = ProcessController()
    print "[system] input command, eg: help."
    while True:
        input = raw_input('>>> ')
        if input:
            cmds = input.split()
            try:
                pc.useage[cmds[0]](*cmds[1:])
            except SystemExit:
                break
            except KeyError:
                print "Unknow command: %s" % cmds[0]
            except:
                import traceback
                traceback.print_exc()
    print 'bye.'
