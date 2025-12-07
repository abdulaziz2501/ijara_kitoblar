import datetime
from database import get_db
from config import TRACKED_USERS

def save_today(data_dict):
    db = get_db()
    cursor = db.cursor()
    today = datetime.date.today().isoformat()

    cursor.execute("DELETE FROM stats_daily WHERE date = ?", (today,))

    for user, count in data_dict.items():
        cursor.execute("INSERT INTO stats_daily (username, count, date) VALUES (?, ?, ?)",
                       (user, count, today))

        cursor.execute("""
        INSERT INTO stats_total (username, total_count) VALUES (?, ?)
        ON CONFLICT(username) DO UPDATE SET total_count = total_count + ?
        """, (user, count, count))

    db.commit()
    db.close()

def get_today():
    db = get_db()
    cursor = db.cursor()
    today = datetime.date.today().isoformat()

    cursor.execute("SELECT username, count FROM stats_daily WHERE date = ?", (today,))
    rows = cursor.fetchall()

    return {u: c for u, c in rows}

def get_yesterday():
    db = get_db()
    cursor = db.cursor()
    yesterday = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()

    cursor.execute("SELECT username, count FROM stats_daily WHERE date = ?", (yesterday,))
    rows = cursor.fetchall()

    return {u: c for u, c in rows}

def calculate_diff(today, yesterday):
    diff = {}
    for user in TRACKED_USERS:
        diff[user] = today.get(user, 0) - yesterday.get(user, 0)
    return diff
