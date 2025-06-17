# ✅ 1. init_db.py (한 번만 실행)
import sqlite3

conn = sqlite3.connect("movingbridge.db")
c = conn.cursor()

# 사용자 테이블
c.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
)
''')

# 자기소개 테이블
c.execute('''
CREATE TABLE IF NOT EXISTS introductions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    nationality TEXT NOT NULL,
    languages TEXT NOT NULL,
    introduction TEXT NOT NULL,
    youtube_link TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
''')

# 채용공고 테이블
c.execute('''
CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    company TEXT NOT NULL,
    contact TEXT NOT NULL,
    description TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
''')

# 공지사항 테이블
c.execute('''
CREATE TABLE IF NOT EXISTS notices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
''')

# 생활 포럼 테이블
c.execute('''
CREATE TABLE IF NOT EXISTS forums (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    author TEXT NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
''')

# 이모지 반응 테이블 (채용공고용)
c.execute('''
CREATE TABLE IF NOT EXISTS job_reactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    emoji TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(job_id, user_id, emoji)
)
''')

# 이모지 반응 테이블 (자기소개용)
c.execute('''
CREATE TABLE IF NOT EXISTS intro_reactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    intro_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    emoji TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(intro_id, user_id, emoji)
)
''')

conn.commit()
conn.close()
print("✅ movingbridge.db 초기화 완료")
