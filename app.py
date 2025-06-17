import os
import logging
import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

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
    """Page to create new notices"""
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