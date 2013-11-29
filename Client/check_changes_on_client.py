__author__ = 'mjr3vk'
#folder monitoring version 1
#ApplyChanges method will occur beforehand
import os, time
from Folder_Monitor import Folder_Monitor

def check_changes_on_client():

    fm = Folder_Monitor("C:/Users/Student\Desktop\TestFolder/")

    while 1:
        time.sleep(5)
        changes = fm.check_changes()
        print changes

check_changes_on_client()
