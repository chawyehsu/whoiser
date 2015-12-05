# -*- coding: utf-8 -*-
import Queue
import threading
import time
from config import DATA_FILE, WHOISER_THREAD, SAVER_THREAD
import jobs
import logging

#: 工作队列
domains = Queue.Queue()
#: whois 结果队列（[domain, whois]）
whois_quene = Queue.Queue()
#: 失败队列
fail_quene = Queue.Queue()


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
        logging.debug("Loading domains data...")
        _start = time.time()
        with open(DATA_FILE, "r") as data:
            for line in data:
                domains.put(line.strip('\n'))
        logging.debug("Finish data loading, work queue length: %s. (time cost: %s)" %
                      (domains.qsize(), (time.time() - _start)))

    # 初始化 whoiser 线程池
    def __init_whoiser_thread_pool(self):
        logging.debug("Initializing whoiser thread pool...")
        for i in range(WHOISER_THREAD):
            self.whoisers.append(Whoiser(domains))

    # 初始化 saver 线程池
    def __init_saver_thread_pool(self):
        logging.debug("Initializing saver thread pool...")
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
        self.start()

    def run(self):
        while True:
            domain = self.work_queue.get()
            if domain is not None:
                whois_resp = jobs.get_whois(domain)
                if whois_resp is None:
                    fail_quene.put(domain)
                else:
                    whois_quene.put([domain, whois_resp])
            self.work_queue.task_done()


class Saver(threading.Thread):
    """Whois 保存线程"""
    def __init__(self, work_queue):
        threading.Thread.__init__(self)
        self.work_queue = work_queue
        self.start()

    def run(self):
        while True:
            whois_obj = self.work_queue.get()
            jobs.save_whois(whois_obj[0], whois_obj[1].text)
            self.work_queue.task_done()


def setup_logging():
    logging.basicConfig(level=logging.DEBUG, format='[%(levelname)s %(filename)s:%(lineno)d] %(message)s')

if __name__ == '__main__':
    setup_logging()
    start = time.time()
    work_manager = WorkManager()
    work_manager.wait_all_complete()
    logging.info("Time cost: %s." % (time.time() - start))
