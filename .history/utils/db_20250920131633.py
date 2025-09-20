import sqlite3
import bcrypt
import secrets
import string

DATABASE_NAME = "education_platform.db"

def get_db_connection():
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row # Bu sayede sütunlara isimleriyle erişebiliriz
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
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print("Veritabanı ve kullanıcı tablosu oluşturuldu veya zaten mevcut.")

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

