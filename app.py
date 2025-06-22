import os
import logging
import psycopg2
import psycopg2.extras
import re
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_wtf.csrf import CSRFProtect
from flask_talisman import Talisman
from werkzeug.security import generate_password_hash, check_password_hash
from markupsafe import Markup

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET")

# Configure session for production deployment
app.config['SESSION_COOKIE_SECURE'] = False  # Allow HTTP in development
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Enable auto-escaping for all templates for XSS protection
app.jinja_env.autoescape = True

# Input sanitization function
def sanitize_input(text):
    """Sanitize user input to prevent XSS attacks"""
    if not text:
        return ""
    # Remove potentially dangerous HTML tags and scripts
    text = str(text).strip()
    # Basic HTML escaping is handled by Jinja2 auto-escaping
    return text

# Validate email format
def is_valid_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

# Initialize CSRF protection
csrf = CSRFProtect(app)

# Security headers with Flask-Talisman
csp = {
    'default-src': "'self'",
    'script-src': [
        "'self'",
        "'unsafe-inline'",
        "https://cdn.jsdelivr.net",
        "https://cdn.replit.com"
    ],
    'style-src': [
        "'self'",
        "'unsafe-inline'",
        "https://cdn.jsdelivr.net",
        "https://cdn.replit.com"
    ],
    'img-src': [
        "'self'",
        "data:",
        "https:"
    ],
    'font-src': [
        "'self'",
        "https://cdn.jsdelivr.net",
        "https://cdn.replit.com"
    ],
    'frame-src': [
        "https://www.youtube.com",
        "https://youtube.com"
    ]
}

talisman = Talisman(
    app,
    force_https=False,  # Allow HTTP in development
    strict_transport_security=False,  # Disable HSTS in development
    content_security_policy=csp,
    session_cookie_secure=False,  # Allow non-HTTPS cookies in development
    session_cookie_http_only=True
)

# Configure secure session cookies
app.config.update(
    SESSION_COOKIE_SECURE=False,  # Allow non-HTTPS cookies in development
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax'
)

# Admin credentials from environment variables
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD_HASH = generate_password_hash(os.environ.get("ADMIN_PASSWORD", "admin123"))

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
    try:
        # Sort posts by timestamp (newest first) - using in-memory storage for now
        sorted_jobs = sorted(job_posts.items(), key=lambda x: x[1]['timestamp'], reverse=True)
        sorted_intros = sorted(intro_posts.items(), key=lambda x: x[1]['timestamp'], reverse=True)
        sorted_notices = sorted(notice_posts.items(), key=lambda x: x[1]['timestamp'], reverse=True)
        sorted_forums = sorted(forum_posts.items(), key=lambda x: x[1]['timestamp'], reverse=True)
        
        return render_template('index.html', 
                             job_posts=sorted_jobs, 
                             intro_posts=sorted_intros,
                             notice_posts=sorted_notices,
                             forum_posts=sorted_forums)
    except Exception as e:
        logging.error(f"Error in index route: {e}")
        # Return a simple response for health checks
        return "Korean Job Community Platform - Health Check OK", 200

@app.route('/health')
def health_check():
    """Simple health check endpoint for deployment"""
    return "OK", 200

