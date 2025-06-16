import os
import logging
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

# In-memory data storage
job_posts = {}
intro_posts = {}
job_counter = 0
intro_counter = 0

@app.route('/')
def index():
    """Home page displaying both job postings and self-introductions"""
    # Sort posts by timestamp (newest first)
    sorted_jobs = sorted(job_posts.items(), key=lambda x: x[1]['timestamp'], reverse=True)
    sorted_intros = sorted(intro_posts.items(), key=lambda x: x[1]['timestamp'], reverse=True)
    
    return render_template('index.html', 
                         job_posts=sorted_jobs, 
                         intro_posts=sorted_intros)

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

@app.route('/job/<int:job_id>')
def job_view(job_id):
    """Page to view a specific job posting"""
    if job_id not in job_posts:
        flash('존재하지 않는 구인공고입니다.', 'error')
        return redirect(url_for('index'))
    
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

@app.route('/intro/<int:intro_id>')
def intro_view(intro_id):
    """Page to view a specific self-introduction"""
    if intro_id not in intro_posts:
        flash('존재하지 않는 자기소개입니다.', 'error')
        return redirect(url_for('index'))
    
    intro = intro_posts[intro_id]
    return render_template('intro_view.html', intro=intro)

@app.template_filter('datetime')
def datetime_filter(dt):
    """Format datetime for display"""
    return dt.strftime('%Y년 %m월 %d일 %H:%M')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
