__author__ = 'mjr3vk'

import os

class Folder_Monitor:

    def __init__(self, onedir_path):

        before = os.listdir(onedir_path)
        file_dict_before_temp = {}
        file_dict_before = {}

        for path, subdirs, files in os.walk(onedir_path):
            for name in subdirs:
                time_stamp = os.path.getmtime(os.path.join(path, name))
                file_dict_before_temp[os.path.join(path, name)] = time_stamp
            for name in files:
                time_stamp = os.path.getmtime(os.path.join(path, name))
                file_dict_before_temp[os.path.join(path, name)] = time_stamp

        for key in file_dict_before_temp:
            file_dict_before[key.replace(onedir_path, '')] = file_dict_before_temp[key]


        self.file_dict_before = file_dict_before
        self.onedir_path = onedir_path

    def set_file_dict_before(self, file_dict_before):
        self.file_dict_before = file_dict_before

    def get_file_dict_before(self):
        return self.file_dict_before

    def check_changes(self):

        file_list_changes = []
        file_list_changes[:] = []
        after = os.listdir(self.onedir_path)
        file_dict_after_temp = {}
        file_dict_after = {}

        for path, subdirs, files in os.walk(self.onedir_path):
            for name in subdirs:
                time_stamp = os.path.getmtime(os.path.join(path, name))
                file_dict_after_temp[os.path.join(path, name)] = time_stamp
            for name in files:
                time_stamp = os.path.getmtime(os.path.join(path, name))
                file_dict_after_temp[os.path.join(path, name)] = time_stamp

        for key in file_dict_after_temp:
            file_dict_after[key.replace(self.onedir_path, '')] = file_dict_after_temp[key]

        #handles multiple file additions, removals, and renames
        temp_change_list = []

        for key in file_dict_after:
            if self.file_dict_before.has_key(key) == False:
                if os.path.isdir(self.onedir_path + key):
                    temp_change_list.append([key.replace('\\', '/'), file_dict_after[key], "Folder Added"])
                else:
                    temp_change_list.append([key.replace('\\', '/'), file_dict_after[key], "Added"])

        for key in self.file_dict_before:
            if file_dict_after.has_key(key) == False:
                if os.path.isdir(self.onedir_path + key):
                    temp_change_list.append([key.replace('\\', '/'), self.file_dict_before[key], "Folder Removed"])
                else:
                    temp_change_list.append([key.replace('\\', '/'), self.file_dict_before[key], "Removed"])

        for row in temp_change_list:
            stamp = row[1]
            type = row[2]
            for newrow in temp_change_list:
                if stamp == newrow[1] and type != newrow[2]:
                    if row[2] == "Removed" or row[2] == "Folder Removed":
                        file_list_changes.append([row[0].replace('\\', '/'), row[1], "Renamed", newrow[0]])
                        print row[0] + " was renamed to " + newrow[0]
                    else:
                        file_list_changes.append([newrow[0].replace('\\', '/'), row[1], "Renamed", row[0]])
                        print newrow[0] + " was renamed to " + row[0]
                    temp_change_list.remove(row)
                    temp_change_list.remove(newrow)

        #puts remaining changes into final change list
        for row in temp_change_list:
            file_list_changes.append(row)
            if row[2] == "Added" or row[2] == "Folder Added":
                print row[0] + " was added"
            else:
                print row[0] + " was removed"

        #handles file modifications if not renamed
        for key in self.file_dict_before:
            if file_dict_after.has_key(key):
                if self.file_dict_before[key] != file_dict_after[key]:
                    if not os.path.isdir(self.onedir_path + key):
                        file_list_changes.append([key.replace('\\', '/'), file_dict_after[key], "Updated"])
                        print key + " was updated"

        self.file_dict_before = file_dict_after
        return file_list_changes



