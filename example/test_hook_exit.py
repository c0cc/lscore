# coding:utf-8
'''
测试退出的hook函数，自己找的位置
'''

import sys
sys.path.append("../")
from lscore.libs.hook.exit_cut import waitexit

@waitexit("qwertyuiopoiuytrew")
def exits(info=""):
    print("这个傻屌py文件已经结束执行了")
    print("最后传入的参数是:%s" % info)

print 123
