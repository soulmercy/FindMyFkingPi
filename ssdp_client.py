#!/usr/bin/python3
# -*- coding: utf-8 -*-

import socket
import time
import select
import netifaces
from ssdp_connect import Connection

SSDP_ADDR = '239.255.255.250'
SSDP_PORT = 1900

MS = 'M-SEARCH * HTTP/1.1\r\nHOST: %s:%d\r\nMAN: "ssdp:discover"\r\nMX: 2\r\nST: ssdp:all\r\n\r\n' \
     % (SSDP_ADDR, SSDP_PORT)


class SSDPClient():
    def __init__(self):
        self.__s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # INFO: 若绑定，服务端收到的是固定的地址和端口号
        self.__s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        local_ip = ""
        if netifaces.gateways()['default']:
            default_if = netifaces.gateways()['default'][netifaces.AF_INET][0]
            if_list = [netifaces.ifaddresses(ifaces) for ifaces in netifaces.interfaces() if ifaces == default_if]
            if len(if_list):
                local_ip = if_list[0]
        if not local_ip:                
            local_ip = socket.gethostbyname(socket.gethostname())
        print("bind %s:50000" % local_ip)    
        self.__s.bind((local_ip, 50000))

    def start(self):
        self.__send_search()
        while True:
            reads, _, _ = select.select([self.__s], [], [], 5)
            if reads:
                data, addr = self.__s.recvfrom(2048)
                conn = Connection(self.__s, data, addr, SSDP_ADDR, SSDP_PORT, "FindMyPI")
                conn.handle_request()
                if conn.is_find_service:
                    break
            else:  # timeout
                self.__send_search()
        self.__s.close()

    def __send_search(self):
        print("Sending M-SEARCH...")
        # INFO: 发送到SSDP组播地址上
        self.__s.sendto(MS.encode(), (SSDP_ADDR, SSDP_PORT))

if __name__ == '__main__':
    port = SSDPClient()
    port.start()
