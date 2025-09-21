import sqlite3
import bcrypt
import secrets
import string
import streamlit as st

DATABASE_NAME = "education_platform.db"

def get_db_connection():
    conn = sqlite3.connect(DATABASE_NAME, timeout=30, isolation_level=None)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS teachers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            branch TEXT NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            class TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')
    cursor.execute('''

        CREATE TABLE IF NOT EXISTS virtual_classes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            class_name TEXT NOT NULL,
            invite_code TEXT NOT NULL UNIQUE,
            description TEXT,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            password TEXT NOT NULL,
            teacher_first_name TEXT NOT NULL,
            teacher_last_name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            event_type TEXT NOT NULL,
            teacher_first_name TEXT NOT NULL,
            teacher_last_name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS student_join_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            class_id INTEGER NOT NULL,
            student_name TEXT NOT NULL,
            student_class TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            request_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (class_id) REFERENCES virtual_classes (id)
        )
    ''')
=======
        CREATE TABLE IF NOT EXISTS quizzes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            teacher_id INTEGER NOT NULL,
            quiz_title TEXT NOT NULL,
            num_questions INTEGER NOT NULL,
            target_class TEXT NOT NULL,
            course_name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (teacher_id) REFERENCES teachers (id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quiz_questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            quiz_id INTEGER NOT NULL,
            question_text TEXT NOT NULL,
            option_a TEXT NOT NULL,
            option_b TEXT NOT NULL,
            option_c TEXT NOT NULL,
            option_d TEXT NOT NULL,
            correct_answer TEXT NOT NULL,
            FOREIGN KEY (quiz_id) REFERENCES quizzes (id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS assignments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            teacher_id INTEGER NOT NULL,
            assignment_title TEXT NOT NULL,
            description TEXT,
            due_date TEXT NOT NULL,
            target_class TEXT NOT NULL,
            course_name TEXT NOT NULL,
            file_path TEXT, -- New column for file path
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (teacher_id) REFERENCES teachers (id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS student_activities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            activity_type TEXT NOT NULL, -- 'quiz' or 'assignment'
            activity_id INTEGER NOT NULL,
            status TEXT NOT NULL, -- 'Yapmadı', 'Devam ediyor', 'Tamamladı'
            correct_answers INTEGER,
            incorrect_answers INTEGER,
            start_time TIMESTAMP,
            end_time TIMESTAMP,
            submission_data TEXT, -- For assignment answers or file paths
            FOREIGN KEY (student_id) REFERENCES students (id)
        )
    ''')
    conn.commit()
    conn.close()

def insert_quiz(teacher_id, quiz_title, num_questions, target_class, course_name, questions_data):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO quizzes (teacher_id, quiz_title, num_questions, target_class, course_name) VALUES (?, ?, ?, ?, ?)",
        (teacher_id, quiz_title, num_questions, target_class, course_name)
    )
    quiz_id = cursor.lastrowid # Get the ID of the newly inserted quiz
    
    for question in questions_data:
        cursor.execute(
            "INSERT INTO quiz_questions (quiz_id, question_text, option_a, option_b, option_c, option_d, correct_answer) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                quiz_id,
                question["question_text"],
                question["option_a"],
                question["option_b"],
                question["option_c"],
                question["option_d"],
                question["correct_answer"]
            )
        )
    
    conn.commit()
    conn.close()

def insert_assignment(teacher_id, assignment_title, description, due_date, target_class, course_name, file_path=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO assignments (teacher_id, assignment_title, description, due_date, target_class, course_name, file_path) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (teacher_id, assignment_title, description, due_date, target_class, course_name, file_path)
    )
    conn.commit()
    conn.close()

def get_all_courses(target_class):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """SELECT DISTINCT course_name, teacher_id FROM quizzes WHERE target_class = ?
           UNION
           SELECT DISTINCT course_name, teacher_id FROM assignments WHERE target_class = ?""",
        (target_class, target_class)
    )
    courses = cursor.fetchall()
    conn.close()
    return courses

def get_teacher_name_by_id(teacher_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT first_name, last_name FROM teachers WHERE id = ?", (teacher_id,))
    teacher = cursor.fetchone()
    conn.close()
    return teacher

def get_quizzes_for_course(course_name, target_class):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, quiz_title FROM quizzes WHERE course_name = ? AND target_class = ?", (course_name, target_class))
    quizzes = cursor.fetchall()
    conn.close()
    return quizzes

def get_assignments_for_course(course_name, target_class):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, assignment_title FROM assignments WHERE course_name = ? AND target_class = ?", (course_name, target_class))
    assignments = cursor.fetchall()
    conn.close()
    return assignments

def record_activity_start(student_id, activity_type, activity_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    # Check if an entry already exists for this student and activity
    cursor.execute(
        "SELECT * FROM student_activities WHERE student_id = ? AND activity_type = ? AND activity_id = ?",
        (student_id, activity_type, activity_id)
    )
    existing_activity = cursor.fetchone()

    if existing_activity:
        # Update existing activity to 'Devam ediyor' if it was 'Yapmadı'
        if existing_activity['status'] == 'Yapmadı':
            cursor.execute(
                "UPDATE student_activities SET status = 'Devam ediyor', start_time = CURRENT_TIMESTAMP WHERE id = ?",
                (existing_activity['id'],)
            )
    else:
        # Insert new activity as 'Devam ediyor'
        cursor.execute(
            "INSERT INTO student_activities (student_id, activity_type, activity_id, status, start_time) VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)",
            (student_id, activity_type, activity_id, 'Devam ediyor')
        )
    conn.commit()
    conn.close()

def record_activity_completion(student_id, activity_type, activity_id, correct_answers=None, incorrect_answers=None, submission_data=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE student_activities SET status = 'Tamamladı', end_time = CURRENT_TIMESTAMP, correct_answers = ?, incorrect_answers = ?, submission_data = ? WHERE student_id = ? AND activity_type = ? AND activity_id = ?",
        (correct_answers, incorrect_answers, submission_data, student_id, activity_type, activity_id)
    )
    conn.commit()
    conn.close()

def get_student_activity_status(student_id, activity_type, activity_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT status, correct_answers, incorrect_answers, submission_data FROM student_activities WHERE student_id = ? AND activity_type = ? AND activity_id = ?",
        (student_id, activity_type, activity_id)
    )
    status_info = cursor.fetchone()
    conn.close()
    # If no record exists, assume 'Yapmadı'
    if status_info:
        return status_info
    else:
        return {'status': 'Yapmadı', 'correct_answers': None, 'incorrect_answers': None, 'submission_data': None}


if __name__ == '__main__':
    init_db()
    print("Veritabanı ve tablolar oluşturuldu veya zaten mevcut.")

def generate_invite_code(length: int = 8) -> str:
    alphabet = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def create_virtual_class(teacher_first_name: str,
                         teacher_last_name: str,
                         class_name: str,
                         description: str,
                         date_str: str,
                         time_str: str,
                         password_plain: str) -> str:
    conn = get_db_connection()
    cursor = conn.cursor()

    # Duplicate check: same class name, date, time for same teacher
    cursor.execute('''
        SELECT 1 FROM virtual_classes 
        WHERE teacher_first_name = ? AND teacher_last_name = ? 
        AND class_name = ? AND date = ? AND time = ?
    ''', (teacher_first_name, teacher_last_name, class_name, date_str, time_str))
    
    if cursor.fetchone():
        conn.close()
        raise ValueError("Bu sınıf adı, tarih ve saat kombinasyonu zaten mevcut.")

    hashed_password = bcrypt.hashpw(password_plain.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    invite_code = None
    for _ in range(5):
        candidate = generate_invite_code()
        try:
            cursor.execute('''
                INSERT INTO virtual_classes (
                    class_name, invite_code, description, date, time, password, teacher_first_name, teacher_last_name
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                class_name,
                candidate,
                description,
                date_str,
                time_str,
                hashed_password,
                teacher_first_name,
                teacher_last_name
            ))
            invite_code = candidate
            break
        except sqlite3.IntegrityError:
            continue

    if invite_code is None:
        conn.rollback()
        conn.close()
        raise RuntimeError("Davet kodu üretilemedi. Lütfen tekrar deneyin.")

    conn.commit()
    conn.close()
    return invite_code

def list_virtual_classes_for_teacher(teacher_first_name: str, teacher_last_name: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, class_name, invite_code, description, date, time, created_at
        FROM virtual_classes
        WHERE teacher_first_name = ? AND teacher_last_name = ?
        ORDER BY date ASC, time ASC
    ''', (teacher_first_name, teacher_last_name))
    rows = cursor.fetchall()
    conn.close()
    return rows

def delete_virtual_class(class_id: int, teacher_first_name: str, teacher_last_name: str) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        DELETE FROM virtual_classes
        WHERE id = ? AND teacher_first_name = ? AND teacher_last_name = ?
    ''', (class_id, teacher_first_name, teacher_last_name))
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return deleted

# Event types with emojis
EVENT_TYPES = {
    "Konferans": "🎤",
    "Seminer": "📚", 
    "Toplantı": "👥",
    "Sınav": "📝",
    "Ödev Teslimi": "📋",
    "Proje Sunumu": "🎯",
    "Ara Tatil": "🏖️",
    "Bayram": "🎉",
    "Genel Duyuru": "📢",
    "Sosyal Etkinlik": "🎪"
}

def create_event(teacher_first_name: str,
                 teacher_last_name: str,
                 title: str,
                 description: str,
                 date_str: str,
                 time_str: str,
                 event_type: str) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Duplicate check: same title, date, time for same teacher
    cursor.execute('''
        SELECT 1 FROM events 
        WHERE teacher_first_name = ? AND teacher_last_name = ? 
        AND title = ? AND date = ? AND time = ?
    ''', (teacher_first_name, teacher_last_name, title, date_str, time_str))
    
    if cursor.fetchone():
        conn.close()
        raise ValueError("Bu etkinlik başlığı, tarih ve saat kombinasyonu zaten mevcut.")
    
    try:
        cursor.execute('''
            INSERT INTO events (
                title, description, date, time, event_type, teacher_first_name, teacher_last_name
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (title, description, date_str, time_str, event_type, teacher_first_name, teacher_last_name))
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        conn.close()

def list_events_for_teacher(teacher_first_name: str, teacher_last_name: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, title, description, date, time, event_type, created_at
        FROM events
        WHERE teacher_first_name = ? AND teacher_last_name = ?
        ORDER BY date ASC, time ASC
    ''', (teacher_first_name, teacher_last_name))
    rows = cursor.fetchall()
    conn.close()
    return rows

def delete_event(event_id: int, teacher_first_name: str, teacher_last_name: str) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        DELETE FROM events
        WHERE id = ? AND teacher_first_name = ? AND teacher_last_name = ?
    ''', (event_id, teacher_first_name, teacher_last_name))
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return deleted

# Student join request functions
def create_student_join_request(class_id: int, student_name: str, student_class: str) -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if there's already a pending request for this student and class
    cursor.execute('''
        SELECT id FROM student_join_requests 
        WHERE class_id = ? AND student_name = ? AND status = 'pending'
    ''', (class_id, student_name))
    
    if cursor.fetchone():
        conn.close()
        raise ValueError("Bu sınıf için zaten bekleyen bir katılım isteğiniz var.")
    
    cursor.execute('''
        INSERT INTO student_join_requests (class_id, student_name, student_class)
        VALUES (?, ?, ?)
    ''', (class_id, student_name, student_class))
    
    request_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return request_id

def get_pending_requests_for_class(class_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, student_name, student_class, request_time
        FROM student_join_requests
        WHERE class_id = ? AND status = 'pending'
        ORDER BY request_time ASC
    ''', (class_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def update_request_status(request_id: int, status: str) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE student_join_requests 
        SET status = ?
        WHERE id = ?
    ''', (status, request_id))
    conn.commit()
    updated = cursor.rowcount > 0
    conn.close()
    return updated

def get_request_status(request_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT status FROM student_join_requests WHERE id = ?
    ''', (request_id,))
    result = cursor.fetchone()
    conn.close()
    return result['status'] if result else None

# Student functions
def get_student_requests(student_name: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT sjr.*, vc.class_name, vc.invite_code, vc.date, vc.time, vc.description
        FROM student_join_requests sjr
        JOIN virtual_classes vc ON sjr.class_id = vc.id
        WHERE sjr.student_name = ?
        ORDER BY sjr.request_time DESC
    ''', (student_name,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_student_approved_classes(student_name: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT sjr.*, vc.class_name, vc.invite_code, vc.date, vc.time, vc.description
        FROM student_join_requests sjr
        JOIN virtual_classes vc ON sjr.class_id = vc.id
        WHERE sjr.student_name = ? AND sjr.status = 'approved'
        ORDER BY vc.date ASC, vc.time ASC
    ''', (student_name,))
    rows = cursor.fetchall()
    conn.close()
    return rows

