# -*- coding: utf-8 -*-
import os

BASE_DIR = os.getcwd()
DATA_DIR = os.path.join(BASE_DIR, '/data')
WHOIS_DIR = os.path.join(DATA_DIR, '/whois')

DATA_FILE = os.path.join(DATA_DIR, 'test.txt')
WHOIS_FILENAME = '/whois.txt'

WHOISER_THREAD = 4
SAVER_THREAD = 2

USE_WHOIS_CMD = True
