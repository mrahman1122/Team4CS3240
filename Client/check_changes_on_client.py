__author__ = 'mjr3vk'
#folder monitoring version 1
#ApplyChanges method will occur beforehand
import os, time
from client import *

#folder_path is pulled from sqlite database after login on particular machine
def check_changes_on_client(onedir_path):
    #prime the file list
    before = os.listdir(onedir_path)
    file_list_changes = []
    file_dict_before = {}

    for folder in before:
        if os.path.isdir(onedir_path + folder):
            for filename in os.listdir(onedir_path + folder):
                path = onedir_path + folder + "/" + filename
                time_stamp = os.path.getmtime(path)
                file_dict_before[folder + "/" + filename] = time_stamp
            # this includes the base folder
            path = onedir_path + folder
            time_stamp = os.path.getmtime(path)
            file_dict_before[folder] = time_stamp
        # folders below are actually file names
        else:
            path = onedir_path + folder
            time_stamp = os.path.getmtime(path)
            file_dict_before[folder] = time_stamp

    while 1:
        time.sleep(5)
        #setup
        file_list_changes[:] = []
        after = os.listdir(onedir_path)
        file_dict_after = {}

        for folder in after:
            if os.path.isdir(onedir_path + folder):
                for filename in os.listdir(onedir_path + folder):
                    path = onedir_path + folder + "/" + filename
                    time_stamp = os.path.getmtime(path)
                    file_dict_after[folder + "/" + filename] = time_stamp
                # this includes the base folder
                path = onedir_path + folder
                time_stamp = os.path.getmtime(path)
                file_dict_after[folder] = time_stamp
        # folder below are actually file names
            else:
                path = onedir_path + folder
                time_stamp = os.path.getmtime(path)
                file_dict_after[folder] = time_stamp

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
        print file_list_changes
        #ask if we still need to include timestamps on the server.  Easier to parse to file if no timestamps.
        with open('changes', 'a') as the_file:
            for change_list in file_list_changes:
                for change in change_list:
                    the_file.write(change)
                    the_file.write(',')
                the_file.write('\n')


check_changes_on_client("C:/Users/Student/Desktop/TestFolder/")