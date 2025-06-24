from database.db import create_connection

def get_all_users():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, username, alias FROM users")
    results = cursor.fetchall()
    conn.close()
    return results
