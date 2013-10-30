__author__ = 'mjr3vk'

import os

def removeFile(folder_path, filename):

    print os.listdir(folder_path)
    os.remove(folder_path+filename)
    print os.listdir(folder_path)

def renameFile(folder_path, filename, new_filename):

    print os.listdir(folder_path)
    os.rename(folder_path+filename, folder_path+new_filename)
    print os.listdir(folder_path)


renameFile("C:/Users/Student/Desktop/TestFolder/", "testfile2.txt", "testfile3.txt")