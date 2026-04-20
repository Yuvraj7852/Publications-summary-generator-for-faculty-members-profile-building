from flask import (Flask, render_template, request, redirect,
                   url_for, session, flash, send_from_directory, jsonify)
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import os

import database as db
import model as nlp
import utils

# ─────────────────────────────────────────────
# App Setup
# ─────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = 'ai_pub_summary_secret_2024'
app.config['UPLOAD_FOLDER'] = utils.UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB

db.init_db()
os.makedirs(utils.UPLOAD_FOLDER, exist_ok=True)


# ─────────────────────────────────────────────
# Jinja helpers
# ─────────────────────────────────────────────
@app.template_filter('score_badge')
def score_badge_filter(score):
    return utils.score_badge(score or 0)

@app.template_filter('short_date')
def short_date_filter(dt_str):
    if not dt_str:
        return ''
    return str(dt_str)[:10]


# ─────────────────────────────────────────────
# Auth decorators
# ─────────────────────────────────────────────
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def faculty_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in.', 'warning')
            return redirect(url_for('login'))
        if session.get('role') != 'faculty':
            flash('Faculty access required.', 'danger')
            return redirect(url_for('student_dashboard'))
        return f(*args, **kwargs)
    return decorated

def student_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in.', 'warning')
            return redirect(url_for('login'))
        if session.get('role') != 'student':
            flash('Student access required.', 'danger')
            return redirect(url_for('faculty_dashboard'))
        return f(*args, **kwargs)
    return decorated


# ─────────────────────────────────────────────
# Routes — Public
# ─────────────────────────────────────────────
@app.route('/')
def index():
    if 'user_id' in session:
        if session['role'] == 'faculty':
            return redirect(url_for('faculty_dashboard'))
        return redirect(url_for('student_dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        email    = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        user = db.get_user_by_email(email)
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['name']    = user['name']
            session['role']    = user['role']
            flash(f"Welcome back, {user['name']}! ", 'success')
            if user['role'] == 'faculty':
                return redirect(url_for('faculty_dashboard'))
            return redirect(url_for('student_dashboard'))

        flash('Invalid email or password. Please try again.', 'danger')

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        name     = request.form.get('name', '').strip()
        email    = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm  = request.form.get('confirm_password', '')
        role     = request.form.get('role', 'student')

        if not all([name, email, password, confirm]):
            flash('All fields are required.', 'danger')
        elif password != confirm:
            flash('Passwords do not match.', 'danger')
        elif len(password) < 6:
            flash('Password must be at least 6 characters.', 'danger')
        elif role not in ('faculty', 'student'):
            flash('Invalid role selected.', 'danger')
        else:
            hashed = generate_password_hash(password)
            user_id = db.add_user(name, email, hashed, role)
            if user_id:
                flash('Account created successfully! Please log in.', 'success')
                return redirect(url_for('login'))
            else:
                flash('Email already registered. Please use a different email.', 'danger')

    return render_template('register.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


# ─────────────────────────────────────────────
# Routes — Faculty
# ─────────────────────────────────────────────
@app.route('/faculty/dashboard')
@faculty_required
def faculty_dashboard():
    papers = db.get_papers_by_faculty(session['user_id'])
    stats  = db.get_faculty_stats(session['user_id'])
    exp    = utils.get_experience_level(
        stats['total_papers'] or 0,
        stats['avg_score']
    )
    return render_template('faculty_dashboard.html',
                           papers=papers,
                           stats=stats,
                           experience=exp)


@app.route('/faculty/upload', methods=['GET', 'POST'])
@faculty_required
def upload_paper():
    if request.method == 'POST':
        if 'pdf_file' not in request.files:
            flash('No file selected.', 'danger')
            return redirect(request.url)

        file = request.files['pdf_file']
        if file.filename == '':
            flash('No file selected.', 'danger')
            return redirect(request.url)

        if not utils.allowed_file(file.filename):
            flash('Only PDF files are allowed.', 'danger')
            return redirect(request.url)

        # Save file
        filename, full_path = utils.save_uploaded_file(file)

        # Extract text
        text = utils.extract_text_from_pdf(full_path)
        if not text:
            flash('Could not extract text from the PDF. Please ensure it is not scanned/image-only.', 'warning')
            text = "(Text extraction failed)"

        # Get or derive title
        custom_title = request.form.get('title', '').strip()
        title = custom_title if custom_title else utils.extract_title_from_text(text)

        # AI processing
        summary  = nlp.generate_summary(text)
        score    = nlp.calculate_score(text)
        keywords = nlp.extract_keywords(text)

        # Save to DB
        paper_id = db.add_paper(
            faculty_id=session['user_id'],
            title=title,
            summary=summary,
            score=score,
            keywords=keywords,
            file_path=filename
        )

        flash('Paper uploaded and analyzed successfully! 🎉', 'success')
        return redirect(url_for('result_page', paper_id=paper_id))

    return render_template('upload.html')


@app.route('/faculty/result/<int:paper_id>')
@login_required
def result_page(paper_id):
    paper = db.get_paper_by_id(paper_id)
    if not paper:
        flash('Paper not found.', 'danger')
        return redirect(url_for('index'))

    # Students can view any paper; faculty can only view their own
    if session['role'] == 'faculty' and paper['faculty_id'] != session['user_id']:
        flash('Access denied.', 'danger')
        return redirect(url_for('faculty_dashboard'))

    badge = utils.score_badge(paper['score'] or 0)
    return render_template('result.html', paper=paper, badge=badge)


@app.route('/faculty/papers')
@faculty_required
def view_faculty_papers():
    papers = db.get_papers_by_faculty(session['user_id'])
    return render_template('view_papers.html', papers=papers, view_mode='faculty')


@app.route('/uploads/<filename>')
@login_required
def serve_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


# ─────────────────────────────────────────────
# Routes — Student
# ─────────────────────────────────────────────
@app.route('/student/dashboard')
@student_required
def student_dashboard():
    search = request.args.get('q', '').strip().lower()
    papers = db.get_all_papers()

    if search:
        papers = [
            p for p in papers
            if search in p['title'].lower()
            or search in (p['summary'] or '').lower()
            or search in (p['keywords'] or '').lower()
            or search in p['faculty_name'].lower()
        ]

    return render_template('student.html', papers=papers, search=search)


# ─────────────────────────────────────────────
# API Endpoints (JSON)
# ─────────────────────────────────────────────
@app.route('/api/papers')
@login_required
def api_papers():
    if session['role'] == 'faculty':
        papers = db.get_papers_by_faculty(session['user_id'])
    else:
        papers = db.get_all_papers()
    return jsonify([dict(p) for p in papers])


@app.route('/api/paper/<int:paper_id>')
@login_required
def api_paper(paper_id):
    paper = db.get_paper_by_id(paper_id)
    if not paper:
        return jsonify({'error': 'Not found'}), 404
    return jsonify(dict(paper))


# ─────────────────────────────────────────────
# Error handlers
# ─────────────────────────────────────────────
@app.errorhandler(404)
def not_found(e):
    return render_template('login.html'), 404

@app.errorhandler(413)
def too_large(e):
    flash('File too large. Maximum size is 16 MB.', 'danger')
    return redirect(url_for('upload_paper'))


# ─────────────────────────────────────────────
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
