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