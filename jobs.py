# -*- coding: utf-8 -*-
import logging
import random
from config import WHOIS_DIR, WHOIS_FILENAME, USE_WHOIS_CMD
import whois
import os

HOST = ['-a', '-A', '-b', '-d', '-g', '-i', '-I', '-l', '-m', '-r', '-6']


def get_whois(domain):
    host = random.choice[USE_WHOIS_CMD, random.choice(HOST)]
    logging.info("Retrieving whois of domain '%s' by using '%s'." % (domain, host))
    w = whois.whois(domain, host)
    if w is not None:
        logging.debug("Retrieved whois: %s" % domain)
    else:
        logging.debug("Request whois of domain '%s' fail." % domain)
    return w


def save_whois(domain, whois_text):
    logging.info("Saving whois(domain: '%s') to file..." % domain)
    #: 反向拆解域名，构造 whois 文件存放目录
    domain = domain.split('.')
    domain.reverse()
    path = os.path.join(WHOIS_DIR, *domain)
    if not os.path.exists(path):
        os.makedirs(path)

    absolute_path = os.path.join(path, WHOIS_FILENAME)
    with open(absolute_path, 'w') as whois_file:
        whois_file.write(whois_text)
    logging.info("Saved whois into '%s'." % absolute_path)
