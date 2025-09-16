import bcrypt
import sqlite3
from utils.db import get_db_connection

def hash_password(password):
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed.decode('utf-8')

def check_password(password, hashed_password):
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

def email_exists(email):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM teachers WHERE email = ?", (email,))
    teacher_exists = cursor.fetchone()
    cursor.execute("SELECT 1 FROM students WHERE email = ?", (email,))
    student_exists = cursor.fetchone()
    conn.close()
    return teacher_exists is not None or student_exists is not None

def register_teacher(first_name, last_name, email, branch, password):
    if email_exists(email):
        return False
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        hashed_password = hash_password(password)
        cursor.execute("INSERT INTO teachers (first_name, last_name, email, branch, password) VALUES (?, ?, ?, ?, ?)",
                       (first_name, last_name, email, branch, hashed_password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def register_student(first_name, last_name, student_class, email, password):
    if email_exists(email):
        return False
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        hashed_password = hash_password(password)
        cursor.execute("INSERT INTO students (first_name, last_name, class, email, password) VALUES (?, ?, ?, ?, ?)",
                       (first_name, last_name, student_class, email, hashed_password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def login_user(user_type, first_name, last_name, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    if user_type == "teacher":
        cursor.execute("SELECT * FROM teachers WHERE first_name = ? AND last_name = ?", (first_name, last_name))
    elif user_type == "student":
        cursor.execute("SELECT * FROM students WHERE first_name = ? AND last_name = ?", (first_name, last_name))
    else:
        return None

    user = cursor.fetchone()
    conn.close()

    if user and check_password(password, user['password']):
        return user
    return None
