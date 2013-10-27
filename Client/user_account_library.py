__author__ = 'zheng_000'

import getpass
import hashlib

def login():
    logged_in = False
    while(not logged_in):
        username, hashed_password = prompt_login()
        if(user_is_valid(username, hashed_password)):
            logged_in = True
        else:
            print "Invalid Credentials"
    return username, hashed_password

def prompt_login():
    def login():
        print "Login:"
    username = prompt_user()
    password = prompt_password()
    hashed_password = hash_password(password)
    return username, hashed_password

def prompt_user():
    return raw_input("Username:")

def prompt_password(prompt):
    return getpass.getpass(prompt)

def hash_password(password):
    salt = "A8912eASDkJHR341SA"
    return hashlib.sha512(password + salt).hexdigest()

def create_account():
    username = set_username()
    password = set_password()

def set_username():
    valid_user = False
    username = ""
    while(not valid_user):
        username = prompt_user()
        if(username_is_valid(username)):
            valid_user = True
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

def user_is_valid(username, hashed_password):
    #todo: check database to see if this is a user
    return True

def username_is_valid(username):
    if(len(username) < 3 or len(username) > 20):
        return False
    if(username_exists(username)):
        return False
    return True

def username_exists(username):
    #todo: check database to see if username exists
    return False

def store_account(username, hashed_password):
    #todo: store username and password in database
    return False