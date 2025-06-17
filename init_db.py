# ✅ 1. init_db.py (한 번만 실행)
import sqlite3

conn = sqlite3.connect("movingbridge.db")
c = conn.cursor()

# 자기소개 테이블
c.execute('''
CREATE TABLE IF NOT EXISTS introductions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    nationality TEXT,
    languages TEXT,
    introduction TEXT,
    video_link TEXT,
    timestamp TEXT
)
''')

# 채용공고 테이블
c.execute('''
CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    company TEXT,
    contact TEXT,
    description TEXT,
    timestamp TEXT
)
''')

# 공지사항 테이블
c.execute('''
CREATE TABLE IF NOT EXISTS notices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    content TEXT,
    timestamp TEXT
)
''')

# 생활 포럼 테이블
c.execute('''
CREATE TABLE IF NOT EXISTS forums (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    author TEXT,
    title TEXT,
    content TEXT,
    timestamp TEXT
)
''')

conn.commit()
conn.close()
print("✅ movingbridge.db 초기화 완료")
