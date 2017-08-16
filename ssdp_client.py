#!/usr/bin/python3
# -*- coding: utf-8 -*-

import socket
#import time
import select
import netifaces
import getopt
import sys
from ssdp_connect import Connection

#SSDP_ADDR = '239.255.255.250'
#SSDP_PORT = 1900
LISTEN_PORT = 50000

class SSDPClient():
    def __resp_message(self):
        return 'M-SEARCH * HTTP/1.1\r\nHOST: %s:%d\r\nMAN: "ssdp:discover"\r\nMX: 2\r\nST: ssdp:all\r\n\r\n' \
                % (self.__addr, self.__port)

    def __localipfor(self, iface):
        return netifaces.ifaddresses(iface)[netifaces.AF_INET][0]['addr']

    def __init__(self, params):
        self.__s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # INFO: 若绑定，服务端收到的是固定的地址和端口号
        self.__s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        local_ip = self.__localipfor(params[3])
        self.__addr = params[0]
        self.__port = params[1]
        self.__name = params[2]
        self.__s.bind((local_ip, 50000))

        print("Bind '%s' on %s:%d with %s:%s" % (self.__name, self.__addr, self.__port, local_ip, LISTEN_PORT))

    def start(self):
        self.__send_search()
        while True:
            reads, _, _ = select.select([self.__s], [], [], 5)
            if reads:
                r_data, r_addr = self.__s.recvfrom(2048)
                conn = Connection(self.__s, r_data, r_addr, self.__addr, self.__port, self.__name)
                conn.handle_request()
                if conn.is_find_service:
                    break
            else:  # timeout
                self.__send_search()
        self.__s.close()

    def __send_search(self):
        print("Sending M-SEARCH...")
        # INFO: 发送到SSDP组播地址上
        self.__s.sendto(self.__resp_message().encode(), (self.__addr, self.__port))

            
def __print_help():
    print("-h print help")
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
    iface = ""
    service_name = ""
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

    if not multicast_addr or not multicast_port or not service_name or not iface:
        __print_help()
    else:
        return (multicast_addr, multicast_port, service_name, iface)

if __name__ == '__main__':
    port = SSDPClient(__parse_argv(sys.argv[1:]))
    port.start()
