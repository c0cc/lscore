# coding:utf-8
from __future__ import print_function
from lscore.utils.colorterminal import Color
from threading import Lock
import time
import sys
import os

__out_lock = Lock()


def console(*args, **kwargs):
    '''
    控制台标准输出
    :param args: 输出的内容
    :param kwargs: 设置的参数
    :return:
    '''
    # 输出的颜色,默认为黑色
    color = kwargs.get("color", None)
    # 输出的文件是否只是文件名？还是绝对路径
    basename = kwargs.get("basename", True)
    # 默认输出的头标记
    prefix = kwargs.get("prefix", "***")
    # 输出的时间格式
    str_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    # 获取调用层的堆栈信息
    frame = sys._getframe(1)
    # 获取行号和文件名
    line = frame.f_lineno
    filename = frame.f_code.co_filename
    # 取文件名
    if basename:
        filename = os.path.basename(filename)
    o = "[%s] %s - 文件 %s -> 第%s行:" % (prefix, str_time, filename, line)

    __out_lock.acquire()
    try:
        print(o, *args, color=color)
    finally:
        __out_lock.release()

