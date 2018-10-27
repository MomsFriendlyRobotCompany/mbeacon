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


class BeaconBase(object):
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
    mcast_addr = '224.3.29.110'
    mcast_port = 11311
    timeout = 2
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
    def __init__(self, key, ttl=1, handler=Pickle):
        BeaconBase.__init__(self, key=key, ttl=ttl)
        self.handler = handler()

    def send(self, msg):
        """
        Search for services using multicast sends out a request for services
        of the specified name and then waits and gathers responses. This sends
        one mdns ping. As soon as a responce is received, the function returns.
        """
        # serviceName = 'GeckoCore'
        self.sock.settimeout(self.timeout)
        # msg = self.handler.dumps((self.key, serviceName, str(pid), processname,))
        # msg['key'] = self.key
        msg = self.handler.dumps(msg)
        self.sock.sendto(msg, self.group)
        servicesFound = None
        while True:
            try:
                # data = returned message info
                # server = ip:port, which is x.x.x.x:9990
                data, server = self.sock.recvfrom(1024)
                data = self.handler.loads(data)
                # print('>> Search:', data, server)
                servicesFound = data
                break
                # if len(data) == 2:
                #     servicesFound = (zmqTCP(server[0], data[0]), zmqTCP(server[0], data[1]),)
                #     break
            except socket.timeout:
                print("*** timeout ***")
                break
        # print(">> search done")
        return servicesFound


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
    def __init__(self, key, callback=None, handler=Pickle, ttl=1):
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

        # setup server data
        self.services = {}  # services
        self.callback = callback
        self.handler = handler()  # serialization method

        # setup thread
        self.exit = False
        self.listener = threading.Thread(target=self.listenerThread)

    def register(self, name, msg):
        """Register a service"""
        self.services[name] = msg

    def unregister(self, name):
        """Unregister a service"""
        if name in self.services.keys():
            self.services.pop(name)

    def start(self):
        """Start the listener thread"""
        self.listener.setDaemon(True)
        self.listener.start()

    def stop(self):
        """Stop the listener thread"""
        self.exit = True

    def listen(self):
        """TBD"""
        pass

    def listenerThread(self):
        """Listener thread that runs until self.exit is True"""
        self.sock.setblocking(0)

        ip = GetIP().get()
        print("<<< beacon ip: {} >>>".format(ip))

        while True:
            if self.exit is True:
                break
            else:
                time.sleep(0.2)
                try:
                    data, address = self.sock.recvfrom(1024)
                except Exception:
                    continue

                data = self.handler.loads(data)
                print(">> Address: {}".format(address))
                print(">> Data: {}".format(data))

                if self.key == data[0]:
                    if self.callback:
                        self.callback(data, address)
                    else:
                        msg  = self.handler.dumps(('hello',))
                        self.sock.sendto(msg, address)





















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
