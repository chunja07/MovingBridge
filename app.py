import os
import logging
import sqlite3
import re
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

# Admin credentials (in production, use environment variables)
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin123")

# In-memory data storage
job_posts = {}
intro_posts = {}
notice_posts = {}
forum_posts = {}
job_counter = 0
intro_counter = 0
notice_counter = 0
forum_counter = 0

@app.route('/')
def index():
    """Home page displaying both job postings and self-introductions"""
    # Sort posts by timestamp (newest first)
    sorted_jobs = sorted(job_posts.items(), key=lambda x: x[1]['timestamp'], reverse=True)
    sorted_intros = sorted(intro_posts.items(), key=lambda x: x[1]['timestamp'], reverse=True)
    sorted_notices = sorted(notice_posts.items(), key=lambda x: x[1]['timestamp'], reverse=True)
    sorted_forums = sorted(forum_posts.items(), key=lambda x: x[1]['timestamp'], reverse=True)
    
    return render_template('index.html', 
                         job_posts=sorted_jobs, 
                         intro_posts=sorted_intros,
                         notice_posts=sorted_notices,
                         forum_posts=sorted_forums)

@app.route('/job/new', methods=['GET', 'POST'])
def job_new():
    """Page for companies to create new job postings"""
    if request.method == 'POST':
        global job_counter
        job_counter += 1
        
        job_data = {
            'id': job_counter,
            'title': request.form.get('title', '').strip(),
            'company': request.form.get('company', '').strip(),
            'contact': request.form.get('contact', '').strip(),
            'description': request.form.get('description', '').strip(),
            'timestamp': datetime.now()
        }
        
        # Basic validation
        if not all([job_data['title'], job_data['company'], job_data['contact'], job_data['description']]):
            flash('모든 필드를 입력해주세요.', 'error')
            return render_template('job_new.html')
        
        job_posts[job_counter] = job_data
        flash('구인공고가 성공적으로 등록되었습니다.', 'success')
        return redirect(url_for('job_view', job_id=job_counter))
    
    return render_template('job_new.html')

@app.route('/job')
def job_list():
    """Page displaying all job postings"""
    sorted_jobs = sorted(job_posts.items(), key=lambda x: x[1]['timestamp'], reverse=True)
    return render_template('job_list.html', job_posts=sorted_jobs)

@app.route('/job/<int:job_id>')
def job_view(job_id):
    """Page to view a specific job posting"""
    if job_id not in job_posts:
        flash('존재하지 않는 구인공고입니다.', 'error')
        return redirect(url_for('job_list'))
    
    job = job_posts[job_id]
    return render_template('job_view.html', job=job)

@app.route('/intro/new', methods=['GET', 'POST'])
def intro_new():
    """Page for foreign workers to create self-introductions"""
    if request.method == 'POST':
        global intro_counter
        intro_counter += 1
        
        intro_data = {
            'id': intro_counter,
            'name': request.form.get('name', '').strip(),
            'nationality': request.form.get('nationality', '').strip(),
            'languages': request.form.get('languages', '').strip(),
            'youtube_link': request.form.get('youtube_link', '').strip(),
            'introduction': request.form.get('introduction', '').strip(),
            'timestamp': datetime.now()
        }
        
        # Basic validation
        if not all([intro_data['name'], intro_data['nationality'], intro_data['languages'], intro_data['introduction']]):
            flash('필수 필드를 모두 입력해주세요.', 'error')
            return render_template('intro_new.html')
        
        intro_posts[intro_counter] = intro_data
        flash('자기소개가 성공적으로 등록되었습니다.', 'success')
        return redirect(url_for('intro_view', intro_id=intro_counter))
    
    return render_template('intro_new.html')

@app.route('/intro')
def intro_list():
    """Page displaying all self-introductions"""
    sorted_intros = sorted(intro_posts.items(), key=lambda x: x[1]['timestamp'], reverse=True)
    return render_template('intro_list.html', intro_posts=sorted_intros)

@app.route('/intro/<int:intro_id>')
def intro_view(intro_id):
    """Page to view a specific self-introduction"""
    if intro_id not in intro_posts:
        flash('존재하지 않는 자기소개입니다.', 'error')
        return redirect(url_for('intro_list'))
    
    intro = intro_posts[intro_id]
    return render_template('intro_view.html', intro=intro)

# Notice routes
@app.route('/notice')
def notice_list():
    """Page displaying all notices"""
    sorted_notices = sorted(notice_posts.items(), key=lambda x: x[1]['timestamp'], reverse=True)
    return render_template('notice_list.html', notice_posts=sorted_notices)

