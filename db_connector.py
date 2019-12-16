import sqlite3


def database_connect():
    '''
    this function connects to the database and makes the results of running queries return a list of
    dictionaries as opposed to tuples, dicts are easier to work with
    '''
    sql = sqlite3.connect('/home/jane/Desktop/flask_ultimate/data.db')
    sql.row_factory = sqlite3.Row
    return sql


def get_database(global_content_holder):
    '''
    this function checks whether the database is still available for the flask app, in g, where all global
    values are, if not we add it
    '''
    if not hasattr(g, 'sqlite3'):
        global_content_holder.sqlite_db = database_connect()
    return global_content_holder.sqlite_db