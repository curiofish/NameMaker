from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash, send_file
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
import sys
from model.database import init_db, create_user, authenticate_user, save_name, get_user_names, get_name_by_id
from model.name_generator import generate_name
from functools import wraps
import time
from fpdf import FPDF
import io
import sqlite3
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))  # 환경 변수에서 시크릿 키 가져오기
app.permanent_session_lifetime = timedelta(days=1)  # 세션 유효 기간 설정

# Set database path for different environments
if os.environ.get('HEROKU'):
    db_path = os.path.join('/tmp', 'namemaker.db')
else:
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'namemaker.db')

def get_db():
    """데이터베이스 연결을 반환하는 함수"""
    try:
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        app.logger.error(f"Database connection error: {str(e)}")
        return None

def init_db():
    """데이터베이스 초기화 함수"""
    try:
        # Ensure the database directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        conn = get_db()
        if conn is None:
            app.logger.error("Could not initialize database: connection failed")
            return False
            
        c = conn.cursor()
        
        # Drop existing tables if they exist
        c.execute("DROP TABLE IF EXISTS names")
        c.execute("DROP TABLE IF EXISTS users")
        
        # Create users table
        c.execute('''CREATE TABLE IF NOT EXISTS users
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     username TEXT UNIQUE NOT NULL,
                     password TEXT NOT NULL,
                     email TEXT NOT NULL,
                     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        
        app.logger.info("Users table created successfully")
                     
        # Create names table
        c.execute('''CREATE TABLE IF NOT EXISTS names
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     user_id INTEGER,
                     name TEXT NOT NULL,
                     hanja TEXT NOT NULL,
                     meaning TEXT NOT NULL,
                     analysis TEXT NOT NULL,
                     score REAL NOT NULL,
                     gender TEXT NOT NULL,
                     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                     FOREIGN KEY (user_id) REFERENCES users (id))''')
        
        app.logger.info("Names table created successfully")
        
        # Create indexes
        c.execute('CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)')
        c.execute('CREATE INDEX IF NOT EXISTS idx_names_user_id ON names(user_id)')
        
        conn.commit()
        conn.close()
        app.logger.info("Database initialized successfully")
        return True
    except Exception as e:
        app.logger.error(f"Database initialization error: {str(e)}")
        return False

# Initialize database on startup
if not init_db():
    app.logger.error("Failed to initialize database")
    sys.exit(1)

def login_required(f):
    """로그인이 필요한 라우트를 위한 데코레이터"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('로그인이 필요합니다.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def cache_control(max_age=300):
    """캐시 제어를 위한 데코레이터"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            response = f(*args, **kwargs)
            if isinstance(response, str):
                response = app.make_response(response)
            response.headers['Cache-Control'] = f'public, max-age={max_age}'
            return response
        return decorated_function
    return decorator

@app.route('/')
@cache_control(max_age=3600)  # 1시간 캐시
def index():
    """메인 페이지"""
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """회원가입"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        
        # 입력값 검증
        if not username or not password or not email:
            flash('모든 필드를 입력해주세요.', 'error')
            return redirect(url_for('register'))
        
        if len(username) < 3 or len(username) > 20:
            flash('사용자명은 3~20자 사이여야 합니다.', 'error')
            return redirect(url_for('register'))
        
        if len(password) < 8:
            flash('비밀번호는 8자 이상이어야 합니다.', 'error')
            return redirect(url_for('register'))
        
        if '@' not in email or '.' not in email:
            flash('올바른 이메일 주소를 입력해주세요.', 'error')
            return redirect(url_for('register'))
        
        try:
            if create_user(username, password, email, db_path):
                flash('회원가입이 완료되었습니다. 로그인해주세요.', 'success')
                return redirect(url_for('login'))
            else:
                flash('이미 존재하는 사용자명입니다.', 'error')
        except Exception as e:
            app.logger.error(f"Registration error: {str(e)}")
            flash('회원가입 중 오류가 발생했습니다.', 'error')
        
        return redirect(url_for('register'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """로그인"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # 입력값 검증
        if not username or not password:
            flash('모든 필드를 입력해주세요.', 'error')
            return redirect(url_for('login'))
        
        try:
            user = authenticate_user(username, password, db_path)
            if user:
                session.permanent = True  # 세션 영구 저장
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['login_time'] = datetime.now().isoformat()
                flash('로그인되었습니다.', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('아이디 또는 비밀번호가 올바르지 않습니다.', 'error')
        except Exception as e:
            app.logger.error(f"Login error: {str(e)}")
            flash('로그인 중 오류가 발생했습니다.', 'error')
            
        return redirect(url_for('login'))
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """로그아웃"""
    session.clear()
    flash('로그아웃되었습니다.', 'success')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
@cache_control(max_age=60)  # 1분 캐시
def dashboard():
    """대시보드"""
    user_names = get_user_names(session['user_id'])
    return render_template('dashboard.html', names=user_names)

@app.route('/generate', methods=['GET', 'POST'])
def generate():
    """이름 생성"""
    try:
        if request.method == 'POST':
            # 입력값 검증
            family_name = request.form.get('family_name', '')
            gender = request.form.get('gender', '')
            birth_year = request.form.get('birth_year', '')
            
            if not all([family_name, gender, birth_year]):
                flash('모든 필드를 입력해주세요.', 'error')
                return render_template('generate.html')
            
            try:
                birth_year = int(birth_year)
                if birth_year < 1900 or birth_year > 2100:
                    flash('올바른 출생년도를 입력해주세요.', 'error')
                    return render_template('generate.html')
            except ValueError:
                flash('올바른 출생년도를 입력해주세요.', 'error')
                return render_template('generate.html')
            
            if gender not in ['남', '여']:
                flash('올바른 성별을 선택해주세요.', 'error')
                return render_template('generate.html')
            
            # 이름 생성
            names = generate_name(family_name, gender, birth_year, 5)
            return render_template('generate.html', names=names)
    except Exception as e:
        app.logger.error(f"Name generation error: {str(e)}")
        flash('이름 생성 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.', 'error')
        return render_template('generate.html')
    
    return render_template('generate.html')

@app.route('/save_name', methods=['POST'])
@login_required
def save_name_route():
    """이름 저장"""
    try:
        data = request.json
        if not data:
            return jsonify({
                'success': False,
                'message': '올바른 데이터를 전송해주세요.'
            }), 400
        
        # 필수 필드 검증
        required_fields = ['name', 'hanja', 'meaning', 'analysis', 'score']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'필수 필드가 누락되었습니다: {field}'
                }), 400
        
        name_id = save_name(session['user_id'], data)
        
        if name_id:
            return jsonify({
                'success': True,
                'message': '이름이 저장되었습니다.',
                'name_id': name_id
            })
        else:
            return jsonify({
                'success': False,
                'message': '이름 저장에 실패했습니다.'
            }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'오류가 발생했습니다: {str(e)}'
        }), 500

@app.route('/download_report/<int:name_id>')
@login_required
def download_report(name_id):
    """PDF 보고서 다운로드"""
    try:
        name_data = get_name_by_id(name_id, session['user_id'])
        if not name_data:
            flash('해당 이름을 찾을 수 없습니다.', 'error')
            return redirect(url_for('dashboard'))
        
        # Create PDF
        pdf = FPDF()
        pdf.add_page()
        
        # Add Korean font support
        pdf.add_font('NotoSansKR', '', 'static/fonts/NotoSansKR-Regular.ttf', uni=True)
        pdf.set_font('NotoSansKR', '', 16)
        
        # Title
        pdf.cell(0, 10, '이름 분석 리포트', ln=True, align='C')
        pdf.ln(10)
        
        # Name information
        pdf.set_font('NotoSansKR', '', 12)
        pdf.cell(0, 10, f'생성된 이름: {name_data["name"]}', ln=True)
        pdf.cell(0, 10, f'성별: {name_data["gender"]}', ln=True)
        pdf.cell(0, 10, f'생년월일: {name_data["birth_date"]}', ln=True)
        pdf.cell(0, 10, f'행운 점수: {name_data["fortune_score"]}', ln=True)
        pdf.ln(10)
        
        # Meaning
        pdf.set_font('NotoSansKR', '', 10)
        pdf.multi_cell(0, 10, f'이름의 의미:\n{name_data["meaning"]}')
        pdf.ln(10)
        
        # Analysis
        pdf.multi_cell(0, 10, f'이름 분석:\n{name_data["analysis"]}')
        
        # Save to memory
        pdf_bytes = pdf.output(dest='S').encode('latin1')
        
        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'name_report_{name_data["name"]}.pdf'
        )
    except Exception as e:
        flash('보고서 생성 중 오류가 발생했습니다.', 'error')
        return redirect(url_for('dashboard'))

@app.before_request
def before_request():
    """요청 처리 전 실행"""
    session.permanent = True
    app.permanent_session_lifetime = timedelta(days=1)

@app.after_request
def after_request(response):
    """응답 처리 후 실행"""
    # 응답 헤더에 보안 관련 설정 추가
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response

if __name__ == '__main__':
    # 필요한 디렉토리 생성
    os.makedirs('static/reports', exist_ok=True)
    os.makedirs('static/fonts', exist_ok=True)
    
    # 개발 서버 실행
    app.run(host='0.0.0.0', port=5000, debug=True) 