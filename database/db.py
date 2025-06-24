import sqlite3
import os

DB_PATH = "data/askuya.db"

def create_connection():
    conn = sqlite3.connect(DB_PATH)
    return conn

# database/db.py

def init_db():
    if not os.path.exists("data"):
        os.makedirs("data")

    conn = create_connection()
    cursor = conn.cursor()

    # Tabel users
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            alias TEXT
        )
    """)

    # ✅ Tabel messages dengan kolom lengkap
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            target_user_id INTEGER,
            sender_user_id INTEGER,
            sender_username TEXT,
            sender_name TEXT,
            message TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()

