import sqlite3

def get_db():
    return sqlite3.connect("stats.db")

def init_db():
    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS stats_daily (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        count INTEGER,
        date TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS stats_total (
        username TEXT PRIMARY KEY,
        total_count INTEGER
    )
    """)

    db.commit()
    db.close()
