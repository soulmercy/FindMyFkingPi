#! /usr/bin/python3
#coding:utf-8

import socket
from ssdp_connect import Connection

SSDP_ADDR = '239.255.255.250'
ANY_ADDR = '0.0.0.0'
SSDP_PORT = 1900
SERVICE_NAME = 'FindMyPI'

class SSDPServer():
    def __init__(self):
        self.__s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        print(socket.getfqdn())
        local_ip = socket.gethostbyname(socket.gethostname())
        #local_ip = '10.0.2.4'
        any_ip = '0.0.0.0'
        print("lip:%s, aip: %s" % (local_ip, any_ip))

        # 绑定到任意地址和SSDP组播端口上
        self.__s.bind((any_ip, SSDP_PORT))

        # INFO: 使用默认值
        # self.__s.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_TTL, 20)
        # self.__s.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_LOOP, 1)
        # self.__s.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_IF,
        #                     socket.inet_aton(intf) + socket.inet_aton('0.0.0.0'))
        # INFO: 添加到多播组
        #print (socket.inet_ntoa(socket.inet_aton(SSDP_ADDR) + socket.inet_aton(local_ip)))
        self.__s.setsockopt(socket.SOL_IP, socket.IP_ADD_MEMBERSHIP, socket.inet_aton(SSDP_ADDR) + socket.inet_aton(ANY_ADDR))
        self.local_ip = local_ip

    def start(self):
        while True:
            data, addr = self.__s.recvfrom(2048)
            conn = Connection(self.__s, data, addr, SSDP_ADDR, SSDP_PORT, SERVICE_NAME)
            conn.handle_request()
        self.__s.setsockopt(socket.SOL_IP, socket.IP_DROP_MEMBERSHIP, socket.inet_aton(SSDP_ADDR) + socket.inet_aton(ANY_ADDR))
        self.__s.close()

if __name__ == '__main__':
    port = SSDPServer()
    port.start()
