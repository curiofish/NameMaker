from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash, send_file
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
from model.database import init_db, create_user, authenticate_user, save_name, get_user_names, get_name_by_id
from model.name_generator import generate_name
from model.pdf_generator import create_name_report
from functools import wraps
import time
from fpdf import FPDF
import io

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))  # 환경 변수에서 시크릿 키 가져오기
app.permanent_session_lifetime = timedelta(days=1)  # 세션 유효 기간 설정

# 데이터베이스 경로 설정
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'namemaker.db')

# 데이터베이스 초기화
init_db(db_path)

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
            if create_user(username, password, email):
                flash('회원가입이 완료되었습니다. 로그인해주세요.', 'success')
                return redirect(url_for('login'))
            else:
                flash('이미 존재하는 사용자명입니다.', 'error')
        except Exception as e:
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
        
        user = authenticate_user(username, password)
        if user:
            session.permanent = True  # 세션 영구 저장
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['login_time'] = datetime.now().isoformat()
            flash('로그인되었습니다.', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('아이디 또는 비밀번호가 올바르지 않습니다.', 'error')
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
@login_required
def generate():
    """이름 생성"""
    if request.method == 'POST':
        family_name = request.form.get('family_name')
        gender = request.form.get('gender')
        birth_year = request.form.get('birth_year')
        num_names = request.form.get('num_names', '5')
        
        # 입력값 검증
        if not family_name or not gender or not birth_year:
            flash('모든 필드를 입력해주세요.', 'error')
            return redirect(url_for('generate'))
        
        try:
            birth_year = int(birth_year)
            if birth_year < 1900 or birth_year > 2100:
                flash('올바른 출생년도를 입력해주세요.', 'error')
                return redirect(url_for('generate'))
        except ValueError:
            flash('올바른 출생년도를 입력해주세요.', 'error')
            return redirect(url_for('generate'))
        
        try:
            num_names = int(num_names)
            if num_names not in [3, 5, 10]:
                flash('올바른 이름 개수를 선택해주세요.', 'error')
                return redirect(url_for('generate'))
        except ValueError:
            flash('올바른 이름 개수를 선택해주세요.', 'error')
            return redirect(url_for('generate'))
        
        try:
            names = generate_name(family_name, gender, birth_year, num_names)
            return render_template('generate.html', names=names)
        except Exception as e:
            flash('이름 생성 중 오류가 발생했습니다.', 'error')
            return redirect(url_for('generate'))
    
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