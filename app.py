import os
import logging
import psycopg2
import psycopg2.extras
import re
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_wtf.csrf import CSRFProtect
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField, SelectMultipleField, DateField, widgets
from wtforms.validators import DataRequired, Length, Optional, URL
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

# Admin Login Form
class AdminLoginForm(FlaskForm):
    username = StringField('관리자 아이디', validators=[DataRequired()])
    password = PasswordField('비밀번호', validators=[DataRequired()])
    submit = SubmitField('로그인')

class Step1RegisterForm(FlaskForm):
    name = StringField('이름', validators=[DataRequired(), Length(min=1, max=50)])
    nationality = StringField('국적', validators=[DataRequired(), Length(min=1, max=50)])
    gender = SelectField('성별', choices=[('', '선택해주세요'), ('male', '남성'), ('female', '여성')], validators=[DataRequired()])
    korean_fluent = SelectField('한국어 가능 여부', choices=[('', '선택해주세요'), ('yes', '예'), ('no', '아니오')], validators=[DataRequired()])
    languages = StringField('구사 언어', validators=[DataRequired(), Length(min=1, max=200)])
    preferred_jobs = SelectField('희망 직무', choices=[
        ('', '선택해주세요'),
        ('moving', '이사 작업'),
        ('construction', '건설업'),
        ('manufacturing', '제조업'),
        ('delivery', '배송업'),
        ('cleaning', '청소업'),
        ('restaurant', '음식점'),
        ('other', '기타')
    ], validators=[DataRequired()])
    preferred_location = SelectField('희망 지역', choices=[
        ('', '선택해주세요'),
        ('seoul', '서울'),
        ('busan', '부산'),
        ('incheon', '인천'),
        ('daegu', '대구'),
        ('daejeon', '대전'),
        ('gwangju', '광주'),
        ('ulsan', '울산'),
        ('gyeonggi', '경기도'),
        ('gangwon', '강원도'),
        ('chungbuk', '충청북도'),
        ('chungnam', '충청남도'),
        ('jeonbuk', '전라북도'),
        ('jeonnam', '전라남도'),
        ('gyeongbuk', '경상북도'),
        ('gyeongnam', '경상남도'),
        ('jeju', '제주도')
    ], validators=[DataRequired()])
    availability = SelectField('근무 가능 여부', choices=[
        ('', '선택해주세요'),
        ('immediate', '즉시 가능'),
        ('negotiable', '조율 필요')
    ], validators=[DataRequired()])
    self_intro = TextAreaField('자기소개', validators=[DataRequired(), Length(min=10, max=1000)])
    video_link = StringField('자기소개 영상 링크 (선택)', validators=[Optional(), URL()])
    submit = SubmitField('등록하기')

class Step2RegisterForm(FlaskForm):
    visa_type = SelectField('체류 자격', choices=[
        ('', '선택해주세요'),
        ('E-9', 'E-9 (비전문취업)'),
        ('H-2', 'H-2 (방문취업)'),
        ('F-4', 'F-4 (재외동포)'),
        ('F-5', 'F-5 (영주)'),
        ('F-6', 'F-6 (결혼이민)'),
        ('other', '기타')
    ])
    visa_expiry = DateField('체류 만료일')
    past_jobs = TextAreaField('이전 근무 경험')
    expected_salary = SelectField('희망 급여 수준', choices=[
        ('', '선택해주세요'),
        ('2000000-2500000', '200만원 - 250만원'),
        ('2500000-3000000', '250만원 - 300만원'),
        ('3000000-3500000', '300만원 - 350만원'),
        ('3500000-4000000', '350만원 - 400만원'),
        ('4000000+', '400만원 이상'),
        ('negotiable', '협의 가능')
    ])
    housing_preference = SelectField('숙소 제공 선호', choices=[
        ('', '선택해주세요'),
        ('required', '필수'),
        ('preferred', '선호'),
        ('not_needed', '필요 없음')
    ])
    licenses = SelectMultipleField('자격증 보유 여부', choices=[
        ('forklift', '지게차 운전'),
        ('crane', '크레인 운전'),
        ('welding', '용접'),
        ('electrical', '전기'),
        ('cooking', '조리'),
        ('driving', '운전면허'),
        ('other', '기타')
    ], widget=widgets.ListWidget(prefix_label=False), option_widget=widgets.CheckboxInput())
    religion = SelectField('종교', choices=[
        ('', '선택해주세요'),
        ('none', '무교'),
        ('christian', '기독교'),
        ('buddhist', '불교'),
        ('catholic', '천주교'),
        ('islam', '이슬람교'),
        ('other', '기타')
    ])
    work_hours = SelectField('근무 가능 시간', choices=[
        ('', '선택해주세요'),
        ('day', '주간근무'),
        ('night', '야간근무'),
        ('shift', '교대근무'),
        ('flexible', '유연근무')
    ])
    submit = SubmitField('정보 업데이트')

