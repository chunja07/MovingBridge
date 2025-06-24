#!/usr/bin/env python3
"""
Initialize SQLite database for development environment
"""
import sqlite3
import os

def create_dev_database():
    """Create development database with all necessary tables"""
    db_file = 'movingbridge_dev.db'
    
    # Remove existing database if it exists
    if os.path.exists(db_file):
        os.remove(db_file)
        print(f"Removed existing database: {db_file}")
    
    conn = sqlite3.connect(db_file)
    cur = conn.cursor()
    
    # Create all tables
    tables = [
        '''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''',
        
        '''CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name TEXT NOT NULL,
            business_number TEXT UNIQUE NOT NULL,
            ceo_name TEXT NOT NULL,
            contact_number TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            address TEXT NOT NULL,
            company_description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''',
        
        '''CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            location TEXT NOT NULL,
            salary TEXT,
            job_type TEXT NOT NULL,
            requirements TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (company_id) REFERENCES companies (id)
        )''',
        
        '''CREATE TABLE IF NOT EXISTS introductions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            nationality TEXT NOT NULL,
            gender TEXT NOT NULL,
            korean_fluent BOOLEAN NOT NULL,
            languages TEXT NOT NULL,
            preferred_jobs TEXT NOT NULL,
            preferred_location TEXT NOT NULL,
            availability TEXT NOT NULL,
            self_intro TEXT NOT NULL,
            video_link TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            -- Step 2 fields
            visa_type TEXT,
            visa_expiry DATE,
            past_jobs TEXT,
            expected_salary TEXT,
            housing_preference TEXT,
            licenses TEXT,
            religion TEXT,
            work_hours TEXT,
            step2_completed BOOLEAN DEFAULT FALSE
        )''',
        
        '''CREATE TABLE IF NOT EXISTS notices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''',
        
        '''CREATE TABLE IF NOT EXISTS forum_posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            author_name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''',
        
        '''CREATE TABLE IF NOT EXISTS reactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_type TEXT NOT NULL,
            post_id INTEGER NOT NULL,
            user_id TEXT NOT NULL,
            reaction_type TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(post_type, post_id, user_id)
        )'''
    ]
    
    for table_sql in tables:
        cur.execute(table_sql)
        print(f"Created table: {table_sql.split('(')[0].split()[-1]}")
    
    conn.commit()
    conn.close()
    
    print(f"✅ Development database created: {db_file}")

if __name__ == '__main__':
    create_dev_database()