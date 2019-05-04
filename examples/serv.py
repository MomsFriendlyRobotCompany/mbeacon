#!/usr/bin/env python3

from colorama import Fore, Style
from mbeacon import BeaconServer

bs = BeaconServer("raspberrypi")

try:
    bs.listenerThread()
except KeyboardInterrupt:
    print("bye")
