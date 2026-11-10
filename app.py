import os
import sys
import json
from pathlib import Path
from flask import Flask, render_template, request, jsonify, session, send_from_directory, redirect, url_for
from werkzeug.utils import secure_filename

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from config import (
    SECRET_KEY, DATABASE_PATH, UPLOAD_DIR, REPORTS_DIR, WEIGHTS, THRESHOLDS
)
from database.db_manager import init_db
from modules import (
    security, auth, ingestion, nlp_processor, ml_detector, deep_learning,
    explainable_ai, source_credibility, fact_verification, image_forensics,
    sentiment_clickbait, multilingual, analytics, history, report_generator
)

app = Flask(__name__)
app.secret_key = SECRET_KEY
app.config['UPLOAD_FOLDER'] = str(UPLOAD_DIR)
app.config['REPORTS_FOLDER'] = str(REPORTS_DIR)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Initialize DB on boot
init_db()

# --- WEB PAGE ROUTES ---
@app.route('/')
def index():
    return render_template('index.html', user=session.get('user'))

@app.route('/dashboard')
def dashboard_view():
    return render_template('dashboard.html', user=session.get('user'))

@app.route('/image-verify')
def image_verify_view():
    return render_template('image_verify.html', user=session.get('user'))

@app.route('/history')
def history_view():
    return render_template('history.html', user=session.get('user'))

@app.route('/login')
def login_view():
    return render_template('login.html', user=session.get('user'))

# --- AUTH API ENDPOINTS ---
@app.route('/api/auth/register', methods=['POST'])
def api_register():
    data = request.get_json() or {}
    username = data.get('username', '')
    email = data.get('email', '')
    password = data.get('password', '')
    
    success, msg, user_id = auth.register_user(username, email, password)
    if not success:
        return jsonify({'success': False, 'message': msg}), 400
        
    session['user'] = {'id': user_id, 'username': username, 'email': email}
    return jsonify({'success': True, 'message': msg, 'user': session['user']})

@app.route('/api/auth/login', methods=['POST'])
def api_login():
    data = request.get_json() or {}
    identifier = data.get('username_or_email', '')
    password = data.get('password', '')
    
    success, msg, user_data = auth.authenticate_user(identifier, password)
    if not success:
        return jsonify({'success': False, 'message': msg}), 401
        
    session['user'] = user_data
    return jsonify({'success': True, 'message': msg, 'user': user_data})

@app.route('/api/auth/logout', methods=['POST', 'GET'])
def api_logout():
    session.pop('user', None)
    return redirect(url_for('index'))

@app.route('/api/auth/me')
def api_me():
    return jsonify({'user': session.get('user')})

# --- ANALYSIS API (MODULES 2 to 11, 14, 15) ---
@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    data = request.get_json() or {}
    input_mode = data.get('mode', 'text') # 'text' or 'url'
    raw_text = data.get('text', '').strip()
    title = data.get('title', '').strip()
    url = data.get('url', '').strip()
