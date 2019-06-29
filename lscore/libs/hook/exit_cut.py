# coding:utf-8
import threading

# 退出调用列表
__exits__ = []
# 原本退出的回调函数
__old_shutdown__ = threading._shutdown


def waitexit(*kw, **kwargs):
    '''
    该注解是给开发者使用的，修饰函数，并且传入参数
    :param kw: 传入参数
    :param kwargs: 传入键值对参数
    :return: 返回被装饰过的函数
    '''
    global __exits__

    def cut(func=None):
        # 一个回调对象，搞不好傻屌开发者可能会需要多个回调函数
        __exits__.append((func, kw, kwargs))
        return func

    return cut


def exit_callback():
    '''
    该函数并不是给开发者用的
    :return:
    '''
    global __exits__
    global __old_shutdown__
    while __exits__:
        func, kw, kwargs = __exits__.pop()
        try:
            func(*kw, **kwargs)
        except:
            pass
    return __old_shutdown__()


# 设置销毁回调
setattr(threading, "_shutdown", exit_callback)

if __name__ == '__main__':
    @waitexit("qwertyuiopoiuytrew")
    def exits(info=""):
        print("这个傻屌py文件已经结束执行了")
        print("最后传入的参数是:%s" % info)

