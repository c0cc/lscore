# coding:utf-8
import sys
sys.path.append("../")

from lscore.utils.cover import size_cover

# 有时候获取到一个字节的长度，想转换一下单位，但是很尴尬，确定要转换成什么样不太好搞
print size_cover(1234567876543234)

# 带上中文一起输出
print size_cover(76543456765432456,flag=True)

# 指定一下单位，但是只能是大写字母
print size_cover(324563214563,unit="KB")
print size_cover(5678765432,unit="TB",flag=True)

