#!/usr/bin/env python3

import threading
import time
from mbeacon import BeaconServer, Service, BeaconFinder

def server(e):
    msg = {'a':1,'b':2}
    # s = Service('bob',msg)

    bs = BeaconServer('local')
    bs.push('bob', msg)
    bs.start()

    while e.isSet():
        time.sleep(.1)

def client(e):
    bf = BeaconFinder('local')
    while e.isSet():
        msg = {
            'topic': 'bob',
            'pid': 123456789,
            'func': 'test_func'
        }
        bf.search(msg)


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