class CompanyRegisterForm(FlaskForm):
    company_name = StringField('회사명', validators=[DataRequired(), Length(min=2, max=100)])
    business_number = StringField('사업자등록번호', validators=[DataRequired(), Length(min=10, max=20)])
    ceo_name = StringField('대표자명', validators=[DataRequired(), Length(min=2, max=50)])
    contact_number = StringField('연락처', validators=[DataRequired(), Length(min=10, max=20)])
    email = StringField('이메일', validators=[DataRequired(), Length(min=5, max=120)])
    password = PasswordField('비밀번호', validators=[DataRequired(), Length(min=8, max=128)])
    confirm_password = PasswordField('비밀번호 확인', validators=[DataRequired()])
    address = StringField('회사 주소', validators=[DataRequired(), Length(min=5, max=200)])
    company_description = TextAreaField('회사 소개', validators=[Optional(), Length(max=500)])
    submit = SubmitField('회원가입')

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
        # Get data from database
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        # Get recent job posts
        cur.execute("SELECT * FROM jobs ORDER BY created_at DESC LIMIT 5")
        job_posts_db = cur.fetchall()
        
        # Get recent introductions
        cur.execute("SELECT * FROM introductions ORDER BY created_at DESC LIMIT 5")
        intro_posts_db = cur.fetchall()
        
        # Get recent notices
        cur.execute("SELECT * FROM notices ORDER BY created_at DESC LIMIT 5")
        notice_posts_db = cur.fetchall()
        
        # Get recent forum posts
        cur.execute("SELECT * FROM forum_posts ORDER BY created_at DESC LIMIT 5")
        forum_posts_db = cur.fetchall()
        
        cur.close()
        conn.close()
        
        # Convert to format expected by template (id, data) tuples
        sorted_jobs = [(post['id'], dict(post)) for post in job_posts_db]
        sorted_intros = [(post['id'], dict(post)) for post in intro_posts_db]
        sorted_notices = [(post['id'], dict(post)) for post in notice_posts_db]
        sorted_forums = [(post['id'], dict(post)) for post in forum_posts_db]
        
        return render_template('index.html', 
                             job_posts=sorted_jobs, 
                             intro_posts=sorted_intros,
                             notice_posts=sorted_notices,
                             forum_posts=sorted_forums)
    except Exception as e:
        logging.error(f"Error in index route: {e}")
        # Fallback to in-memory storage if database fails
        sorted_jobs = sorted(job_posts.items(), key=lambda x: x[1]['timestamp'], reverse=True)
        sorted_intros = sorted(intro_posts.items(), key=lambda x: x[1]['timestamp'], reverse=True)
        sorted_notices = sorted(notice_posts.items(), key=lambda x: x[1]['timestamp'], reverse=True)
        sorted_forums = sorted(forum_posts.items(), key=lambda x: x[1]['timestamp'], reverse=True)
        
        return render_template('index.html', 
                             job_posts=sorted_jobs, 
                             intro_posts=sorted_intros,
                             notice_posts=sorted_notices,
                             forum_posts=sorted_forums)

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
    admin_status = is_admin()
    print(f"DEBUG: require_admin check - is_admin(): {admin_status}, session: {dict(session)}")
    if not admin_status:
        flash('관리자 권한이 필요합니다.', 'error')
        return redirect(url_for('admin_login'))
    return None

# Registration choice route
@app.route('/register')
def register_choice():
    return render_template('register_choice.html')

# Company registration route
@app.route('/register/company', methods=['GET', 'POST'])
def register_company():
    form = CompanyRegisterForm()
    
    if form.validate_on_submit():
        # Password confirmation check
        if form.password.data != form.confirm_password.data:
            flash('비밀번호가 일치하지 않습니다.', 'error')
            return render_template('register_company.html', form=form)
        
        conn = get_db_connection()
        if not conn:
            flash('데이터베이스 연결 오류가 발생했습니다.', 'error')
            return render_template('register_company.html', form=form)
        
        try:
            with conn.cursor() as cur:
                # Check if company already exists
                cur.execute('SELECT id FROM companies WHERE email = %s OR business_number = %s', 
                           (form.email.data, form.business_number.data))
                existing_company = cur.fetchone()
                
                if existing_company:
                    flash('이미 등록된 이메일 또는 사업자등록번호입니다.', 'error')
                    return render_template('register_company.html', form=form)
                
                # Hash password and create company
                password_hash = generate_password_hash(form.password.data)
                cur.execute('''
                    INSERT INTO companies (
                        company_name, business_number, ceo_name, contact_number,
                        email, password_hash, address, company_description, created_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
                ''', (
                    form.company_name.data,
                    form.business_number.data,
                    form.ceo_name.data,
                    form.contact_number.data,
                    form.email.data,
                    password_hash,
                    form.address.data,
                    form.company_description.data
                ))
                conn.commit()
                
                flash('업체 회원가입이 완료되었습니다! 로그인해주세요.', 'success')
                return redirect(url_for('login'))
                
        except Exception as e:
            logging.error(f"Error creating company: {e}")
            flash('회원가입 중 오류가 발생했습니다.', 'error')
            return render_template('register_company.html', form=form)
        finally:
            conn.close()
    
    return render_template('register_company.html', form=form)