@app.route('/notice/new', methods=['GET', 'POST'])
def notice_new():
    """Page to create new notices - requires login"""
    auth_check = require_login()
    if auth_check:
        return auth_check
    
    if request.method == 'POST':
        global notice_counter
        notice_counter += 1
        
        notice_data = {
            'id': notice_counter,
            'title': request.form.get('title', '').strip(),
            'content': request.form.get('content', '').strip(),
            'timestamp': datetime.now()
        }
        
        if not all([notice_data['title'], notice_data['content']]):
            flash('모든 필드를 입력해주세요.', 'error')
            return render_template('notice_new.html')
        
        notice_posts[notice_counter] = notice_data
        flash('공지사항이 성공적으로 등록되었습니다.', 'success')
        return redirect(url_for('notice_view', notice_id=notice_counter))
    
    return render_template('notice_new.html')

@app.route('/notice/<int:notice_id>')
def notice_view(notice_id):
    """Page to view a specific notice"""
    if notice_id not in notice_posts:
        flash('존재하지 않는 공지사항입니다.', 'error')
        return redirect(url_for('notice_list'))
    
    notice = notice_posts[notice_id]
    return render_template('notice_view.html', notice=notice)

# Forum routes
@app.route('/forum')
def forum_list():
    """Page displaying all forum posts"""
    sorted_forums = sorted(forum_posts.items(), key=lambda x: x[1]['timestamp'], reverse=True)
    return render_template('forum_list.html', forum_posts=sorted_forums)

@app.route('/forum/new', methods=['GET', 'POST'])
def forum_new():
    """Page to create new forum posts"""
    if request.method == 'POST':
        global forum_counter
        forum_counter += 1
        
        forum_data = {
            'id': forum_counter,
            'author': request.form.get('author', '').strip(),
            'title': request.form.get('title', '').strip(),
            'content': request.form.get('content', '').strip(),
            'timestamp': datetime.now()
        }
        
        if not all([forum_data['author'], forum_data['title'], forum_data['content']]):
            flash('모든 필드를 입력해주세요.', 'error')
            return render_template('forum_new.html')
        
        forum_posts[forum_counter] = forum_data
        flash('포럼 게시글이 성공적으로 등록되었습니다.', 'success')
        return redirect(url_for('forum_view', forum_id=forum_counter))
    
    return render_template('forum_new.html')

@app.route('/forum/<int:forum_id>')
def forum_view(forum_id):
    """Page to view a specific forum post"""
    if forum_id not in forum_posts:
        flash('존재하지 않는 게시글입니다.', 'error')
        return redirect(url_for('forum_list'))
    
    forum = forum_posts[forum_id]
    return render_template('forum_view.html', forum=forum)

# User authentication helpers
def is_logged_in():
    return 'user_id' in session

def get_current_user():
    if not is_logged_in():
        return None
    
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    conn.close()
    return user

def require_login():
    if not is_logged_in():
        flash('로그인이 필요합니다.', 'error')
        return redirect(url_for('login'))
    return None

# Admin authentication helper
def is_admin():
    return session.get('admin_logged_in', False)

def require_admin():
    if not is_admin():
        flash('관리자 권한이 필요합니다.', 'error')
        return redirect(url_for('admin_login'))
    return None

