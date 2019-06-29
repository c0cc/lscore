# coding:utf-8
from __future__ import print_function
import sys
sys.path.append("../")

# colorterminal修改了内置对象中的print的内容，但是这个获取到的print对象是需要导入python3的特性才可以使用的
from lscore.utils.colorterminal import Color


# 测试一下输出语句,支持跨平台使用
print("aa",color=Color.RED)

# 支持的颜色 BLUE,GREEN,BLACK,YELLOW,WHITE   还有一个比较特殊的RAND，是随机上面几个颜色

for x in range(100):
    print("test color",color=Color.RAND)

