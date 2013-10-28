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