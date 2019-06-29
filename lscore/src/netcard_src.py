# coding:utf-8
from scapy.all import *
from scapy.sendrecv import *


def readline_iter(iface=None, count=0, lfilter=None, *arg, **karg):
    '''
    数据源为网卡的时候，这样进行数据包的捕获
    :param iface: 数据源的接口
    :param count: 捕获数据包的数量
    :param lfilter: 数据包的过滤器
    :param arg: L2socket的调用参数
    :param karg: L2socket的调用参数
    :return:
    '''
    c = 0
    sniff_sockets = {}  # socket: label dict
    if not sniff_sockets or iface is not None:
        L2socket = conf.L2listen
        if isinstance(iface, list):
            sniff_sockets.update(
                (L2socket(type=ETH_P_ALL, iface=ifname, *arg, **karg), ifname)
                for ifname in iface
            )
        elif isinstance(iface, dict):
            sniff_sockets.update(
                (L2socket(type=ETH_P_ALL, iface=ifname, *arg, **karg), iflabel)
                for ifname, iflabel in six.iteritems(iface)
            )
        else:
            sniff_sockets[L2socket(type=ETH_P_ALL, iface=iface,
                                   *arg, **karg)] = iface
    remain = None
    _main_socket = next(iter(sniff_sockets))
    read_allowed_exceptions = _main_socket.read_allowed_exceptions
    select_func = _main_socket.select
    if not all(select_func == sock.select for sock in sniff_sockets):
        warning("Warning: inconsistent socket types ! The used select function will be the one of the first socket")
    _select = lambda sockets, remain: select_func(sockets, remain)[0]

    try:
        while sniff_sockets:
            for s in _select(sniff_sockets, remain):
                try:
                    p = s.recv()
                except socket.error as ex:
                    log_runtime.warning("Socket %s failed with '%s' and thus will be ignored" % (s, ex))
                    del sniff_sockets[s]
                    continue
                except read_allowed_exceptions:
                    continue
                if p is None:
                    try:
                        if s.promisc:
                            continue
                    except AttributeError:
                        pass
                    del sniff_sockets[s]
                    break
                if lfilter and not lfilter(p):
                    continue
                p.sniffed_on = sniff_sockets[s]
                c += 1
                yield p
                if 0 < count <= c:
                    sniff_sockets = []
                    break
    except KeyboardInterrupt:
        pass

