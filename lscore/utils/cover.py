# coding:utf-8
'''
单位转换计算类

当前该类主要用于转换计算机单位
'''


def size_cover(length, unit="B", flag=False):
    '''
    文件尺寸转换函数
    :param length: 输入要计算的数字(文件长度)
    :param unit: 输入单位，默认是字节，可以自己设定大写的B,GB,KB之类的单位
    :param flag: 返回输出的标记，标记为True的时候会在后面加入中文单位 例如:1.11KB (千字节)
    :return: 返回计算的长度
    '''
    unit_table = ["CB", "DB", "NB", "BB", "YB", "ZB", "EB", "PB", "TB", "GB", "MB", "KB", "B"]
    unit_table_chinese = ["", "刀字节", "诺字节", "珀字节", "尧字节", "泽字节", "艾字节", "拍字节", "太字节", "吉字节", "兆字节", "千字节", "字节"]
    if length > 2000:
        i = unit_table.index(unit)
        if i <= 0:
            if flag:
                return "%.2f %s(%s)" % (length, unit, unit_table_chinese[unit_table.index(unit)])
            else:
                return "%.2f %s" % (length, unit)
        unit = unit_table[i - 1]
        length /= 1024.0
        return size_cover(length, unit, flag)
    if flag:
        return "%.2f %s(%s)" % (length, unit, unit_table_chinese[unit_table.index(unit)])
    else:
        return "%.2f %s" % (length, unit)


def date_mon_cover(mon=""):
    '''
    月份的转换
    :param mon: 很神奇的英文月份转换
    :return:
    '''
    mons = ["jan", "feb", "march", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]
    r = mons.index(mon.lower())
    assert r >= 0
    return r + 1

