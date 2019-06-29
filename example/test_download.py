# coding:utf-8
'''
测试一下这个下载文件的操作

这是一个毛片下载器
'''
import sys
sys.path.append("../")

from lscore.net.download import Downloader
import requests
import urlparse
import StringIO
import os
import re


def get_m3u8_list(addr):
    r = requests.get(addr)
    io = StringIO.StringIO(r.content)
    while True:
        line = io.readline()
        if not line:
            break
        line = line.strip("\r\n ")
        if not line.startswith("#"):
            yield line
        elif line.startswith("#EXT-X-KEY"):
            r = re.search('URI="([^"]+?)"', line)
            if r:
                yield r.group(1)


down = Downloader(50)
down.set_block_size(10000000000)

bases = "/Users/minisys/Desktop/maopian"
addr = "http://v1.zhiguoer.com:8091/20171206/NMpqyXTy/650kb/hls/index.m3u8"

down.add_task(addr, os.path.join(bases, "index.m3u8"))
for file_name in get_m3u8_list(addr):
    down.add_task(urlparse.urljoin(addr, file_name), os.path.join(bases, file_name.lstrip("/")))
down.wait()