# User authentication routes
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validation
        if not username or not password:
            flash('사용자명과 비밀번호를 모두 입력해주세요.', 'error')
            return render_template('register.html')
        
        if len(username) < 3:
            flash('사용자명은 3글자 이상이어야 합니다.', 'error')
            return render_template('register.html')
        
        if len(password) < 8:
            flash('비밀번호는 8글자 이상이어야 합니다.', 'error')
            return render_template('register.html')
        
        # Check for special character
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            flash('비밀번호에는 최소 1개의 특수문자(!@#$%^&*(),.?":{}|<>)가 포함되어야 합니다.', 'error')
            return render_template('register.html')
        
        # Check for at least one number
        if not re.search(r'\d', password):
            flash('비밀번호에는 최소 1개의 숫자가 포함되어야 합니다.', 'error')
            return render_template('register.html')
        
        # Check for at least one letter
        if not re.search(r'[a-zA-Z]', password):
            flash('비밀번호에는 최소 1개의 영문자가 포함되어야 합니다.', 'error')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('비밀번호가 일치하지 않습니다.', 'error')
            return render_template('register.html')
        
        # Check if username already exists
        conn = get_db_connection()
        existing_user = conn.execute('SELECT id FROM users WHERE username = ?', (username,)).fetchone()
        
        if existing_user:
            conn.close()
            flash('이미 사용 중인 사용자명입니다.', 'error')
            return render_template('register.html')
        
        # Create new user
        hashed_password = generate_password_hash(password)
        try:
            conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', 
                        (username, hashed_password))
            conn.commit()
            conn.close()
            
            flash('회원가입이 완료되었습니다. 로그인해주세요.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            conn.close()
            flash('회원가입 중 오류가 발생했습니다.', 'error')
            return render_template('register.html')
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not username or not password:
            flash('사용자명과 비밀번호를 모두 입력해주세요.', 'error')
            return render_template('login.html')
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash(f'{user["username"]}님 환영합니다!', 'success')
            
            # Redirect to intended page or home
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('사용자명 또는 비밀번호가 올바르지 않습니다.', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    username = session.get('username', '')
    session.pop('user_id', None)
    session.pop('username', None)
    if username:
        flash(f'{username}님 로그아웃되었습니다.', 'success')
    return redirect(url_for('index'))

# Admin routes
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            flash('관리자로 로그인되었습니다.', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('잘못된 관리자 정보입니다.', 'error')
    
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    flash('로그아웃되었습니다.', 'success')
    return redirect(url_for('index'))

@app.route('/admin')
def admin_dashboard():
    auth_check = require_admin()
    if auth_check:
        return auth_check
    
    # Statistics
    stats = {
        'total_jobs': len(job_posts),
        'total_intros': len(intro_posts),
        'total_notices': len(notice_posts),
        'total_forums': len(forum_posts)
    }
    
    # Recent posts
    recent_jobs = sorted(job_posts.items(), key=lambda x: x[1]['timestamp'], reverse=True)[:5]
    recent_intros = sorted(intro_posts.items(), key=lambda x: x[1]['timestamp'], reverse=True)[:5]
    recent_notices = sorted(notice_posts.items(), key=lambda x: x[1]['timestamp'], reverse=True)[:5]
    recent_forums = sorted(forum_posts.items(), key=lambda x: x[1]['timestamp'], reverse=True)[:5]
    
    return render_template('admin_dashboard.html', 
                         stats=stats,
                         recent_jobs=recent_jobs,
                         recent_intros=recent_intros,
                         recent_notices=recent_notices,
                         recent_forums=recent_forums)

@app.route('/admin/jobs')
def admin_jobs():
    auth_check = require_admin()
    if auth_check:
        return auth_check
    
    sorted_jobs = sorted(job_posts.items(), key=lambda x: x[1]['timestamp'], reverse=True)
    return render_template('admin_jobs.html', job_posts=sorted_jobs)

@app.route('/admin/jobs/<int:job_id>/delete', methods=['POST'])
def admin_delete_job(job_id):
    auth_check = require_admin()
    if auth_check:
        return auth_check
    
    if job_id in job_posts:
        del job_posts[job_id]
        flash('채용공고가 삭제되었습니다.', 'success')
    else:
        flash('존재하지 않는 채용공고입니다.', 'error')
    
    return redirect(url_for('admin_jobs'))

@app.route('/admin/intros')
def admin_intros():
    auth_check = require_admin()
    if auth_check:
        return auth_check
    
    sorted_intros = sorted(intro_posts.items(), key=lambda x: x[1]['timestamp'], reverse=True)
    return render_template('admin_intros.html', intro_posts=sorted_intros)

@app.route('/admin/intros/<int:intro_id>/delete', methods=['POST'])
def admin_delete_intro(intro_id):
    auth_check = require_admin()
    if auth_check:
        return auth_check
    
    if intro_id in intro_posts:
        del intro_posts[intro_id]
        flash('자기소개가 삭제되었습니다.', 'success')
    else:
        flash('존재하지 않는 자기소개입니다.', 'error')
    
    return redirect(url_for('admin_intros'))

@app.route('/admin/notices')
def admin_notices():
    auth_check = require_admin()
    if auth_check:
        return auth_check
    
    sorted_notices = sorted(notice_posts.items(), key=lambda x: x[1]['timestamp'], reverse=True)
    return render_template('admin_notices.html', notice_posts=sorted_notices)

@app.route('/admin/notices/<int:notice_id>/delete', methods=['POST'])
def admin_delete_notice(notice_id):
    auth_check = require_admin()
    if auth_check:
        return auth_check
    
    if notice_id in notice_posts:
        del notice_posts[notice_id]
        flash('공지사항이 삭제되었습니다.', 'success')
    else:
        flash('존재하지 않는 공지사항입니다.', 'error')
    
    return redirect(url_for('admin_notices'))

@app.route('/admin/forums')
def admin_forums():
    auth_check = require_admin()
    if auth_check:
        return auth_check
    
    sorted_forums = sorted(forum_posts.items(), key=lambda x: x[1]['timestamp'], reverse=True)
    return render_template('admin_forums.html', forum_posts=sorted_forums)

@app.route('/admin/forums/<int:forum_id>/delete', methods=['POST'])
def admin_delete_forum(forum_id):
    auth_check = require_admin()
    if auth_check:
        return auth_check
    
    if forum_id in forum_posts:
        del forum_posts[forum_id]
        flash('포럼 게시글이 삭제되었습니다.', 'success')
    else:
        flash('존재하지 않는 게시글입니다.', 'error')
    
    return redirect(url_for('admin_forums'))

@app.template_filter('datetime')
def datetime_filter(dt):
    """Format datetime for display"""
    return dt.strftime('%Y년 %m월 %d일 %H:%M')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

def get_db_connection():
    conn = sqlite3.connect('movingbridge.db')
    conn.row_factory = sqlite3.Row
    return conn