# coding:utf-8
'''
测试输出到xls文件
'''
import sys
sys.path.append("../")
from lscore.out.xls import outer
arrays = [
    ["test1", "test2"],
    ["test3", "test4"]
]

outer(arrays,"/Users/minisys/Desktop/12345678.xls")


