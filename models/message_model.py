import sqlite3
from database.db import create_connection

# 🔹 Simpan pesan anonim
def save_message(target_user_id: int, sender_user_id: int, sender_username: str, sender_name: str, message: str):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO messages (target_user_id, sender_user_id, sender_username, sender_name, message)
        VALUES (?, ?, ?, ?, ?)
    """, (target_user_id, sender_user_id, sender_username, sender_name, message))
    conn.commit()
    conn.close()

# 🔹 Ambil semua pesan masuk ke user (pendek)
def get_messages_for_user(user_id: int):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT message, timestamp
        FROM messages
        WHERE target_user_id = ?
        ORDER BY timestamp DESC
    """, (user_id,))
    results = cursor.fetchall()
    conn.close()
    return results

# 🔹 Ambil pesan masuk dengan detail (digunakan untuk tampil ke user)
def get_messages_for_user_detailed(user_id: int):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT sender_username, message, timestamp, sender_name, sender_user_id
        FROM messages
        WHERE target_user_id = ?
        ORDER BY timestamp DESC
    """, (user_id,))
    results = cursor.fetchall()
    conn.close()
    return results

# 🔹 Ambil semua pesan (untuk admin)
def get_all_messages_detailed():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT sender_username, sender_user_id, target_user_id, message, timestamp, sender_name
        FROM messages
        ORDER BY timestamp DESC
        LIMIT 50
    """)
    results = cursor.fetchall()
    conn.close()
    return results

# 🔍 Cari pesan berdasarkan alias dan keyword isi pesan
def search_messages_by_alias_and_keyword(user_id: int, keyword: str):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT sender_username, sender_user_id, message, timestamp, sender_name
        FROM messages
        WHERE target_user_id = ? AND message LIKE ?
        ORDER BY timestamp DESC
    """, (user_id, f"%{keyword}%"))
    results = cursor.fetchall()
    conn.close()
    return results

# 🔍 Digunakan saat admin cari berdasarkan alias
def get_messages_by_user_id(user_id: int):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT sender_name, sender_username, sender_user_id, message, timestamp
        FROM messages
        WHERE target_user_id = ?
        ORDER BY timestamp DESC
    """, (user_id,))
    results = cursor.fetchall()
    conn.close()
    return results

def get_all_messages():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT sender_name, sender_username, sender_user_id, message, timestamp, target_user_id
        FROM messages
        ORDER BY timestamp DESC
    """)
    results = cursor.fetchall()
    conn.close()
    return results

def get_user_by_alias(alias):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE alias = ?", (alias,))
    return cursor.fetchone()

def get_messages_by_alias(target_user_id):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT sender_name, sender_username, sender_user_id, message, timestamp
        FROM messages
        WHERE target_user_id = ?
        ORDER BY timestamp DESC
    """, (target_user_id,))
    return cursor.fetchall()

