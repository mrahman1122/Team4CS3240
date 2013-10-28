__author__ = 'zheng_000'
import sqlite3

db_file = 'OneDir.db'

def setup_tables():
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    c.execute('''CREATE TABLE users (
                username varchar(50) NOT NULL PRIMARY KEY,
                password varchar(255) NOT NULL
                )''')

    c.execute('''CREATE TABLE machines(
                m_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                username varchar(50) NOT NULL,
                machine_name varchar(50) NOT NULL,
                folder_path varchar(255) NOT NULL,
                FOREIGN KEY (username) REFERENCES users(username)
                )''')

    c.execute('''CREATE TABLE cache(
                c_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                username varchar(50) NOT NULL,
                m_id int NOT NULL,
                file_path varchar(50) NOT NULL,
                command varchar(50) NOT NULL,
                FOREIGN KEY (username) REFERENCES users(username),
                FOREIGN KEY (m_id) REFERENCES machines(m_id)
                )''')

    conn.commit()
    conn.close()

def drop_tables():
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    c.execute('''DROP TABLE IF EXISTS cache''')
    c.execute('''DROP TABLE IF EXISTS machines''')
    c.execute('''DROP TABLE IF EXISTS users''')
    conn.commit()
    conn.close()

#Remove all of the entries in the updatecache of username and m_id
def clear_cache(username, m_id):
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    c.execute('DELETE FROM cache WHERE username=? and m_id=?', (username, m_id))
    conn.commit()
    conn.close()

#updates the cache for all machines of the user that are not m_id
def update_cache(username, m_id, path, command):
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    machine_entries = c.execute('SELECT m_id FROM machines where username=?', (username,))
    for row in machine_entries:
        if row[0] != m_id:
            c.execute('INSERT INTO cache (username, m_id, file_path, command) VALUES (?,?,?,?)', (username, row[0], path, command))
    conn.commit()
    conn.close()

#get all updates necessary for user and machine
def get_updates(username, m_id):
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    entries = c.execute('SELECT file_path, command FROM cache WHERE username=? AND m_id=?', (username, m_id))
    for row in entries:
        file_path = row[0]
        command = row[1]
        #todo: do something with the file_path and command (build a ftp object or something?)

    conn.commit()
    conn.close()

#client calls this to see if the username already exists
def username_exists(username):
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    entries = c.execute('SELECT * FROM users WHERE username=?', (username))
    if len(entries) > 0:
        conn.commit()
        conn.close()
        return False
    conn.commit()
    conn.close()
    return True

#client calls this to try to login
def user_is_valid(username, hashed_password):
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    entries = c.execute('SELECT * FROM users WHERE username=?', (username,))
    if(len(entries) > 0 and hashed_password == entries[0][1]):
        conn.commit()
        conn.close()
        return True
    conn.commit()
    conn.close()
    return False

#client calls this to store a new account, returns whether or not it was successful
def store_new_account(username, hashed_password):
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    try:
        c.execute('INSERT INTO users (username, password) VALUES (?,?)' (username, hashed_password))
        conn.commit()
        conn.close()
        return True
    except:
        conn.close()
        return False

#client calls this to register a new machine, returns whether or not it was successful
def store_new_machine(username, hashed_password, machine_name, folder_path):
    if(not user_is_valid(username, hashed_password) or machine_exists(username, machine_name)):
        return False
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    try:
        c.execute('INSERT INTO machines (username, machine_name, folder_path) VALUES (?,?,?)',
                  (username, machine_name, folder_path))
        conn.commit()
        conn.close()
        return True
    except:
        conn.close()
        return False

#returns true if this username, machine_name pair already exists in the machines table
def machine_exists(username, machine_name):
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    entries = c.execute('SELECT * FROM machines WHERE username=? and machine_name=?', (username, machine_name))
    if len(entries) > 0:
        conn.commit()
        conn.close()
        return True
    conn.close()
    return False

#client calls this to get the folder_path for the specific machine, returns None if the machine does not exist
def get_folder_path(username, machine_name):
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    entries = c.execute('SELECT * FROM machines WHERE username=? AND machine_name=?', (username, machine_name))
    if len(entries) > 0:
        folder_path = entries[0][3]
        conn.commit()
        conn.close()
        return folder_path
    conn.close()
    return None