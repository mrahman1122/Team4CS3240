__author__ = 'zheng_000'
from user_account_library import *
from machine_library import *
from db_calls import *

def main():
    install()

def install():
    user_input = False
    has_account = False
    while(not user_input):
        has_account_input = raw_input("Do you have an account? y/n: ").lower()
        if(has_account_input == "yes" or has_account_input == "y"):
            has_account = True
            user_input = True
        elif(has_account_input == "no" or has_account_input == "n"):
            user_input = True
    if(has_account):
        print "Please Log In:"
        username, hashed_password = prompt_login()
    else:
        print "Please Create an Account:"
        username, hashed_password = create_account()

    machine_name = get_machine_name()
    folder_path = input_folder_path()
    if(store_new_machine(username, hashed_password, machine_name, folder_path)):
        print "Installation Success!"
        return True
    else:
        print "Installation failed, try again later"
        return False

def input_folder_path():
    valid_path = False
    while(not valid_path):
        path = raw_input("Name your folder:")
        if(path_is_valid(path)):
            print path
            valid_path = True
            return path
        else:
            print "Invalid path."

def path_exists(path):
    #todo: check if path exists on client
    return False

def path_is_valid(path):
    #todo: check if path can be created on client
    return True

if __name__ == "__main__":
    main()