import bcrypt
import sqlite3
from utils.db import get_db_connection

def hash_password(password):
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed.decode('utf-8')

def check_password(password, hashed_password):
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

def register_user(username, email, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        hashed_password = hash_password(password)
        cursor.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                       (username, email, hashed_password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        # Kullanıcı adı veya e-posta zaten mevcut
        return False
    finally:
        conn.close()

def login_user(username_or_email, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? OR email = ?", (username_or_email, username_or_email))
    user = cursor.fetchone()
    conn.close()

    if user and check_password(password, user['password']):
        return user
    return None
