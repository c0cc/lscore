# -*- coding:utf-8 -*-
'''
下载类

是不是有时候觉得自己有很多需要下载的东西？
是不是有时候批量下载几万个大大小小的文件不太方便？

暂时还没有发现很多的问题

我觉得还可以试一试，随便用一用
'''

from lscore.utils.cover import size_cover
import threading
import requests
import urllib3
import queue
import time
import uuid
import sys
import os

urllib3.disable_warnings()


class Downloader():
    def __init__(self, limit=10, log=None, err=None):
        '''
        下载器，真正的多线程下载器
        :param limit: 同时下载任务的数量
        '''
        if not log:
            self.__log = sys.stdout
        else:
            self.__log = log
        if not err:
            self.__err = sys.stdout
        else:
            self.__err = err
        self.thread = limit  # 同时运行的下载进程数量
        self.__block = False  # 是否阻塞
        self.buffer = queue.Queue()  # 缓存池，缓存线程
        self.pool = []  # 运行的线程池
        self.listen_thread = threading.Thread(target=self.__listen)  # 监听模式
        self.listen_thread.setDaemon(True)
        self.listen_thread.start()
        self.__debug = True  # 调试模式
        self.__max_retry = 10  # 最大重试次数
        self.__lock_queue = threading.Lock()  # 锁队列添加
        self.__lock_task_chk = threading.Lock()  # 锁检查过程
        self.__lock_out = threading.Lock()  # 输出锁
        self.__lock_add_size = threading.Lock()  # 添加下载尺寸锁
        self.__lock_mkdir = threading.Lock()
        self.__sub_thread = 100  # 子下载文件进程限制
        self.__download_size = 0  # 下载的尺寸
        self.__block_size = 1000000  # 100万字节 ~ 1mb

    def set_block_size(self, size=1000000):
        '''
        设置分块下载字节长度
        :param size:
        :return:
        '''
        self.__block_size = size

    def __add_size(self, count):
        '''
        添加到尺寸统计里面
        :param count:
        :return:
        '''
        if not self.__debug:
            # 优化一下 如果不是调试模式，直接跳出去
            return
        assert isinstance(count, int)
        self.__lock_add_size.acquire()
        self.__download_size += count
        self.__lock_add_size.release()

    def set_debug(self, status=False):
        '''
        设置调试状态
        :param status:
        :return:
        '''
        assert isinstance(status, bool)
        self.__debug = status

    def set_sub_thread(self, num):
        '''
        设置子线程数量限制
        :param num: 设置的子线程限制
        :return:
        '''
        assert isinstance(num, int)
        self.__sub_thread = num

    def log(self, msg):
        '''
        标准化输出日志
        :param msg:
        :return:
        '''
        if not self.__debug:
            return
        self.__lock_out.acquire()
        self.__log.write("%s\r\n" % msg)
        self.__log.flush()
        self.__lock_out.release()

    def err(self, msg):
        '''
        标准化输出错误日志
        :param msg:
        :return:
        '''
        if not self.__debug:
            return
        self.__lock_out.acquire()
        self.__err.write("%s\r\n" % msg)
        self.__err.flush()
        self.__lock_out.release()

    def set_max_retry(self, max_retry=10):
        '''
        设置重试次数
        :param max_retry: 重试次数
        :return: 空
        '''
        assert isinstance(max_retry, int)
        self.__max_retry = max_retry

    def debug_progress(self):
        '''
        打印文件下载进度
        :return:
        '''
        if self.__block:
            self.log("[***] 当前线程: <%s/%s> 已经下载的数据: %s" % (
                len(self.pool),
                self.thread,
                size_cover(self.__download_size)
            ))
        else:
            self.log("[***] 当前线程: <%s/%s> 已经下载的数据: %s 等待线程: %s" % (
                len(self.pool),
                self.thread,
                size_cover(self.__download_size),
                self.buffer.qsize()
            ))

    def __listen(self):
        '''
        该函数主要用于判断存活，获取缓存表中的进程进行添加
        :return:
        '''
        while True:
            for index, thread in enumerate(self.pool):  # 此处注意流程问题，需要先启动线程数占用，然后启用线程，将线程丢入表中
                if not thread.isAlive():
                    self.pool.pop(index)
                    continue
            if self.__block == False and not self.buffer.empty():
                # 如果是通过缓存表进行工作，并且不为空,则获取锁权限,判断表内有空余位置,获取线程下载
                self.__lock_task_chk.acquire()
                if len(self.pool) < self.thread:
                    netaddr, localaddr, args, kwargs = self.get_queue()
                    t = threading.Thread(target=self.__start, args=(netaddr, localaddr) + args, kwargs=kwargs)
                    t.start()
                    self.pool.append(t)
                    self.log("[+++] 队列文件添加:%s" % netaddr)
                    self.__lock_task_chk.release()
                    continue
                self.__lock_task_chk.release()
                time.sleep(0.01)
            else:
                time.sleep(0.01)

    def set_block(self, flag=False):
        '''
        设置添加下载任务阻塞状态
        :param flag: 设置的状态
        :return:
        '''
        self.__block = flag

    def __block_download(self, netaddr, localaddr, tmp_localaddr, start_bit, end_bit, *args, **kwargs):
        '''
        分块下载
        :param netaddr: 网络地址
        :param localaddr: 即将合成的文件名称
        :param tmp_localaddr: 本地存储地址
        :param start_bit: 开始位置
        :param end_bit: 结束位置
        :param args: 下载参数
        :param kwargs: 下载参数
        :return:
        '''
        self.log("[***] 分块下载文件:%s 开始位置:%s 结束位置:%s" % (os.path.basename(localaddr), start_bit, end_bit))
        headers = {"Range": "bytes=%d-%d" % (start_bit, end_bit)}
        kwargs.setdefault("stream", True)
        kwargs.setdefault("headers", {})
        kwargs['headers'].update(headers)
        for x in range(self.__sub_thread):
            try:
                r = requests.get(netaddr, *args, **kwargs)
                with open(tmp_localaddr, "wb") as f:
                    for line in r.iter_content(4096):
                        self.__add_size(len(line))
                        f.write(line)
                assert os.path.getsize(tmp_localaddr) - (end_bit - start_bit) == 1
                self.log("[+++] 分块下载完成:%s %d-%d" % (os.path.basename(localaddr), start_bit, end_bit))
                return True
            except:
                continue
        self.err("[!!!] 分块下载失败:%s %d-%d" % (os.path.basename(localaddr), start_bit, end_bit))
        if os.path.exists(tmp_localaddr):
            os.remove(tmp_localaddr)
        return False

    def __start(self, netaddr, localaddr, *args, **kwargs):
        '''
        直接启动一个下载线程
        :param netaddr: 网络地址
        :param localaddr: 本地地址
        :param args: 下载参数
        :param kwargs: 下载参数
        :return:
        '''
        start_time = int(time.time() * 100) / 100.0
        try:
            netaddr, size, ddxc = self.__get_size(netaddr)
        except:
            self.err("[!!!] 文件下载失败:%s 404" % netaddr)
            return
        self.log("[***] 文件尺寸:%s %s断点续传" % (size_cover(size), ["不支持", "支持"][ddxc]))
        local_dir = os.path.dirname(localaddr)
        self.__lock_mkdir.acquire()
        if not os.path.exists(local_dir):
            self.err("[!!!] 创建目录:%s" % local_dir)
            os.makedirs(local_dir)
            self.__lock_mkdir.release()
        elif os.path.isfile(local_dir):
            self.__lock_mkdir.release()
            self.err("[!!!] 目录位置为文件:%s" % local_dir)
            return False
        else:
            self.__lock_mkdir.release()

        if size > self.__block_size and ddxc:  # 获取到长度了，同时判断一下是不是大于5m，基本是支持多线程下载的
            size -= 1
            sub_thread = []
            starts = 0
            tmp_name = str(uuid.uuid1())
            local_tmp_path = os.path.join(local_dir, tmp_name) + "."
            count = 0
            while True:
                if len(sub_thread) < self.__sub_thread:
                    args_list = [netaddr, localaddr, "%s%s" % (local_tmp_path, count), starts]
                    if size - starts < self.__block_size + 2:  # 小于分块直接丢线程里面跑下载
                        args_list.append(size)
                        args_list.extend(args)
                        t = threading.Thread(target=self.__block_download,
                                             args=tuple(args_list),
                                             kwargs=kwargs)
                        count += 1
                        starts = size
                    else:
                        args_list.append(starts + self.__block_size)
                        args_list.extend(args)
                        t = threading.Thread(target=self.__block_download,
                                             args=tuple(args_list),
                                             kwargs=kwargs)
                        count += 1
                        starts += self.__block_size
                        starts += 1
                    t.start()
                    sub_thread.append(t)
                    if starts == size:
                        break
                else:
                    for index, thread in enumerate(sub_thread):
                        if not thread.isAlive():
                            sub_thread.pop(index)
                            break
                    else:
                        time.sleep(0.01)
            # 等待所有下载线程结束
            while sub_thread:
                for index, thread in enumerate(sub_thread):
                    if not thread.isAlive():
                        sub_thread.pop(index)
                        self.log("[***] 剩余等待线程 <%s:%d>" % (repr(os.path.basename(localaddr)), len(sub_thread)))
                        break
                else:
                    time.sleep(0.1)
            for thread in sub_thread:
                thread.join()
            self.log("[***] 文件下载完成 等待文件检查:%s" % os.path.basename(localaddr))
            # 文件下载检查
            fail = False
            for index in range(count):
                tmp_source_file = "%s%s" % (local_tmp_path, index)
                if not os.path.exists(tmp_source_file):
                    fail = True
            if fail:
                self.err("[!!!] 文件下载失败:%s" % localaddr)
                for index in range(count):
                    tmp_source_file = "%s%s" % (local_tmp_path, index)
                    if os.path.exists(tmp_source_file):
                        os.remove(tmp_source_file)
                return False
            self.log("[***] 文件校验成功:%s" % os.path.basename(localaddr))
            # 拼接文件
            with open(localaddr, "wb") as f:
                for index in range(count):
                    tmp_source_file = "%s%s" % (local_tmp_path, index)
                    r = open(tmp_source_file, "rb")
                    while True:
                        data = r.read(4096)
                        if not len(data) == 4096:
                            f.write(data)
                            break
                        f.write(data)
                    r.close()
                    os.remove(tmp_source_file)
            self.log("[+++] 文件下载完成:%s 时间:%.2f秒" % (netaddr, int(time.time()) - start_time))
        else:
            # 单线程下载
            for _ in range(self.__max_retry):
                try:
                    r = requests.get(netaddr, *args, **kwargs)
                    with open(localaddr, "wb") as f:
                        for line in r.iter_content(4096):
                            self.__add_size(len(line))
                            f.write(line)
                    self.log("[+++] 文件下载完成:%s 时间:%.2f秒" % (netaddr, int(time.time()) - start_time))
                    return True
                except Exception as e:
                    pass
            # 下载失败需要清理垃圾
            if os.path.exists(localaddr):
                os.remove(localaddr)
            self.err("[!!!] 文件下载失败:%s" % netaddr)

    def __get_size(self, addr, max_retry=3, *args, **kwargs):
        '''
        获取要下载的文件的尺寸
        :param addr: 地址
        :param max_retry: 重试次数
        :param args: 下载参数
        :param kwargs: 下载参数
        :return:
        '''
        length = 0
        ddxc = False
        for _ in range(max_retry):
            try:
                r = requests.head(addr, *args, **kwargs)
                if r.headers.get("Location", False) != False:
                    new_addr = r.headers.get("Location", False)
                    self.log("[***] 追踪跳转 %s --> %s" % (repr(addr), repr(new_addr)))
                    return self.__get_size(new_addr, max_retry=3, *args, **kwargs)
                assert 300 > r.status_code >= 200
                length = int(r.headers.get('Content-Length', 0))
                ddxc = r.headers.get("Content-Range", False) != False
                if not ddxc:
                    ddxc = r.headers.get("Accept-Ranges", False) != False

                break
            except AssertionError as e:
                raise
            except Exception as e1:
                pass
        return addr, length, ddxc

    def add_queue(self, task):
        '''
        添加任务到队列里面
        :param task:
        :return:
        '''
        self.__lock_queue.acquire()
        self.buffer.put(task)
        self.__lock_queue.release()

    def get_queue(self):
        '''
        从队列里面获取一个任务执行
        :return: 返回一个任务的对象
        '''
        self.__lock_queue.acquire()
        task = self.buffer.get()
        self.__lock_queue.release()
        return task

    def add_task(self, netaddr, localaddr, *args, **kwargs):
        '''
        添加下载任务
        :param netaddr: 网络地址
        :param localaddr: 本级地址
        :param args: 下载参数
        :param kwargs: 下载参数
        :return:
        '''
        assert isinstance(netaddr, str) and isinstance(localaddr, str), "Param Type Error"
        kwargs.setdefault("verify", False)
        kwargs.setdefault("headers", {})
        kwargs.setdefault("timeout", 5)  # 默认设置个超时，不然等起来很烦
        kwargs['headers'].setdefault(
            "User-Agent",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36"
        )
        args_list = [netaddr, localaddr]
        args_list.extend(args)
        if self.__block:
            while True:
                # 锁 检查线程
                self.__lock_task_chk.acquire()
                if len(self.pool) < self.thread:
                    # 如果有空余线程，就创建任务，添加进去
                    self.log("[+++] 添加线程:%s" % netaddr)
                    t = threading.Thread(target=self.__start, args=tuple(args_list), kwargs=kwargs)
                    t.start()
                    self.pool.append(t)
                    self.__lock_task_chk.release()
                    break
                self.__lock_task_chk.release()
                time.sleep(0.01)


        else:
            self.add_queue((netaddr, localaddr, args, kwargs))

    def wait(self):
        '''
        等待下载结束
        :return:
        '''
        # 等待线程缓冲池为空 线程缓冲池空了以后还要等待当前存活线程
        while True:
            self.__lock_task_chk.acquire()
            expr = self.buffer.empty() and not self.pool
            self.__lock_task_chk.release()
            if expr:
                break
            time.sleep(5)
            self.debug_progress()
        self.log("[***] 文件下载完成 下载数据:%s" % size_cover(self.__download_size))


def download(url, save_path, *args, **kwargs):
    '''
    文件下载
    :param url: 下载地址的url
    :param save_path: 保存的路径
    :param args:
    :param kwargs:
    :return:
    '''
    d = Downloader()
    d.set_debug(False)
    d.set_block(True)
    d.add_task(url, save_path, *args, **kwargs)
    return os.path.exists(save_path) and os.path.isfile(save_path)

