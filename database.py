import sqlite3
import os

_DB_NAME_ = 'paula.sqlite'

def _init():
    con = sqlite3.connect(_DB_NAME_)
    cursor = con.cursor()
    # Creates the basic schema
    with open('schema.sql', 'rt', encoding="utf-8") as f:
        cursor.executescript(f.read())
    # Prepopulates the database if needed
    if os.path.isfile('data.sql'):
        with open('data.sql', 'rt', encoding="utf-8") as f:
            cursor.executescript(f.read())
    con.commit()
    con.close()

def init():
    if not os.path.isfile(_DB_NAME_):
        _init()

def get_all_tables():
    con = sqlite3.connect(_DB_NAME_)
    cursor = con.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    results = cursor.fetchall()
    con.close()
    return results

def add_user(user_id, name, last_name):
    con = sqlite3.connect(_DB_NAME_)
    cursor = con.cursor()
    cursor.execute("INSERT INTO USERS VALUES (?, ?, ?)", (user_id, name, last_name))
    con.commit()
    con.close()

# Returns the name of the user if allowed, otherwise return None
def get_user_name(user_id):
    con = sqlite3.connect(_DB_NAME_)
    cursor = con.cursor()
    cursor.execute("SELECT name FROM USERS WHERE id=?", (user_id,))
    results = cursor.fetchall()
    con.close()
    if len(results) != 1:
        return None
    return results[0][0]

def add_contact():
    pass

def get_contact():
    pass
