import sqlite3
import hashlib
from datetime import datetime

DB_NAME = 'job_detection.db'

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS job_detections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            job_title TEXT NOT NULL,
            company_name TEXT NOT NULL,
            job_description TEXT NOT NULL,
            salary TEXT,
            location TEXT,
            prediction TEXT NOT NULL,
            confidence REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_activities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            activity_type TEXT NOT NULL,
            description TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_preferences (
            user_id INTEGER PRIMARY KEY,
            dark_mode INTEGER DEFAULT 0,
            compact_view INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(username, password):
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)',
                      (username, hash_password(password)))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def verify_user(username, password):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?',
                  (username, hash_password(password)))
    user = cursor.fetchone()
    conn.close()
    return user is not None

def get_user_id(username):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def save_job_detection(username, job_title, company_name, job_description, salary, location, prediction, confidence):
    user_id = get_user_id(username)
    if not user_id:
        return False
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO job_detections 
        (user_id, job_title, company_name, job_description, salary, location, prediction, confidence)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, job_title, company_name, job_description, salary, location, prediction, confidence))
    conn.commit()
    conn.close()
    return True

def get_user_detections(username, limit=10):
    user_id = get_user_id(username)
    if not user_id:
        return []
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM job_detections 
        WHERE user_id = ? 
        ORDER BY created_at DESC 
        LIMIT ?
    ''', (user_id, limit))
    results = cursor.fetchall()
    conn.close()
    return [dict(row) for row in results]

def get_user_profile(username):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT id, username, created_at FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    
    if not user:
        conn.close()
        return None
    
    user_dict = dict(user)
    cursor.execute('SELECT COUNT(*) as total FROM job_detections WHERE user_id = ?', (user_dict['id'],))
    user_dict['total_detections'] = cursor.fetchone()[0]
    
    conn.close()
    return user_dict

def log_activity(username, activity_type, description):
    user_id = get_user_id(username)
    if not user_id:
        return False
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO user_activities (user_id, activity_type, description) VALUES (?, ?, ?)',
                  (user_id, activity_type, description))
    conn.commit()
    conn.close()
    return True

def get_user_activities(username, limit=4):
    user_id = get_user_id(username)
    if not user_id:
        return []
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT activity_type, description, created_at 
        FROM user_activities 
        WHERE user_id = ? 
        ORDER BY created_at DESC 
        LIMIT ?
    ''', (user_id, limit))
    results = cursor.fetchall()
    conn.close()
    return [dict(row) for row in results]

def get_user_preferences(username):
    user_id = get_user_id(username)
    if not user_id:
        return {'dark_mode': 0, 'compact_view': 0}
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT dark_mode, compact_view FROM user_preferences WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return dict(result)
    return {'dark_mode': 0, 'compact_view': 0}

def save_user_preferences(username, dark_mode, compact_view):
    user_id = get_user_id(username)
    if not user_id:
        return False
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO user_preferences (user_id, dark_mode, compact_view)
        VALUES (?, ?, ?)
    ''', (user_id, dark_mode, compact_view))
    conn.commit()
    conn.close()
    return True

init_db()
