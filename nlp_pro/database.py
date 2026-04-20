import sqlite3
import os

DATABASE = 'database.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('faculty', 'student')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS papers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            faculty_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            summary TEXT,
            score REAL DEFAULT 0,
            keywords TEXT,
            file_path TEXT NOT NULL,
            upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (faculty_id) REFERENCES users(id)
        )
    ''')

    conn.commit()
    conn.close()
    print("✅ Database initialized successfully.")

def add_user(name, email, password, role):
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            'INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)',
            (name, email, password, role)
        )
        conn.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()

def get_user_by_email(email):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
    user = cursor.fetchone()
    conn.close()
    return user

def get_user_by_id(user_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user

def add_paper(faculty_id, title, summary, score, keywords, file_path):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO papers (faculty_id, title, summary, score, keywords, file_path) VALUES (?, ?, ?, ?, ?, ?)',
        (faculty_id, title, summary, score, keywords, file_path)
    )
    conn.commit()
    paper_id = cursor.lastrowid
    conn.close()
    return paper_id

def get_papers_by_faculty(faculty_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        'SELECT * FROM papers WHERE faculty_id = ? ORDER BY upload_date DESC',
        (faculty_id,)
    )
    papers = cursor.fetchall()
    conn.close()
    return papers

def get_all_papers():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT p.*, u.name as faculty_name 
        FROM papers p 
        JOIN users u ON p.faculty_id = u.id 
        ORDER BY p.upload_date DESC
    ''')
    papers = cursor.fetchall()
    conn.close()
    return papers

def get_paper_by_id(paper_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT p.*, u.name as faculty_name 
        FROM papers p 
        JOIN users u ON p.faculty_id = u.id 
        WHERE p.id = ?
    ''', (paper_id,))
    paper = cursor.fetchone()
    conn.close()
    return paper

def get_faculty_stats(faculty_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT COUNT(*) as total_papers, 
               AVG(score) as avg_score,
               MAX(score) as max_score
        FROM papers WHERE faculty_id = ?
    ''', (faculty_id,))
    stats = cursor.fetchone()
    conn.close()
    return stats
