#! /usr/bin/python3
#coding=utf-8

import socket

class Connection():
    def __init__(self, socket, data, addr, ssdp_addr, ssdp_port, service_name):
        self.__s = socket
        self.__data = data
        self.__addr = addr
        self.__ssdp_addr = ssdp_addr
        self.__ssdp_port = ssdp_port
        self.__service_name = service_name
        self.is_find_service = False

    def handle_request(self):
        if self.__data.decode().startswith('M-SEARCH * HTTP/1.1\r\n'):
            self.__handle_search()
        elif self.__data.decode().startswith('HTTP/1.1 200 OK\r\n'):
            self.__handle_ok()

    def __handle_search(self):
        props = self.__parse_props(['HOST', 'MAN', 'ST', 'MX'])
        if not props:
            #print("No props")
            return

        if props['HOST'] != '%s:%d' % (self.__ssdp_addr, self.__ssdp_port) or props['MAN'] != '"ssdp:discover"' or props['ST'] != 'ssdp:all':
            #print("Cannot handle props: ", props)
            return

        print('RECV: %s' % str(self.__data))
        print('ADDR: %s' % str(self.__addr))

        response = 'HTTP/1.1 200 OK\r\nST: %s\r\n\r\n' % self.__service_name
        self.__s.sendto(response.encode(), self.__addr)
        print('SEND: %s' % response)

    def __handle_ok(self):
        props = self.__parse_props(['ST'])
        if not props:
            return

        if props['ST'] != self.__service_name:
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
