# database/db.py

import pymysql
import os

def create_connection():
    try:
        connection = pymysql.connect(
            host=os.environ.get("MYSQLHOST"),
            user=os.environ.get("MYSQLUSER"),
            password=os.environ.get("MYSQLPASSWORD"),
            database=os.environ.get("MYSQLDATABASE"),
            port=int(os.environ.get("MYSQLPORT")),
            cursorclass=pymysql.cursors.DictCursor
        )
        return connection
    except Exception as e:
        print("❌ Gagal koneksi ke MySQL:", e)
        return None

def init_db():
    conn = create_connection()
    if conn is None:
        print("❌ Tidak bisa membuat tabel karena koneksi gagal.")
        return

    cursor = conn.cursor()

    # 🔹 Tabel users
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id BIGINT PRIMARY KEY,
            username VARCHAR(255),
            alias VARCHAR(255)
        )
    """)

    # 🔹 Tabel messages
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id BIGINT AUTO_INCREMENT PRIMARY KEY,
            target_user_id BIGINT,
            sender_user_id BIGINT,
            sender_username VARCHAR(255),
            sender_name VARCHAR(255),
            message TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()
