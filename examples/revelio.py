#!/usr/bin/env python3

from colorama import Fore, Style
from mbeacon import BeaconFinder


bf = BeaconFinder("raspberrypi")

found = {}

try:
    while True:
        msg = ("raspberrypi",)
        ans = bf.send(msg)

        if ans:
            ip, host = ans

            if host not in found.keys():
                found[host] = ip
                # print(">> Found: {}[{}]".format(host, ip))
        #     else:
        #         print("> nothing new found, {} hosts".format(len(found)))
        # else:
        #     print("* nothing found")

        print("Raspberry Pis", '-'*20)
        for key, val in found.items():
            print("{} [{}]".format(key, val))
        print(' ')

except KeyboardInterrupt:
    print("bye ...")

except Exception as e:
    print("ERROR: {}".format(e))
