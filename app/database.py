import sqlite3

DB_NAME = '/app/streams.db'  # Use an absolute path

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS streams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            url TEXT NOT NULL,
            auth TEXT
        )
    ''')
    conn.commit()
    conn.close()

def add_stream(name, url, auth):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO streams (name, url, auth) VALUES (?, ?, ?)', (name, url, auth))
    conn.commit()
    conn.close()

def get_streams():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM streams')
    streams = cursor.fetchall()
    conn.close()
    return [Stream(*s) for s in streams]

def get_stream_by_id(stream_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM streams WHERE id = ?', (stream_id,))
    stream = cursor.fetchone()
    conn.close()
    return Stream(*stream) if stream else None

def delete_stream(stream_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM streams WHERE id = ?', (stream_id,))
    conn.commit()
    conn.close()

class Stream:
    def __init__(self, id, name, url, auth):
        self.id = id
        self.name = name
        self.url = url
        self.auth = auth