@app.route('/job/new', methods=['GET', 'POST'])
def job_new():
    """Page for companies to create new job postings"""
    if request.method == 'POST':
        global job_counter
        job_counter += 1
        
        job_data = {
            'id': job_counter,
            'title': sanitize_input(request.form.get('title', '')),
            'company': sanitize_input(request.form.get('company', '')),
            'contact': sanitize_input(request.form.get('contact', '')),
            'description': sanitize_input(request.form.get('description', '')),
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
            'name': sanitize_input(request.form.get('name', '')),
            'nationality': sanitize_input(request.form.get('nationality', '')),
            'languages': sanitize_input(request.form.get('languages', '')),
            'youtube_link': sanitize_input(request.form.get('youtube_link', '')),
            'introduction': sanitize_input(request.form.get('introduction', '')),
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
    conn = get_db_connection()
    if not conn:
        flash('데이터베이스 연결 오류가 발생했습니다.', 'error')
        return render_template('notice_list.html', notice_posts=[])
    
    try:
        with conn.cursor() as cur:
            cur.execute('SELECT * FROM notices ORDER BY created_at DESC')
            notices = cur.fetchall()
            # Convert to tuple format for template compatibility
            notice_posts = [(notice['id'], notice) for notice in notices]
            return render_template('notice_list.html', notice_posts=notice_posts)
    except Exception as e:
        logging.error(f"Error fetching notices: {e}")
        flash('공지사항을 불러오는 중 오류가 발생했습니다.', 'error')
        return render_template('notice_list.html', notice_posts=[])
    finally:
        conn.close()

@app.route('/notice/new', methods=['GET', 'POST'])
def notice_new():
    """Page to create new notices - requires admin login"""
    # Check if user is logged in and is admin
    if not session.get('user_id'):
        flash('로그인이 필요합니다.', 'error')
        return redirect(url_for('login'))
    
    if session.get('role') != 'admin':
        flash('공지사항 작성 권한이 없습니다. 관리자만 작성 가능합니다.', 'error')
        return redirect(url_for('notice_list'))
    
    if request.method == 'POST':
        title = sanitize_input(request.form.get('title', ''))
        content = sanitize_input(request.form.get('content', ''))
        
        if not all([title, content]):
            flash('모든 필드를 입력해주세요.', 'error')
            return render_template('notice_new.html')
        
        conn = get_db_connection()
        if not conn:
            flash('데이터베이스 연결 오류가 발생했습니다.', 'error')
            return render_template('notice_new.html')
        
        try:
            with conn.cursor() as cur:
                cur.execute('INSERT INTO notices (title, content) VALUES (%s, %s) RETURNING id', 
                           (title, content))
                notice_id = cur.fetchone()['id']
                conn.commit()
                
                flash('공지사항이 성공적으로 등록되었습니다.', 'success')
                return redirect(url_for('notice_view', notice_id=notice_id))
                
        except Exception as e:
            logging.error(f"Error creating notice: {e}")
            flash('공지사항 등록 중 오류가 발생했습니다.', 'error')
            return render_template('notice_new.html')
        finally:
            conn.close()
    
    return render_template('notice_new.html')

@app.route('/notice/<int:notice_id>')
def notice_view(notice_id):
    """Page to view a specific notice"""
    conn = get_db_connection()
    if not conn:
        flash('데이터베이스 연결 오류가 발생했습니다.', 'error')
        return redirect(url_for('notice_list'))
    
    try:
        with conn.cursor() as cur:
            cur.execute('SELECT * FROM notices WHERE id = %s', (notice_id,))
            notice = cur.fetchone()
            
            if not notice:
                flash('존재하지 않는 공지사항입니다.', 'error')
                return redirect(url_for('notice_list'))
                
            return render_template('notice_view.html', notice=notice)
    except Exception as e:
        logging.error(f"Error fetching notice {notice_id}: {e}")
        flash('공지사항을 불러오는 중 오류가 발생했습니다.', 'error')
        return redirect(url_for('notice_list'))
    finally:
        conn.close()

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
            'author': sanitize_input(request.form.get('author', '')),
            'title': sanitize_input(request.form.get('title', '')),
            'content': sanitize_input(request.form.get('content', '')),
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
    if not conn:
        return None
    
    try:
        with conn.cursor() as cur:
            cur.execute('SELECT * FROM users WHERE id = %s', (session['user_id'],))
            user = cur.fetchone()
        return user
    except Exception as e:
        logging.error(f"Error getting current user: {e}")
        return None
    finally:
        conn.close()

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
        username = sanitize_input(request.form.get('username', ''))
        email = sanitize_input(request.form.get('email', ''))
        password = request.form.get('password', '')  # Don't sanitize passwords
        confirm_password = request.form.get('confirm_password', '')
        terms_agreed = request.form.get('terms_agreed') == 'on'
        
        # Basic validation
        if not username or not email or not password:
            flash('모든 필수 항목을 입력해주세요.', 'error')
            return render_template('register.html')
        
        if not terms_agreed:
            flash('이용약관에 동의해주세요.', 'error')
            return render_template('register.html')
        
        # Username validation
        if len(username) < 3:
            flash('사용자명은 3글자 이상이어야 합니다.', 'error')
            return render_template('register.html')
        
        if len(username) > 20:
            flash('사용자명은 20글자 이하여야 합니다.', 'error')
            return render_template('register.html')
        
        # Email validation
        if not is_valid_email(email):
            flash('올바른 이메일 주소를 입력해주세요.', 'error')
            return render_template('register.html')
        
        # Password validation
        if len(password) < 8:
            flash('비밀번호는 8글자 이상이어야 합니다.', 'error')
            return render_template('register.html')
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            flash('비밀번호에는 최소 1개의 특수문자가 포함되어야 합니다.', 'error')
            return render_template('register.html')
        
        if not re.search(r'\d', password):
            flash('비밀번호에는 최소 1개의 숫자가 포함되어야 합니다.', 'error')
            return render_template('register.html')
        
        if not re.search(r'[a-zA-Z]', password):
            flash('비밀번호에는 최소 1개의 영문자가 포함되어야 합니다.', 'error')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('비밀번호가 일치하지 않습니다.', 'error')
            return render_template('register.html')
        
        # Check if username or email already exists
        conn = get_db_connection()
        if not conn:
            flash('데이터베이스 연결 오류가 발생했습니다.', 'error')
            return render_template('register.html')
        
        try:
            with conn.cursor() as cur:
                cur.execute('SELECT id FROM users WHERE username = %s OR email = %s', (username, email))
                existing_user = cur.fetchone()
                
                if existing_user:
                    cur.execute('SELECT id FROM users WHERE username = %s', (username,))
                    existing_username = cur.fetchone()
                    cur.execute('SELECT id FROM users WHERE email = %s', (email,))
                    existing_email = cur.fetchone()
                    
                    if existing_username:
                        flash('이미 사용 중인 사용자명입니다.', 'error')
                    if existing_email:
                        flash('이미 사용 중인 이메일 주소입니다.', 'error')
                    return render_template('register.html')
                
                # Create new user
                hashed_password = generate_password_hash(password)
                cur.execute('INSERT INTO users (username, email, password) VALUES (%s, %s, %s)', 
                           (username, email, hashed_password))
                conn.commit()
                
                flash('회원가입이 완료되었습니다. 로그인해주세요.', 'success')
                return redirect(url_for('login'))
                
        except Exception as e:
            logging.error(f"Error during registration: {e}")
            flash('회원가입 중 오류가 발생했습니다.', 'error')
            return render_template('register.html')
        finally:
            conn.close()
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login_id = sanitize_input(request.form.get('username', ''))  # Can be username or email
        password = request.form.get('password', '')
        
        if not login_id or not password:
            flash('아이디와 비밀번호를 모두 입력해주세요.', 'error')
            return render_template('login.html')
        
        conn = get_db_connection()
        if not conn:
            flash('데이터베이스 연결 오류가 발생했습니다.', 'error')
            return render_template('login.html')
        
        try:
            with conn.cursor() as cur:
                # Try to find user by username or email
                cur.execute('SELECT * FROM users WHERE username = %s OR email = %s', (login_id, login_id))
                user = cur.fetchone()
        except Exception as e:
            logging.error(f"Error during login: {e}")
            flash('로그인 중 오류가 발생했습니다.', 'error')
            return render_template('login.html')
        finally:
            conn.close()
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['email'] = user['email']
            session['role'] = user.get('role', 'user')  # Default to 'user' if role is not set
            flash(f'{user["username"]}님 환영합니다!', 'success')
            
            # Redirect to intended page or home
            next_page = request.args.get('next')
            if next_page:
                # Validate redirect URL to prevent open redirect attacks
                from urllib.parse import urlparse
                parsed_url = urlparse(next_page)
                # Only allow relative URLs (no netloc) or URLs from the same domain
                if not parsed_url.netloc or parsed_url.netloc == request.host:
                    return redirect(next_page)
            return redirect(url_for('index'))
        else:
            flash('아이디 또는 비밀번호가 올바르지 않습니다.', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    username = session.get('username', '')
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('email', None)
    session.pop('role', None)
    if username:
        flash(f'{username}님 로그아웃되었습니다.', 'success')
    return redirect(url_for('index'))

# Admin routes
@app.route('/admin/login', methods=['GET', 'POST'])
@csrf.exempt  # Disable CSRF for admin login to avoid issues
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        print(f"DEBUG: Admin login attempt - username: '{username}', password: '{password}'")
        print(f"DEBUG: Form data: {dict(request.form)}")
        
        if not username or not password:
            flash('아이디와 비밀번호를 모두 입력해주세요.', 'error')
            return render_template('admin_login.html')
        
        # Test both direct check and database check
        admin_success = False
        
        # Direct hardcoded check
        if username == 'admin' and password == 'admin':
            admin_success = True
            print(f"DEBUG: Direct admin check passed")
        
        # Database check as backup
        if not admin_success:
            conn = get_db_connection()
            if conn:
                try:
                    with conn.cursor() as cur:
                        cur.execute('SELECT * FROM users WHERE username = %s AND role = %s', 
                                   (username, 'admin'))
                        user = cur.fetchone()
                        if user and check_password_hash(user['password'], password):
                            admin_success = True
                            print(f"DEBUG: Database admin check passed")
                except Exception as e:
                    print(f"DEBUG: Database check failed: {e}")
                finally:
                    conn.close()
        
        if admin_success:
            # Clear any existing session data
            session.clear()
            # Set session with explicit values
            session.permanent = True
            session['admin_logged_in'] = True
            session['admin_user_id'] = 1
            session['admin_username'] = 'admin'
            print(f"DEBUG: Admin login successful, session keys: {list(session.keys())}")
            flash('관리자로 로그인되었습니다.', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            print(f"DEBUG: All admin checks failed - username: '{username}', password: '{password}'")
            flash('잘못된 관리자 정보입니다.', 'error')
    
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    session.pop('admin_user_id', None)
    session.pop('admin_username', None)
    flash('관리자 로그아웃되었습니다.', 'success')
    return redirect(url_for('index'))

@app.route('/admin')
def admin_dashboard():
    print(f"DEBUG: Admin dashboard access attempt, session: {dict(session)}")
    auth_check = require_admin()
    if auth_check:
        print(f"DEBUG: Admin auth check failed, redirecting")
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

# Reaction routes
@app.route('/react/<string:post_type>/<int:post_id>', methods=['GET', 'POST'])
def add_reaction(post_type, post_id):
    if request.method == 'GET':
        # Return current reaction data for the post
        reactions = get_post_reactions(post_type, post_id)
        return jsonify({'success': True, 'reactions': reactions})
    
    if not is_logged_in():
        return jsonify({'success': False, 'message': '로그인이 필요합니다.'}), 401
    
    data = request.get_json()
    emoji = data.get('emoji') if data else None
    user_id = session['user_id']
    
    if not emoji:
        return jsonify({'success': False, 'message': '이모지를 선택해주세요.'}), 400
    
    conn = get_db_connection()
    
    try:
        if post_type == 'job':
            # Check if job exists
            job = conn.execute('SELECT id FROM jobs WHERE id = ?', (post_id,)).fetchone()
            if not job:
                return jsonify({'success': False, 'message': '존재하지 않는 게시글입니다.'}), 404
            
            # Remove existing reaction from this user for this job and emoji
            conn.execute('DELETE FROM job_reactions WHERE job_id = ? AND user_id = ? AND emoji = ?', 
                        (post_id, user_id, emoji))
            
            # Add new reaction
            conn.execute('INSERT INTO job_reactions (job_id, user_id, emoji) VALUES (?, ?, ?)', 
                        (post_id, user_id, emoji))
            
        elif post_type == 'intro':
            # Check if intro exists
            intro = conn.execute('SELECT id FROM introductions WHERE id = ?', (post_id,)).fetchone()
            if not intro:
                return jsonify({'success': False, 'message': '존재하지 않는 게시글입니다.'}), 404
            
            # Remove existing reaction from this user for this intro and emoji
            conn.execute('DELETE FROM intro_reactions WHERE intro_id = ? AND user_id = ? AND emoji = ?', 
                        (post_id, user_id, emoji))
            
            # Add new reaction
            conn.execute('INSERT INTO intro_reactions (intro_id, user_id, emoji) VALUES (?, ?, ?)', 
                        (post_id, user_id, emoji))
        else:
            return jsonify({'success': False, 'message': '잘못된 게시글 유형입니다.'}), 400
        
        conn.commit()
        
        # Get updated reaction counts
        reactions = get_post_reactions(post_type, post_id)
        
        return jsonify({'success': True, 'reactions': reactions})
        
    except Exception as e:
        return jsonify({'success': False, 'message': '반응 추가 중 오류가 발생했습니다.'}), 500
    finally:
        conn.close()

@app.route('/unreact/<string:post_type>/<int:post_id>', methods=['POST'])
def remove_reaction(post_type, post_id):
    if not is_logged_in():
        return jsonify({'success': False, 'message': '로그인이 필요합니다.'}), 401
    
    data = request.get_json()
    emoji = data.get('emoji') if data else None
    user_id = session['user_id']
    
    if not emoji:
        return jsonify({'success': False, 'message': '이모지를 선택해주세요.'}), 400
    
    conn = get_db_connection()
    
    try:
        if post_type == 'job':
            conn.execute('DELETE FROM job_reactions WHERE job_id = ? AND user_id = ? AND emoji = ?', 
                        (post_id, user_id, emoji))
        elif post_type == 'intro':
            conn.execute('DELETE FROM intro_reactions WHERE intro_id = ? AND user_id = ? AND emoji = ?', 
                        (post_id, user_id, emoji))
        else:
            return jsonify({'success': False, 'message': '잘못된 게시글 유형입니다.'}), 400
        
        conn.commit()
        
        # Get updated reaction counts
        reactions = get_post_reactions(post_type, post_id)
        
        return jsonify({'success': True, 'reactions': reactions})
        
    except Exception as e:
        return jsonify({'success': False, 'message': '반응 제거 중 오류가 발생했습니다.'}), 500
    finally:
        conn.close()

def get_post_reactions(post_type, post_id):
    """Get reaction counts and user reactions for a post"""
    conn = get_db_connection()
    
    # Whitelist allowed table and field combinations to prevent SQL injection
    ALLOWED_REACTIONS = {
        'job': {'table': 'job_reactions', 'id_field': 'job_id'},
        'intro': {'table': 'intro_reactions', 'id_field': 'intro_id'}
    }
    
    if post_type not in ALLOWED_REACTIONS:
        return {}
    
    table = ALLOWED_REACTIONS[post_type]['table']
    id_field = ALLOWED_REACTIONS[post_type]['id_field']
    
    # Get reaction counts grouped by emoji
    reaction_counts = conn.execute(f'''
        SELECT emoji, COUNT(*) as count 
        FROM {table} 
        WHERE {id_field} = ? 
        GROUP BY emoji
    ''', (post_id,)).fetchall()
    
    # Get current user's reactions if logged in
    user_reactions = []
    if is_logged_in():
        user_reactions_result = conn.execute(f'''
            SELECT emoji 
            FROM {table} 
            WHERE {id_field} = ? AND user_id = ?
        ''', (post_id, session['user_id'])).fetchall()
        user_reactions = [row['emoji'] for row in user_reactions_result]
    
    conn.close()
    
    reactions = {}
    for row in reaction_counts:
        reactions[row['emoji']] = {
            'count': row['count'],
            'user_reacted': row['emoji'] in user_reactions
        }
    
    return reactions

@app.template_filter('get_reactions')
def get_reactions_filter(post_type, post_id):
    """Template filter to get reactions for a post"""
    return get_post_reactions(post_type, post_id)

def get_db_connection():
    try:
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            raise Exception("DATABASE_URL environment variable not set")
        
        conn = psycopg2.connect(database_url, cursor_factory=psycopg2.extras.RealDictCursor)
        return conn
    except Exception as e:
        logging.error(f"Database connection failed: {e}")
        return None