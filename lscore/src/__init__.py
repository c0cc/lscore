# coding:utf-8
'''
数据来源包

这个包里面的是一些常用的数据来源,这些来源可能是文本，可能是文件，可能是网卡，可能是数据包

数据源尽量实现`readline_iter`方法,每个数据源都可以使用该方法去读取自己需要的东西

'''
