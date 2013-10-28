__author__ = 'zheng_000'

import socket

def get_machine_name():
    return socket.gethostname()

def get_folder_path(username):
    #todo: contact server to get folder name
    return None