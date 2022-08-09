import logging

def init():
    init_log()

def init_log():
    log = logging.getLogger('giro')
    log.setLevel(logging.INFO)