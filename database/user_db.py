import sqlite3

DB_NAME = "data/askuya.db"

def get_all_user_ids():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users")
    results = cursor.fetchall()
    conn.close()
    return [row[0] for row in results]
