# coding:utf-8
from scapy.all import PcapReader


def readline_iter(filename):
    '''
    数据源为pcap文件的时候，这样进行数据包的读取
    :param filename: 数据包的文件名
    :return:
    '''
    with PcapReader(filename) as fdesc:
        while True:
            packet = fdesc.read_packet()
            if packet is None:
                break
            yield packet

