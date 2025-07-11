# database/user.py

from database.db import create_connection

def get_all_user_ids():
    conn = create_connection()
    if conn is None:
        return []

    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT user_id FROM users")
            results = cursor.fetchall()
            return [row['user_id'] for row in results]
    finally:
        conn.close()


def add_user(user_id, username, alias=None):
    conn = create_connection()
    if conn is None:
        return False

    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO users (user_id, username, alias)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE
                username = VALUES(username),
                alias = VALUES(alias)
            """, (user_id, username, alias))
        conn.commit()
        return True
    finally:
        conn.close()
