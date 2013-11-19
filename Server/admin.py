__author__ = 'zheng_000'

import MySQLdb
from db_settings import *

def get_users():
    users = []
    db = MySQLdb.connect(db_server, db_username, db_password, db_database)
    c = db.cursor()
    numEntries = c.execute('SELECT username FROM ' + db_usertable)
    for i in range(numEntries):
        row = c.fetchone()
        users.append(row[0])
    c.close()
    db.commit()
    db.close()
    return users

def list_machines():
    machines = []
    db = MySQLdb.connect(db_server, db_username, db_password, db_database)
    c = db.cursor()
    numEntries = c.execute('SELECT m_id, username, machine_name, folder_path FROM ' + db_machinestable)
    for i in range(numEntries):
        row = c.fetchone()
        machines.append(row)
    c.close()
    db.commit()
    db.close()
    return machines

def hash_password(password):
    salt = "A8912eASDkJHR341SA"
    return hashlib.sha512(password + salt).hexdigest()

def change_password_for_user(username, password):
    db = MySQLdb.connect(db_server, db_username, db_password, db_database)
    c = db.cursor()
    hashed_password = hash_password(password)
    c.execute('UPDATE ' + db_usertable + ' set password=%s WHERE username=%s', (hashed_password, username))
    c.close()
    db.commit()
    db.close()


def change_client_folder_path(username, machine_name, new_folder_path):
    db = MySQLdb.connect(db_server, db_username, db_password, db_database)
    c = db.cursor()
    c.execute('UPDATE ' + db_machinestable + ' set folder_path=%s WHERE username=%s AND machine_name=%s', (new_folder_path, username, machine_name))
    c.close()
    db.commit()
    db.close()
    return

def delete_user(username):
    db = MySQLdb.connect(db_server, db_username, db_password, db_database)
    c = db.cursor()
    c.execute('DELETE FROM ' + db_cachetable + ' WHERE username=%s ', (username,))
    c.execute('DELETE FROM ' + db_machinestable + ' WHERE username=%s ', (username,))
    c.execute('DELETE FROM ' + db_usertable + ' WHERE username=%s ', (username,))
    c.close()
    db.commit()
    db.close()
    return
