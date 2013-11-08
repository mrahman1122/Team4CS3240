__author__ = 'mjr3vk'
#folder monitoring version 1
#ApplyChanges method will occur beforehand
import os, time
from clientExample import *

#folder_path is pulled from sqlite database after login on particular machine
def checkChangesOnClient(folder_path):
    #prime the file list
    before = os.listdir(folder_path)
    file_list_changes = []
    file_dict_before = {}

    for filename in before:
            path = folder_path+filename
            time_stamp = os.path.getmtime(path)
            file_dict_before[filename] = time_stamp

    while 1:
        time.sleep(5)
        #setup
        file_list_changes[:] = []
        after = os.listdir(folder_path)
        file_dict_after = {}
        for filename in after:
            path = folder_path+filename
            time_stamp = os.path.getmtime(path)
            file_dict_after[filename] = time_stamp

        #handles multiple file additions, removals, and renames
        temp_change_list = []

        for key in file_dict_after:
            if file_dict_before.has_key(key) == False:
                temp_change_list.append([key, file_dict_after[key], "Added"])

        for key in file_dict_before:
            if file_dict_after.has_key(key) == False:
                temp_change_list.append([key, file_dict_before[key], "Removed"])

        for row in temp_change_list:
            stamp = row[1]
            type = row[2]
            for newrow in temp_change_list:
                if stamp == newrow[1] and type != newrow[2]:
                    if row[2] == "Removed":
                        file_list_changes.append([row[0], row[1], "Renamed", newrow[0]])
                    else:
                        file_list_changes.append([newrow[0], row[1], "Renamed", row[0]])
                    temp_change_list.remove(row)
                    temp_change_list.remove(newrow)

        for row in temp_change_list:
            file_list_changes.append(row)

        #handles file modifications if not renamed
        for key in file_dict_before:
            if file_dict_after.has_key(key):
                if file_dict_before[key] != file_dict_after[key]:
                    file_list_changes.append([key, file_dict_after[key], "Updated"])

        file_dict_before = file_dict_after
        print file_list_changes #this will be changed to create FTP object and send the object to the server

    #FTPClient.methods

checkChangesOnClient("C:/Users/Student/Desktop/TestFolder/")