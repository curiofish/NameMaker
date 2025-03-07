from flask import Blueprint, render_template, request, jsonify
from model.name_generator import generate_name
from model.database import save_name, get_saved_names, init_db

main = Blueprint('main', __name__)

# 데이터베이스 초기화
init_db()

@main.route('/')
def index():
    saved_names = get_saved_names(5)  # 최근 5개의 저장된 이름을 가져옴
    return render_template('index.html', saved_names=saved_names)

@main.route('/generate', methods=['POST'])
def generate():
    data = request.get_json()
    # TODO: 실제 이름 생성 로직 구현
    result = generate_name(data)
    return jsonify(result)

@main.route('/save', methods=['POST'])
def save():
    data = request.get_json()
    try:
        save_name(data['name_data'], data['user_data'])
        return jsonify({'success': True, 'message': '이름이 저장되었습니다.'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@main.route('/saved-names')
def saved_names():
    names = get_saved_names()
    return jsonify(names) 