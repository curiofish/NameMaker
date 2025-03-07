from flask import Blueprint, render_template, request, jsonify, send_file, session, redirect, url_for
from model.name_generator import generate_name
from model.database import (
    save_name, get_saved_names, init_db, create_user,
    authenticate_user, get_user_by_id
)
from model.pdf_generator import create_name_report
import os
from functools import wraps

main = Blueprint('main', __name__)

# 데이터베이스 초기화
init_db()

def login_required(f):
    """로그인이 필요한 라우트를 위한 데코레이터"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('main.login'))
        return f(*args, **kwargs)
    return decorated_function

@main.route('/')
def index():
    saved_names = get_saved_names(user_id=session.get('user_id'), limit=5)
    return render_template('index.html', saved_names=saved_names)

@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        if create_user(username, email, password):
            return jsonify({'status': 'success'})
        return jsonify({'status': 'error', 'message': '이미 존재하는 사용자명 또는 이메일입니다.'}), 400
    
    return render_template('register.html')

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        user_id = authenticate_user(username, password)
        if user_id:
            session['user_id'] = user_id
            return jsonify({'status': 'success'})
        return jsonify({'status': 'error', 'message': '잘못된 사용자명 또는 비밀번호입니다.'}), 401
    
    return render_template('login.html')

@main.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('main.index'))

@main.route('/profile')
@login_required
def profile():
    user = get_user_by_id(session['user_id'])
    saved_names = get_saved_names(user_id=session['user_id'])
    return render_template('profile.html', user=user, saved_names=saved_names)

@main.route('/generate', methods=['POST'])
def generate():
    data = request.get_json()
    user_data = {
        'family_name': data.get('family_name'),
        'gender': data.get('gender'),
        'birth_date': data.get('birth_date')
    }
    
    name_data = generate_name(user_data)
    return jsonify(name_data)

@main.route('/save', methods=['POST'])
@login_required
def save():
    try:
        data = request.get_json()
        name_data = data.get('name_data')
        user_data = data.get('user_data')
        
        save_name(name_data, user_data, session['user_id'])
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@main.route('/saved-names')
@login_required
def saved_names():
    names = get_saved_names(user_id=session['user_id'])
    return jsonify(names)

@main.route('/generate-report', methods=['POST'])
@login_required
def generate_report():
    try:
        data = request.get_json()
        name_data = data.get('name_data')
        user_data = data.get('user_data')
        
        filepath = create_name_report(name_data, user_data)
        filename = os.path.basename(filepath)
        
        return send_file(
            filepath,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500 