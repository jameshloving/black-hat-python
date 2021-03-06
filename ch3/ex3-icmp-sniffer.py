#!/bin/python

import socket
import os
import struct
from ctypes import *

host = '192.168.1.133'

class IP(Structure):
    _fields_ = [
        ('ihl',         c_ubyte, 4),
        ('version',     c_ubyte, 4),
        ('tos',         c_ubyte),
        ('len',         c_ushort),
        ('id',          c_ushort),
        ('offset',      c_ushort),
        ('ttl',         c_ubyte),
        ('protocol_num',c_ubyte),
        ('sum',         c_ushort),
        # changed because this is a 64-bit system
        # https://stackoverflow.com/questions/29306747/python-sniffing-from-black-hat-python-book
        ('src',         c_uint32),
        ('dst',         c_uint32),
    ]

    def __new__(self, socket_buffer=None):
        return self.from_buffer_copy(socket_buffer)

    def __init__(self, socket_buffer=None):
        self.protocol_map = {1: 'ICMP', 6: 'TCP', 17: 'UDP'}

        self.src_address = socket.inet_ntoa(struct.pack('<L', self.src))
        self.dst_address = socket.inet_ntoa(struct.pack('<L', self.dst))

        try:
            self.protocol = self.protocol_map[self.protocol_num]
        except:
            self.protocol = str(self.protocol_num)



class ICMP(Structure):
    _fields_ = [
        ('type',            c_ubyte),
        ('code',            c_ubyte),
        ('checksum',        c_ushort),
        ('unused',          c_ushort),
        ('next_hop_mtu',    c_ushort),
    ]

    def __new__(self, socket_buffer):
        return self.from_buffer_copy(socket_buffer)

    def __init__(self, socket_buffer):
        pass



# create the raw socket
if os.name == 'nt':
    socket_protocol = socket.IPPROTO_IP
else:
    socket_protocol = socket.IPPROTO_ICMP

sniffer = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket_protocol)

# for pings?
sniffer.bind((host, 0))

# include headers
sniffer.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

# if we're on Windows, enable promiscuous mode
if os.name == 'nt':
    sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)

# read in packets
try:
    while 1:
        raw_buffer = sniffer.recvfrom(65565)[0]
        ip_header = IP(raw_buffer)
        print('Protocol: {} {} -> {}'.format(ip_header.protocol,
                                             ip_header.src_address,
                                             ip_header.dst_address,))

        if ip_header.protocol == 'ICMP':
            offset = ip_header.ihl * 4
            buf = raw_buffer[offset:offset + sizeof(ICMP)]
            icmp_header = ICMP(buf)
            
            print('ICMP -> Type: {} Code: {}'.format(icmp_header.type,
                                                     icmp_header.code))            

except KeyboardInterrupt:
    # turn off promiscuous mode
    if os.name == 'nt':
        sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)
