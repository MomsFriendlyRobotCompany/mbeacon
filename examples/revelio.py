#!/usr/bin/env python3

from colorama import Fore, Style
from mbeacon import BeaconFinder


bf = BeaconFinder("raspberrypi", ttl=2)

found = {}

try:
    while True:
        msg = ("raspberrypi",)
        ans = bf.send(msg)

        print("Raspberry Pis", '-'*20)
        for key, val in bf.hosts.items():
            print("{} [{}]".format(key, val))
        print(' ')

except KeyboardInterrupt:
    print("bye ...")

except Exception as e:
    print("ERROR: {}".format(e))
