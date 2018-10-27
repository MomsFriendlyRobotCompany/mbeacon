#!/usr/bin/env python3

import threading
import time
from mbeacon import BeaconServer, BeaconFinder
from collections import namedtuple


# Pub_t = namedtuple('Pub_t', 'key topic pid funcname')
# Sub_t = namedtuple('Sub_t', 'key topic pid funcname')
# Perf_t = namedtuple('Perf_t', 'key nummsg msgrate datarate funcname')
# Connect_t = namedtuple('Connect_t', 'topic ip')


class IPC(object):
    def __init__(self, key, kind, topic, pid, funcname):
        self.msg = (key, kind, topic, pid, funcname,)

class PubIPC(IPC):
    def __init__(self, key, topic, pid, funcname):
        IPC.__init__(self, key, 0, topic, pid, funcname,)

class SubIPC(IPC):
    def __init__(self, key, topic, pid, funcname):
        IPC.__init__(self, key, 1, topic, pid, funcname,)

class PerfIPC(object):
    def __init__(self, key, nummsg, msgrate, datarate, funcname):
        self.msg = (key, nummsg, msgrate, datarate, funcname,)

class CoreIPC(object):
    def __init__(self, topic, tcpaddr):
        self.msg = (topic, tcpaddr,)


# class mService(Service):
#     def __init__(self):
#         Service.__init__(self, msg)
#
#     def dumps(self):
#         m = tuple(msg) + (0,)
#         return m
#
#     def loads(self):
#         pass
def callback(d, a):
    pass

def server(e):
    bs = BeaconServer('local')

    # msg = {'a':1,'b':2}
    # bs.register('bob', msg)
    #
    # msg = {'aa':111,'bb':222,'cc':333}
    # bs.register('tom', msg)
    bs.start()

    while e.isSet():
        time.sleep(.1)

def client(e):
    bf = BeaconFinder('local')

    # publisher setup
    msg = PubIPC('local','bob',12345,'fun').msg
    bf.send(msg)
    # msg = PubIPC('local','tom',12345,'fun').msg
    # bf.send(msg)

    while e.isSet():
        print('-'*40)

        msg = SubIPC('local','tom',12345,'fun').msg
        ret = bf.send(msg)
        print('>>', ret)

        msg = SubIPC('local','bob',12345,'fun').msg
        ret = bf.send(msg)
        print('>>', ret)


if __name__ == "__main__":
    e = threading.Event()
    e.set()

    s = threading.Thread(target=server, args=(e,))
    s.start()

    c = threading.Thread(target=client, args=(e,))
    c.start()

    time.sleep(6)
    e.clear()

    # try:
    #     while(1):
    #         time.sleep(1)
    # except KeyboardInterrupt:
    #     e.clear()
    #     time.sleep(0.5)
    #
    # s.join()
    # c.join()
