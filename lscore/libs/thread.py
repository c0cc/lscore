# coding:utf-8
from lscore.out.console import console, Color
import threading
import time


def multi_threading(limit, daemon=True, callback=None):
    '''
    使用该函数修饰其他函数后，调用过程直接多线程

    被装饰过的函数，会有新的属性,active,可以检查当前线程的数量
    :param limit: 线程数量限制
    :param daemon: 随主线程退出而退出
    :param callback: 函数执行结束回调函数
    :return: 没有返回值
    '''

    def center(func):
        func_hash = hash(func)
        if not ('__%s_func_lock__' % func_hash) in globals():
            globals()['__%s_func_lock__' % func_hash] = threading.Lock()
            globals()['__%s_threading_num__' % func_hash] = 0

        def run(*args, **kwargs):
            lock = globals()['__%s_func_lock__' % func_hash]

            def listen_callback(callback=callback):
                try:
                    r = func(*args, **kwargs)
                except:
                    r = None
                lock.acquire()
                globals()['__%s_threading_num__' % func_hash] -= 1
                lock.release()
                if callback:
                    try:
                        callback(r)
                    except:
                        pass

            while True:
                lock.acquire()
                n = globals()['__%s_threading_num__' % func_hash]
                if n <= limit:
                    globals()['__%s_threading_num__' % func_hash] = n + 1
                    lock.release()
                    break
                lock.release()
                time.sleep(0.01)
            t = threading.Thread(target=listen_callback, args=(callback,))
            t.setDaemon(daemon)
            t.start()

        def __sum_active():
            '''
            计算当前装饰器的存活线程
            :return:
            '''
            if not ('__%s_func_lock__' % func_hash) in globals():
                return 0
            # 这个部分好像不需要锁线程，毕竟线程竞争添加减少的位置是有锁的，单独取值估计不需要锁
            func_num = globals()['__%s_threading_num__' % func_hash]
            return func_num

        def __wait(debug=False):
            '''
            等待线程结束
            :param debug: 调试
            :return:无返回值
            '''
            # 如果没有全局的锁，直接认定不存在
            if not ('__%s_func_lock__' % func_hash) in globals():
                return
            if debug:
                up_thread = globals()['__%s_threading_num__' % func_hash]
                console("当前等待函数:%s 线程:%d" % (func.func_name, up_thread), prefix="***")
            # 存活线程大于0就可以认定还在运行
            while globals()['__%s_threading_num__' % func_hash] > 0:
                if debug:
                    if globals()['__%s_threading_num__' % func_hash] != up_thread:
                        up_thread = globals()['__%s_threading_num__' % func_hash]
                        console("当前等待函数:%s 线程:%d" % (func.func_name, up_thread), prefix="***")
                time.sleep(0.01)
            if debug:
                console("当前等待函数:%s 运行完毕" % func.func_name, prefix="***")
            return

        setattr(run, 'active', __sum_active)
        setattr(run, 'wait', __wait)
        setattr(run, 'join', __wait)
        return run

    return center