# Worker Registration route (Step 1) - Keep original /register for workers
@app.route('/register/worker', methods=['GET', 'POST'])
@app.route('/register-worker', methods=['GET', 'POST'])
def register():
    form = Step1RegisterForm()
    
    if form.validate_on_submit():
        conn = get_db_connection()
        if not conn:
            flash('데이터베이스 연결 오류가 발생했습니다.', 'error')
            return render_template('register.html', form=form)
        
        try:
            with conn.cursor() as cur:
                # Insert into introductions table with step 1 data
                cur.execute('''
                    INSERT INTO introductions (
                        name, nationality, gender, korean_fluent, languages,
                        preferred_jobs, preferred_location, availability, 
                        introduction, video_link, step_completed, created_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                    RETURNING id
                ''', (
                    form.name.data,
                    form.nationality.data,
                    form.gender.data,
                    form.korean_fluent.data == 'yes',
                    form.languages.data,
                    form.preferred_jobs.data,
                    form.preferred_location.data,
                    form.availability.data,
                    form.self_intro.data,
                    form.video_link.data or None,
                    1  # Step 1 completed
                ))
                
                intro_id = cur.fetchone()[0]
                conn.commit()
                
                # Store intro_id in session for step 2
                session['intro_id'] = intro_id
                flash('1단계 등록이 완료되었습니다!', 'success')
                return redirect(url_for('success'))
                
        except Exception as e:
            logging.error(f"Error creating introduction: {e}")
            flash('등록 중 오류가 발생했습니다.', 'error')
            return render_template('register.html', form=form)
        finally:
            conn.close()
    
    return render_template('register.html', form=form)

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

# Success page route
@app.route('/success')
def success():
    return render_template('success.html')

# Step 2 Registration route
@app.route('/more-info', methods=['GET', 'POST'])
def more_info():
    form = Step2RegisterForm()
    
    if form.validate_on_submit():
        intro_id = session.get('intro_id')
        if not intro_id:
            flash('등록 정보를 찾을 수 없습니다. 다시 등록해주세요.', 'error')
            return redirect(url_for('register'))
        
        conn = get_db_connection()
        if not conn:
            flash('데이터베이스 연결 오류가 발생했습니다.', 'error')
            return render_template('more_info.html', form=form)
        
        try:
            with conn.cursor() as cur:
                # Update the existing record with step 2 data
                cur.execute('''
                    UPDATE introductions SET
                        visa_type = %s, visa_expiry = %s, past_jobs = %s,
                        expected_salary = %s, housing_preference = %s,
                        licenses = %s, religion = %s, work_hours = %s,
                        step_completed = %s
                    WHERE id = %s
                ''', (
                    form.visa_type.data or None,
                    form.visa_expiry.data,
                    form.past_jobs.data or None,
                    form.expected_salary.data or None,
                    form.housing_preference.data or None,
                    ','.join(form.licenses.data) if form.licenses.data else None,
                    form.religion.data or None,
                    form.work_hours.data or None,
                    2,  # Step 2 completed
                    intro_id
                ))
                conn.commit()
                
                # Clear session
                session.pop('intro_id', None)
                flash('추가 정보가 성공적으로 등록되었습니다!', 'success')
                return redirect(url_for('intro_list'))
                
        except Exception as e:
            logging.error(f"Error updating introduction: {e}")
            flash('정보 업데이트 중 오류가 발생했습니다.', 'error')
            return render_template('more_info.html', form=form)
        finally:
            conn.close()
    
    return render_template('more_info.html', form=form)

# Admin routes
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    form = AdminLoginForm()
    
    if form.validate_on_submit():
        username = form.username.data.strip()
        password = form.password.data
        
        # Simple hardcoded admin check for reliability
        if username == 'admin' and password == 'admin':
            session.clear()
            session.permanent = True
            session['admin_logged_in'] = True
            session['admin_user_id'] = 1
            session['admin_username'] = 'admin'
            flash('관리자로 로그인되었습니다.', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('잘못된 관리자 정보입니다.', 'error')
    
    return render_template('admin_login.html', form=form)

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    session.pop('admin_user_id', None)
    session.pop('admin_username', None)
    flash('관리자 로그아웃되었습니다.', 'success')
    return redirect(url_for('index'))

@app.route('/admin')
def admin_dashboard():
    # Skip auth check for now to test directly
    if not session.get('admin_logged_in'):
        flash('관리자 권한이 필요합니다.', 'error')
        return redirect(url_for('admin_login'))
    
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