__author__ = 'zheng_000'

import MySQLdb
from db_settings import *

#SECTION: TABLE CREATION AND DELETION----------------------------------------------------------------
def setup_tables():
    db = MySQLdb.connect(db_server, db_username, db_password, db_database)
    c = db.cursor()
    print "CREATING USERS TABLE"
    c.execute('''CREATE TABLE ''' + db_usertable + '''
                (
                username varchar(50) NOT NULL PRIMARY KEY,
                password varchar(255) NOT NULL
                )''')

    print "CREATING MACHINES TABLE"
    c.execute('''CREATE TABLE ''' + db_machinestable + '''
                (
                m_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                username varchar(50) NOT NULL,
                machine_name varchar(50) NOT NULL,
                folder_path varchar(255) NOT NULL,
                FOREIGN KEY (username) REFERENCES users(username)
                )''')

    print "CREATING CACHE TABLE"
    c.execute('''CREATE TABLE ''' + db_cachetable + '''
                (
                c_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                username varchar(50) NOT NULL,
                m_id int NOT NULL,
                file_path varchar(50) NOT NULL,
                command varchar(50) NOT NULL,
                FOREIGN KEY (username) REFERENCES users(username),
                FOREIGN KEY (m_id) REFERENCES machines(m_id)
                )''')

    c.close()
    db.commit()
    db.close()

def drop_tables():
    db = MySQLdb.connect(db_server, db_username, db_password, db_database)
    c = db.cursor()
    print "DROPPING CACHE TABLE"
    c.execute('''DROP TABLE IF EXISTS ''' + db_cachetable)
    print "DROPPING MACHINES TABLE"
    c.execute('''DROP TABLE IF EXISTS ''' + db_machinestable)
    print "DROPPING USERS TABLE"
    c.execute('''DROP TABLE IF EXISTS ''' + db_usertable)
    c.close()
    db.commit()
    db.close()

#END TABLE CREATION AND DELETION SECTION------------------------------------------------------------


#SECTION: CACHE OPERATIONS--------------------------------------------------------------------------

#Remove all of the entries in the updatecache of username and m_id
def clear_cache(username, m_id):
    db = MySQLdb.connect(db_server, db_username, db_password, db_database)
    c = db.cursor()
    print "REMOVING ENTRIES FOR USER:" + username + " AND MACHINE ID: " + m_id
    c.execute('DELETE FROM ' + db_cachetable + ' WHERE username=? and m_id=?', (username, m_id))
    c.close()
    db.commit()
    db.close()

#updates the cache for all machines of the user that are not m_id
def update_cache(username, m_id, path, command):
    db = MySQLdb.connect(db_server, db_username, db_password, db_database)
    c = db.cursor()
    machine_entries = c.execute('SELECT m_id FROM ' + db_machinestable + ' where username=?', (username,))
    machine_ids = get_machine_ids_from_user(username)
    for machine_id in machine_ids:
        if machine_id != m_id:
            print "NEW CACHE ENTRY-----------------------"
            print "PATH:" + path
            print "COMMAND:" + command
            print "USER:" + username
            print "MACHINE ID:" + machine_id
            c.execute('INSERT INTO ' + db_cachetable + ' (username, m_id, file_path, command) VALUES (?,?,?,?)', (username, machine_id, path, command))
    c.close()
    db.commit()
    db.close()

#get all updates necessary for user and machine
def get_updates(username, m_id):
    db = MySQLdb.connect(db_server, db_username, db_password, db_database)
    c = db.cursor()
    entries = c.execute('SELECT file_path, command FROM ' + db_cachetable + ' WHERE username=? AND m_id=?', (username, m_id))
    for row in entries:
        file_path = row[0]
        command = row[1]
        #todo: do something with the file_path and command, return them as a list?
    c.close()
    db.commit()
    db.close()

#END CACHE OPERATIONS SECTION--------------------------------------------------------------------------

#SECTION: USER OPERATIONS------------------------------------------------------------------------------
#client calls this to see if the username already exists
def username_exists(username):
    db = MySQLdb.connect(db_server, db_username, db_password, db_database)
    c = db.cursor()
    entries = c.execute('SELECT * FROM ' + db_usertable + ' WHERE username=?', (username))
    if len(entries) > 0:
        c.close()
        db.commit()
        db.close()
        return False
    c.close()
    db.commit()
    db.close()
    return True

#client calls this to try to login
def user_is_valid(username, hashed_password):
    db = MySQLdb.connect(db_server, db_username, db_password, db_database)
    c = db.cursor()
    entries = c.execute('SELECT * FROM ' + db_usertable + ' WHERE username=?', (username,))
    if(len(entries) > 0 and hashed_password == entries[0][1]):
        c.close()
        db.commit()
        db.close()
        return True
    c.close()
    db.commit()
    db.close()
    return False

#client calls this to store a new account, returns whether or not it was successful
def store_new_account(username, hashed_password):
    db = MySQLdb.connect(db_server, db_username, db_password, db_database)
    c = db.cursor()
    try:
        c.execute('INSERT INTO ' + db_usertable + ' (username, password) VALUES (?,?)' (username, hashed_password))
        c.close()
        db.commit()
        db.close()
        return True
    except:
        c.close()
        db.close()
        return False

#END USER OPERATIONS SECTION

#SECTION: MACHINE OPERATIONS SECTION----------------------------------------------------------------------------

#client calls this to register a new machine, returns whether or not it was successful
def store_new_machine(username, hashed_password, machine_name, folder_path):
    if(not user_is_valid(username, hashed_password) or machine_exists(username, machine_name)):
        return False
    db = MySQLdb.connect(db_server, db_username, db_password, db_database)
    c = db.cursor()
    try:
        c.execute('INSERT INTO ' + db_machinestable + ' (username, machine_name, folder_path) VALUES (?,?,?)',
                  (username, machine_name, folder_path))
        c.close()
        db.commit()
        db.close()
        return True
    except:
        c.close()
        db.close()
        return False

#returns true if this username, machine_name pair already exists in the machines table
def machine_exists(username, machine_name):
    return get_machine_id(username, machine_name) != None

def get_machine_ids_from_user(username):
    db = MySQLdb.connect(db_server, db_usertable, db_password, db_database)
    c = db.cursor()
    entries = c.execute('SELECT * FROM ' + db_machinestable + ' WHERE username=?', (username))
    machine_ids = []
    for row in entries:
        machine_ids.append(row[0])
    c.close()
    db.close()
    return machine_ids

def get_machine_id(username, machine_name):
    db = MySQLdb.connect(db_server, db_username, db_password, db_database)
    c = db.cursor()
    entries = c.execute('SELECT * FROM ' + db_machinestable + ' WHERE username=? and machine_name=?', (username, machine_name))
    if len(entries) > 0:
        c.close()
        db.commit()
        db.close()
        return entries[0][0]
    c.close()
    db.close()
    return None

#client calls this to get the folder_path for the specific machine, returns None if the machine does not exist
def get_folder_path(username, machine_name):
    db = MySQLdb.connect(db_server, db_username, db_password, db_database)
    c = db.cursor()
    entries = c.execute('SELECT * FROM ' + db_machinestable + ' WHERE username=? AND machine_name=?', (username, machine_name))
    if len(entries) > 0:
        folder_path = entries[0][3]
        c.close()
        db.commit()
        db.close()
        return folder_path
    c.close()
    db.close()
    return None

#END MACHINE OPERATIONS SECTION-----------------------------------------------------------------------