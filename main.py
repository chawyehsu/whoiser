# -*- coding: utf-8 -*-
import Queue
import threading
import time
from config import DATA_FILE, WHOISER_THREAD, SAVER_THREAD, DB_CONN, LOG_LEVEL
import jobs
import coloredlogs
import logging

#: 工作队列
domains = Queue.Queue()
#: whois 结果队列（[domain, whois]）
whois_quene = Queue.Queue()
#: 失败队列
fail_quene = Queue.Queue()

EXIT_FLAG = threading.Event()


class WorkManager(object):
    def __init__(self):
        self.__init_work_queue()
        #: Whoisers 线程池
        self.whoisers = []
        self.__init_whoiser_thread_pool()
        #: Savers 线程池
        self.savers = []
        self.__init_saver_thread_pool()

    # 初始化工作队列
    @staticmethod
    def __init_work_queue():
        logging.info("Loading domains data...")
        _start = time.time()
        with open(DATA_FILE, "r") as data:
            for line in data:
                domains.put(line.strip('\n'))
        logging.info("Finish data loading, work queue length: %s. (time cost: %s)" %
                      (domains.qsize(), (time.time() - _start)))

    # 初始化 whoiser 线程池
    def __init_whoiser_thread_pool(self):
        logging.info("Initializing whoiser thread pool...")
        for i in range(WHOISER_THREAD):
            self.whoisers.append(Whoiser(domains))

    # 初始化 saver 线程池
    def __init_saver_thread_pool(self):
        logging.info("Initializing saver thread pool...")
        for i in range(SAVER_THREAD):
            self.savers.append(Saver(whois_quene))

    def wait_all_complete(self):
        for t in self.whoisers:
            if t.isAlive():
                t.join()

        for t in self.savers:
            if t.isAlive():
                t.join()


class Whoiser(threading.Thread):
    """Whois 请求线程"""
    def __init__(self, work_queue):
        threading.Thread.__init__(self)
        self.work_queue = work_queue
        self.setDaemon(True)
        self.start()

    def run(self):
        while not EXIT_FLAG.is_set():
            if not self.isAlive():
                self.setDaemon(True)
                self.start()
            try:
                domain = domains.get()
                whois_resp = jobs.get_whois(domain)
                if whois_resp is None:
                    fail_quene.put(domain)
                    #: 获取失败重新加入查询队列
                    # domains.put(domain)
                else:
                    whois_quene.put([domain, whois_resp])
            except domains.empty():
                continue
            domains.task_done()


class Saver(threading.Thread):
    """Whois 保存线程"""
    def __init__(self, work_queue):
        threading.Thread.__init__(self)
        self.work_queue = work_queue
        self.setDaemon(True)
        self.start()

    def run(self):
        while not EXIT_FLAG.is_set():
            if not self.isAlive():
                self.setDaemon(True)
                self.start()
            try:
                whois_obj = whois_quene.get()
                jobs.save_whois(whois_obj[0], whois_obj[1])
            except whois_quene.empty():
                continue
            whois_quene.task_done()


def setup_logging():
    coloredlogs.DEFAULT_LOG_FORMAT = '[%(levelname)-8s %(filename)s:%(lineno)d] %(message)s'
    coloredlogs.install(level=LOG_LEVEL)
    # logging.basicConfig(level=LOG_LEVEL, format='[%(levelname)s %(filename)s:%(lineno)d] %(message)s')

if __name__ == '__main__':
    EXIT_FLAG.clear()

    setup_logging()
    start = time.time()
    work_manager = WorkManager()
    domains.join()
    EXIT_FLAG.set()

    # work_manager.wait_all_complete()
    DB_CONN.close()
    logging.debug("Finish whois querying, time cost: %ss." % (time.time() - start))
    logging.info("Saving fail querying domains")
    with open('data/fail.txt', 'a') as fail_file:
        while not fail_quene.empty():
            fail_file.write("%s%s" % (fail_quene.get(), '\n'))
