#! /usr/bin/python3
#coding:utf-8

import socket
import netifaces
import sys
import getopt
from ssdp_connect import Connection

class SSDPServer():
    def __init__(self, params):
        self.__addr = params[0]
        self.__port = params[1]
        self.__service_name = params[2]
        self.__local_ip = self.__localipfor(params[3])

        self.__s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # 绑定到任意地址和SSDP组播端口上 
        self.__s.bind(("0.0.0.0", self.__port))

        print("Bind '%s' on %s:%d with %s" % (self.__service_name, self.__addr, self.__port, self.__local_ip))

        # INFO: 添加到多播组
        self.__s.setsockopt(socket.SOL_IP, socket.IP_ADD_MEMBERSHIP, socket.inet_aton(self.__addr) + socket.inet_aton(self.__local_ip))

    def __localipfor(self, iface):
        return netifaces.ifaddresses(iface)[netifaces.AF_INET][0]['addr']

    def start(self):
        while True:
            r_data, r_addr = self.__s.recvfrom(2048)
            conn = Connection(self.__s, r_data, r_addr, self.__addr, self.__port, self.__service_name)
            conn.handle_request()
        self.__s.setsockopt(socket.SOL_IP, socket.IP_DROP_MEMBERSHIP, socket.inet_aton(self.__addr) + socket.inet_aton(self.__local_ip))
        self.__s.close()

def __print_help():
    print("-h print help")
    print("-l                   List all network ifaces")
    print("-a --addr            SSDP multicast addr")
    print("-p --port            SSDP multicast port")
    print("-s --service-name    Service name")
    print("-i --iface           Network ifaces")
    sys.exit(2)

def __print_ifaces():
    print(netifaces.interfaces())
    sys.exit(0)

def __parse_argv(argv):
    # print(argv)
    multicast_addr = ""
    multicast_port = ""
    service_name = ""
    iface = ""

    try:
        opts, args = getopt.getopt(argv, "ha:p:s:i:l", ["addr=", "port=", "service-name=", "iface="])
    except getopt.GetoptError:
        __print_help() 
    for opt, arg in opts:
        if opt == '-h':
            __print_help()
        elif opt == '-l':
            __print_ifaces()
        elif opt in ("-a", "--addr"): 
            multicast_addr = arg
        elif opt in ("-p", "--port"):
            multicast_port = int(arg)
        elif opt in ("-s", "--service-name"):
            service_name = arg
        elif opt in ("-i", "--iface"):
            iface = arg

    if not iface and netifaces.gateways()['default']:
        iface = netifaces.gateways()['default'][netifaces.AF_INET][1]

    if not multicast_addr or not multicast_port or not service_name or not iface:
        __print_help()
    else:
        return (multicast_addr, multicast_port, service_name, iface)

if __name__ == '__main__':
    port = SSDPServer(__parse_argv(sys.argv[1:]))
    port.start()
