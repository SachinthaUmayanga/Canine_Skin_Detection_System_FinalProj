import sqlite3

def get_db_connection():
    """
    Establishes a connection to the SQLite database.
    """
    conn = sqlite3.connect('site.db')
    conn.row_factory = sqlite3.Row  # Allows accessing rows as dictionaries
    return conn
