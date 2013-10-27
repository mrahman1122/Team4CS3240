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
