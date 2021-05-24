##############################################
# The MIT License (MIT)
# Copyright (c) 2018 Kevin Walchko
# see LICENSE for full details
##############################################
#
# https://pymotw.com/2/socket/multicast.html
#
import socket
import struct
import threading
import time
# import ipaddress  # kjw
from mbeacon.ip import GetIP
from mbeacon.transport import Ascii, Json, Pickle
import os
import platform
from collections import namedtuple

Host = namedtuple('Host', 'ipv4 hostname os arch')


class BeaconBase:
    """
    https://www.tldp.org/HOWTO/Multicast-HOWTO-2.html
    TTL  Scope
    ----------------------------------------------------------------------
       0 Restricted to the same host. Won't be output by any interface.
       1 Restricted to the same subnet. Won't be forwarded by a router.
     <32 Restricted to the same site, organization or department.
     <64 Restricted to the same region.
    <128 Restricted to the same continent.
    <255 Unrestricted in scope. Global.
    """
    mcast_addr = '224.3.29.120'
    mcast_port = 11311
    timeout = 5
    ttl = 1

    def __init__(self, key, ttl=1):
        self.group = (self.mcast_addr, self.mcast_port)
        self.sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM,socket.IPPROTO_UDP)
        self.sock.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_TTL, ttl)
        self.sock.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_LOOP, 1)
        self.key = key

        # print("[Beacon]==================")
        # print(" key: {}".format(self.key))


class BeaconFinder(BeaconBase):
    """
    Find Services using the magic of multicast

    pid = 123456
    proc_name = "my-cool-process"
    key = hostname
    finder = BeaconFinder(key)
    msg = finder.search(msg)
    """
    def __init__(self, key, ttl=1, handler=Ascii):
        BeaconBase.__init__(self, key=key, ttl=ttl)
        self.handler = handler()
        self.hosts = {}

    def send(self, msg):
        """
        Search for services using multicast sends out a request for services
        of the specified name and then waits and gathers responses. This sends
        one mdns ping. As soon as a responce is received, the function returns.
        """
        self.sock.settimeout(self.timeout)
        msg = self.handler.dumps(msg)
        self.sock.sendto(msg, self.group)
        try:
            while True:
                # data = returned message info
                # server = ip:port, which is x.x.x.x:9990
                data, server = self.sock.recvfrom(1024)
                print(">> raw data:", data)
                data = self.handler.loads(data)
                print('>> sock.recvfrom:', data, server)
                if data:
                    ip, host = data[:2]
                    if host not in self.hosts.keys():
                        self.hosts[host] = ip
        except socket.timeout:
            print("*** timeout ***")
            # break
            pass
        # print(">> search done")
        # return servicesFound


class BeaconServer(BeaconBase):
    """A simple multicast listener which responds to
    requests for services it has

    # message to be transmitted via multicast
    msg = {'something': 123, 'other': 'abc'}

    # create a server
    provider = BeaconServer(
        'hostname',
        callback_function [optional],  # ??
        handler              # ??
    )

    provider.start()
    try:
        while True:
            time.sleep(500)
    except KeyboardInterrupt:
        provider.stop()

    """
    def __init__(self, key, handler=Ascii, ttl=1):
        BeaconBase.__init__(self, key=key, ttl=ttl)

        # setup service socket
        # allow multiple connections
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.sock.bind(('0.0.0.0', self.mcast_port))
        except OSError as e:
            print("*** {} ***".format(e))
            raise

        mreq = struct.pack("=4sl", socket.inet_aton(self.mcast_addr), socket.INADDR_ANY)
        self.sock.setsockopt(socket.SOL_IP, socket.IP_ADD_MEMBERSHIP, mreq)

        self.handler = handler()  # serialization method

    def listener(self):
        """Listener thread that runs until self.exit is True"""
        self.sock.setblocking(0)

        p = platform.uname()
        # machine = p.machine
        # self.system = p.system

        ip, hostname = GetIP().get()
        print(f"<<< beacon {hostname} [{ip}] {p.system} {p.machine} >>>")

        while True:
            time.sleep(0.2)
            try:
                data, address = self.sock.recvfrom(1024)
            except Exception:
                continue

            data = self.handler.loads(data)
            # print(">> Address: {}".format(address))
            # print(">> Data: {}".format(data))

            if self.key == data[0]:
                msg  = self.handler.dumps((ip, hostname, p.system, p.machine,))
                self.sock.sendto(msg, address)
                print('.', end='', flush=True)





















                # key = data['key']
                # if key == self.key:
                #     if 'topic' in data.keys():
                #         print('sub req')
                #     msg  = self.handler.dumps(('hello',11,22,33,))
                #     self.sock.sendto(msg, address)






                # if len(data) == 4:
                #     key = data[0]
                #     serviceName = data[1]
                #     if key == self.key:
                #         if serviceName == self.service.serviceName:
                #             self.sock.sendto(msg, address)
                #
                #             # is there a callback to save process pid/name?
                #             if self.callback:
                #                 # is the message coming from the same machine?
                #                 # if so, then save the info
                #                 if ip == address[0]:
                #                     # print(">><< same addresses >><<")
                #                     pid = int(data[2])
                #                     name = data[3]
                #                     self.callback(pid, name)


# -----------------
# try:
#     import simplejson as json
# except ImportError:
#     import json


# def get_host_key():
#     try:
#         key = os.uname().nodename.split('.')[0].lower()
#     except:
#         key = socket.gethostname()

#     return key


# class Ascii(object):
#     """Simple ASCII format to send info"""
#     def dumps(self, data):
#         return "|".join(data).encode('utf-8')
#     def loads(self, msg):
#         return msg.decode('utf-8').split("|")

# class Json(object):
#     """Use json to transport message"""
#     def dumps(self, data):
#         return json.dumps(data).encode('utf-8')
#     def loads(self, msg):
#         return json.loads(msg.decode('utf-8'))

# class Pickle(object):
#     """Use pickle to transport message"""
#     def dumps(self, data):
#         return pickle.dumps(data)
#     def loads(self, msg):
#         return pickle.loads(msg)


# class GetIP(object):
#     ip = None
#     def get(self):
#         s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#         try:
#             # doesn't even have to be reachable
#             s.connect(('10.255.255.255', 1))
#             IP = s.getsockname()[0]
#         except:
#             try:
#                 n = socket.gethostname()
#                 # make sure it has a zeroconfig .local or you end up
#                 # with 127.0.0.1 as your address
#                 if n.find('.local') < 0:
#                     n += '.local'
#                 IP = socket.gethostbyname(n)
#             except:
#                 IP = '127.0.0.1'
#         finally:
#             s.close()

#         self.ip = IP
#         return IP
