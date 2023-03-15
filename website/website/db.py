import mysql.connector as mysql
from .config import *
from flask import g

# Add the mysql db_connection to g
# NOTE: create a cursor before executing any sql commands
def get_db():
    if 'db' not in g:
        g.db = mysql.connect(
            host=MYSQL_HOST,
            database=MYSQL_DATABASE,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
        )
    return g.db


# close connection to db
def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def db_insert(query, values=()):
    db_connection = get_db()
    db = db_connection.cursor()
    db.execute(query, values)
    db_connection.commit()
    db.close()


#returns tuple
def db_fetch(query, args=(), one=False):
    db_connection = get_db()
    db = db_connection.cursor()
    db.execute(query, args)
    rv=db.fetchall()
    db.close()

    return (rv[0] if rv else None) if one else rv


#returns dictionary {col:val}
def db_fetch_dict(query, args=(), one=False):
    db_connection = get_db()
    db = db_connection.cursor()
    db.execute(query, args)
    try:
        if one:
            rv = dict(zip(db.column_names, db.fetchone()))
        else:
            rv = dict(zip(db.column_names, db.fetchall()))
    except:
        rv = None
    db.close()
    return rv

def db_fetch_notebooks(query, args=(), one=False):
    db_connection = get_db();
    db = db_connection.cursor();
    db.execute(query, args)
    try:
        if one:
            rv = dict(zip(db.column_names, db.fetchone()))
        else:
            a = db.fetchall()
            rv = dict(zip(range(len(a)), a))
    except:
        rv = None
    db.close()
    return rv
