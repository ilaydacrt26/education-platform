import sqlite3
import streamlit as st

DATABASE_NAME = "education_platform.db"

def get_db_connection():
    conn = sqlite3.connect(DATABASE_NAME, timeout=30, isolation_level=None)
    conn.row_factory = sqlite3.Row # This allows accessing columns by name
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

