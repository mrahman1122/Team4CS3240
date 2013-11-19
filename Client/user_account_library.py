__author__ = 'zheng_000'

import getpass
from db_calls import *

def create_account():
    username = set_username()
    password = set_password()
    hashed_password = hash_password(password)
    if(store_new_account(username, hashed_password)):
        print "Succeeded in creating new user: " + username
    else:
        print "Failed to create new user: " + username
    return username, hashed_password

def login():
    logged_in = False
    while(not logged_in):
        username, hashed_password = prompt_login()
        if(user_is_valid(username, hashed_password)):
            print "Valid Credentials!"
            logged_in = True
        else:
            print "Invalid Credentials"
    return username, hashed_password

def prompt_login():
    def login():
        print "Login:"
    username = prompt_user()
    password = prompt_password("Password:")
    hashed_password = hash_password(password)
    return username, hashed_password

def prompt_user():
    return raw_input("Username:")

def prompt_password(prompt):
    return getpass.getpass(prompt)

def hash_password(password):
    salt = "A8912eASDkJHR341SA"
    return hashlib.sha512(password + salt).hexdigest()

def set_username():
    valid_user = False
    username = ""
    while(not valid_user):
        username = prompt_user()
        if(validate_username(username)):
            valid_user = True
        else:
            print "Invalid Username"
    return username

def set_password():
    valid_password = False
    password = ""
    while(not valid_password):
        password1 = prompt_password("Password:")
        password2 = prompt_password("Confirm Password:")
        if(password1 != password2):
            print "Passwords do not match! Try again."
        else:
            valid_password = True
            password = password1
    return password

def reset_password():
    print "Please Log In"
    username, h = login()
    print "Please Change Your Password"
    password = set_password()
    new_hashed_password = hash_password(password)
    change_password(username, new_hashed_password)

def validate_username(username):
    if(len(username) < 3 or len(username) > 20):
        return False
    if(username_exists(username)):
        return False
    return True