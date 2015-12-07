# -*- coding: utf-8 -*-
import json
import logging
import random
import time
from config import WHOIS_DIR, WHOIS_FILENAME, USE_WHOIS_CMD, DB_CONN
import whois
import os

HOST = ['-a', '-A', '-b', '-d', '-g', '-i', '-I', '-l', '-m', '-r', '-6']
COUNT = 0


def get_whois(domain):
    global COUNT
    host = random.choice([USE_WHOIS_CMD, random.choice(HOST)])
    logging.info("Retrieving whois of domain '%s' by using '%s'." % (domain, host))
    if COUNT == 10:
        logging.warn("Whoiser thread is sleeping for 2 seconds.")
        time.sleep(2)
        host = USE_WHOIS_CMD
        COUNT = 0
    w = None
    try:
        w = whois.whois(domain, host)
    except Exception as e:
        logging.error("PyWhois Exception: %s" % e)

    if w is None:
        COUNT += 1
        logging.error("FAIL Retrieve whois of domain '%s' fail." % domain)
        return None
    #: 没有邮箱直接判定为查询失败
    elif w.emails is not None:
        logging.debug("SUCCESS Retrieve whois of domain '%s'." % domain)
        return w
    else:
        COUNT += 1
        logging.error("FAIL Retrieve whois of domain '%s' fail." % domain)
        return None


def save_whois(domain, whois_obj):
    logging.info("Saving whois(domain: '%s') to file..." % domain)
    original_domain_str = domain
    #: 反向拆解域名，构造 whois 文件存放目录
    domain = domain.split('.')
    domain.reverse()
    try:
        path = os.path.join(WHOIS_DIR, *domain)
        if not os.path.exists(path):
            os.makedirs(path)

        # 文件形式保存 whois 原始信息
        absolute_path = os.path.join(path, WHOIS_FILENAME)
        with open(absolute_path, 'w') as whois_file:
            whois_file.write(whois_obj.text)
    except Exception as e:
        logging.error("Saving to file Exception: %s" % e)

    # 然后以 Json 形式保存到数据库
    try:
        with DB_CONN.cursor() as cursor:
            # Create a new record
            sql = "INSERT INTO `whois` (`domain`, `whois`, `last_modified`) VALUES (%s, %s, %s)"
            cursor.execute(sql, (original_domain_str,
                                 json.dumps(json.loads(str(whois_obj))),
                                 time.strftime('%Y-%m-%d %H:%M:%S')))
        # connection is not autocommit by default. So you must commit to save your changes.
        DB_CONN.commit()

        with DB_CONN.cursor() as cursor:
            # Read a single record
            sql = "SELECT `id`, `domain` FROM `whois` WHERE `domain`=%s"
            cursor.execute(sql, (original_domain_str,))
            result = cursor.fetchone()
            logging.debug("Saved whois json into mysql: %s" % result)
    except Exception as e:
        logging.error("PyMySQL Exception: %s" % e)
