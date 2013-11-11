__author__ = 'mjr3vk'

import os

#pull folder_path from database, and filename from server (Remove request?)
def remove_file_on_client(folder_path, filename):

    print os.listdir(folder_path)
    os.remove(folder_path+filename)
    print os.listdir(folder_path)

#pull folder_path from database, and filename and new_filename from server (Rename request?)
def rename_file_on_client(folder_path, filename, new_filename):
    #or can use rename(pathFrom, pathTo) from twisted library
    print os.listdir(folder_path)
    os.rename(folder_path+filename, folder_path+new_filename)
    print os.listdir(folder_path)

def add_file_on_client(folder_path, filename):
    #use storeFile(path) from twisted library
    print "placeholder"

def update_file_on_client(folder_path, filename):
    # removeFile(folder_path, filename)
    # addFile(folder_path, filename)
    print "placeholder"

#renameFile("C:/Users/Student/Desktop/TestFolder/", "testfile2.txt", "testfile3.txt")
#addFile("C:/Users/Student/Desktop/TestFolder/", "testfile3.txt")