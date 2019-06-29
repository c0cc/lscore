# coding:utf-8

'''
测试数据源为网卡的时候，数据源的操作
'''
import sys
sys.path.append("../")
from scapy.all import *
from lscore.src.netcard_src import readline_iter
from lscore.out.console import console,Color

for packet in readline_iter("en0",filter="tcp and ip"):
    ip_layer = packet.getlayer(IP)
    console("%s->%s" % (ip_layer.src, ip_layer.dst),color=Color.BLUE)
