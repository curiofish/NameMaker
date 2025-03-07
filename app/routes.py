from flask import Blueprint, render_template, request, jsonify
from model.name_generator import generate_name

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/generate', methods=['POST'])
def generate():
    data = request.get_json()
    # TODO: 실제 이름 생성 로직 구현
    result = generate_name(data)
    return jsonify(result) 