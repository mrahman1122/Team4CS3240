__author__ = 'zheng_000'
from user_account_library import *
from machine_library import *

def main():
    install()

def install():
    user_input = False
    has_account = False
    while(not user_input):
        has_account_input = raw_input("Do you have an account? y/n").lower()
        if(has_account_input == "yes" or has_account_input == "no"):
            has_account = True
            user_input = True
        elif(has_account_input == "y" or has_account_input == "n"):
            user_input = True
    if(has_account):
        username, hashed_password = prompt_login()
    else:
        username, hashed_password = create_account()

    machine_name = get_machine_name()
    folder_path = get_folder_path()
    if(store_new_user_information(username, hashed_password, machine_name, folder_path)):
        print "Installation Success!"
        return True
    else:
        print "Communication with service failed, try again later"
        return False

def get_folder_path():
    valid_path = False
    while(not valid_path):
        path = raw_input("Enter exact path:")
        if(path_is_valid(path)):
            valid_path = True
        else:
            print "Invalid path."

def store_new_user_information(username, hashed_password, machine_name, folder_path):
    #todo: talk to server and try to store information
    return False

def path_exists(path):
    #todo: check if path exists
    return False

def path_is_valid(path):
    #todo: check if path can be created
    return True

if __name__ == "__main__":
    main()