from database.db import create_connection

def add_user(user_id: int, username: str):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT IGNORE INTO users (user_id, username, alias)
        VALUES (%s, %s, NULL)
    """, (user_id, username))
    conn.commit()
    conn.close()

def get_user_by_id(user_id: int):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result  # (user_id, username, alias) atau None

def get_user_by_alias(alias: str):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE alias = %s", (alias,))
    result = cursor.fetchone()
    conn.close()
    return result

def set_alias(user_id: int, alias: str):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET alias = %s WHERE user_id = %s",
        (alias.lower(), user_id)
    )
    conn.commit()
    conn.close()

def alias_exists(alias: str, exclude_user_id: int = None):
    conn = create_connection()
    cursor = conn.cursor()

    if exclude_user_id:
        cursor.execute(
            "SELECT 1 FROM users WHERE LOWER(alias) = LOWER(%s) AND user_id != %s",
            (alias, exclude_user_id)
        )
    else:
        cursor.execute(
            "SELECT 1 FROM users WHERE LOWER(alias) = LOWER(%s)",
            (alias,)
        )

    result = cursor.fetchone()
    conn.close()
    return result is not None

def get_messages_for_user(user_id: int):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT message FROM messages
        WHERE target_user_id = %s
        ORDER BY timestamp DESC
        LIMIT 10
    """, (user_id,))
    results = cursor.fetchall()
    conn.close()
    return results
