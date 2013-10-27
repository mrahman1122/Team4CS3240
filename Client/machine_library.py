__author__ = 'zheng_000'

import socket

def get_machine_name():
    return socket.gethostname()