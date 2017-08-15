#! /usr/bin/python3
#coding:utf-8

import socket

SSDP_ADDR = '239.255.255.250'
ANY_ADDR = '0.0.0.0'
SSDP_PORT = 1900
SERVICE_NAME = 'FindMyPI'

class Connection():
    def __init__(self, s, data, addr):
        self.__s = s
        self.__data = data
        self.__addr = addr
        self.is_find_service = False

    def handle_request(self):
        if self.__data.decode().startswith('M-SEARCH * HTTP/1.1\r\n'):
            print("Got M-SEARCH")
            self.__handle_search()
        elif self.__data.decode().startswith('HTTP/1.1 200 OK\r\n'):
            print("Got OK")
            self.__handle_ok()

    def __handle_search(self):
        props = self.__parse_props(['HOST', 'MAN', 'ST', 'MX'])
        if not props:
            #print("No props")
            return

        if props['HOST'] != '%s:%d' % (SSDP_ADDR, SSDP_PORT) or props['MAN'] != '"ssdp:discover"' or props['ST'] != 'ssdp:all':
            #print("Cannot handle props: ", props)
            return

        print('RECV: %s' % str(self.__data))
        print('ADDR: %s' % str(self.__addr))

        response = 'HTTP/1.1 200 OK\r\nST: %s\r\n\r\n' % SERVICE_NAME
        self.__s.sendto(response.encode(), self.__addr)
        print('SEND: %s' % response)

    def __handle_ok(self):
        props = self.__parse_props(['ST'])
        if not props:
            return

        if props['ST'] != SERVICE_NAME:
            return

        print('RECV: %s' % str(self.__data))
        print('ADDR: %s' % str(self.__addr))
        print('Find service!!!!')

        self.is_find_service = True

    def __parse_props(self, target_keys):
        lines = self.__data.splitlines()

        props = {}
        for idx, line in enumerate(lines):
            pair = line.decode().split(":", maxsplit = 1)
            if len(pair) > 0:
                if not pair[0].strip():
                    continue
                props[pair[0].upper()] = pair[1].strip() if len(pair)>1 else ''

        #props_keys = [e.upper() for e in props.keys()]
        if not set(target_keys).issubset(set(props.keys())):
            return None

        return props

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
            conn = Connection(self.__s, data, addr)
            conn.handle_request()
        self.__s.setsockopt(socket.SOL_IP, socket.IP_DROP_MEMBERSHIP, socket.inet_aton(SSDP_ADDR) + socket.inet_aton(ANY_ADDR))
        self.__s.close()

if __name__ == '__main__':
    port = SSDPServer()
    port.start()
