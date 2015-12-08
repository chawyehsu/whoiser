# -*- coding: utf-8 -*-
import logging
import os
import pymysql

DEBUG = True
LOG_LEVEL = logging.DEBUG

BASE_DIR = os.getcwd()
DATA_DIR = os.path.join(BASE_DIR, 'data')
WHOIS_DIR = os.path.join(DATA_DIR, 'whois')

DATA_FILE = os.path.join(DATA_DIR, 'test.txt')
WHOIS_FILENAME = 'whois.txt'

WHOISER_THREAD = 7
SAVER_THREAD = 3
FAIL_SAVER_THREAD = 1

USE_WHOIS_CMD = True

# Connect to the database
DB_CONN = pymysql.connect(host='127.0.0.1', user='root', password='', db='db_whois', charset='utf8',
                          cursorclass=pymysql.cursors.DictCursor)
