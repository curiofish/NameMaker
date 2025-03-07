import random
from datetime import datetime
from .hanja_data import (
    get_strokes, get_meaning, get_yinyang_score,
    get_strokes_score, get_name_score
)

# 한자 데이터베이스
HANJA_DB = {
    'male': {
        'wood': ['木', '林', '森', '松', '柏', '桂', '桐', '楓', '楠', '樺', '榮', '華', '茂', '植', '樹'],
        'fire': ['火', '炎', '焱', '煜', '煥', '熙', '炫', '燦', '煒', '焱', '日', '陽', '晝', '暉', '曜'],
        'earth': ['土', '地', '坤', '垣', '城', '基', '培', '境', '域', '壤', '山', '岳', '峰', '峻', '崇'],
        'metal': ['金', '銀', '銅', '鐵', '鋼', '銘', '鋒', '銳', '錚', '鏗', '鐘', '鈴', '鈺', '鈞', '鈺'],
        'water': ['水', '河', '海', '湖', '江', '潤', '澤', '淵', '浩', '洋', '泉', '溪', '湖', '海', '洋']
    },
    'female': {
        'wood': ['花', '草', '蓮', '梅', '蘭', '菊', '竹', '芝', '芸', '芳', '枝', '葉', '根', '芽', '苗'],
        'fire': ['光', '明', '晶', '瑩', '燦', '熙', '炫', '煥', '煒', '焱', '曉', '晞', '晢', '晧', '晝'],
        'earth': ['玉', '珠', '珍', '寶', '琳', '瑗', '瑤', '瑾', '瑜', '琪', '崑', '崙', '崢', '崟', '崢'],
        'metal': ['金', '銀', '珠', '玉', '珍', '寶', '琳', '瑗', '瑤', '瑾', '鈺', '鈞', '鈺', '鈞', '鈺'],
        'water': ['雨', '露', '霜', '雪', '冰', '清', '澄', '潤', '澤', '淵', '潮', '汐', '滄', '滌', '滎']
    }
}

# 음양 데이터
YINYANG = {
    'wood': '양',
    'fire': '양',
    'earth': '음',
    'metal': '양',
    'water': '음'
}

# 오행 순서 정의 (목화토금수)
ELEMENTS = ['wood', 'fire', 'earth', 'metal', 'water']

def get_birth_element(birth_year):
    """생년에 따른 오행을 반환합니다."""
    return ELEMENTS[(birth_year - 1900) % 5]

def get_compatible_elements(element):
    """상생 원리에 따른 호환되는 오행을 반환합니다."""
    index = ELEMENTS.index(element)
    return [ELEMENTS[(index + 1) % 5], ELEMENTS[(index + 2) % 5]]

def get_opposing_elements(element):
    """상극 원리에 따른 상극되는 오행을 반환합니다."""
    index = ELEMENTS.index(element)
    # 상극 관계: 목극토, 화극금, 토극수, 금극목, 수극화
    # 목 -> 금, 수
    # 화 -> 수, 목
    # 토 -> 목, 화
    # 금 -> 화, 토
    # 수 -> 토, 금
    opposing_indices = [(index + 3) % 5, (index + 4) % 5]
    return [ELEMENTS[i] for i in opposing_indices]

def calculate_name_score(name_data, birth_element):
    """이름의 종합 점수를 계산합니다."""
    chars = list(name_data['hanja'])
    yinyang_score = get_yinyang_score(chars)
    strokes_score = get_strokes_score(name_data['analysis']['strokes'])
    
    # 오행 조화 점수 계산
    elements = name_data['analysis']['elements'].split(' + ')
    element_score = 100
    for element in elements:
        if element in get_opposing_elements(birth_element):
            element_score -= 20
    
    return (yinyang_score + strokes_score + element_score) / 3

def generate_name(user_data, options=None):
    """사용자 정보를 기반으로 이름을 생성합니다."""
    if options is None:
        options = {}
    
    birth_date = datetime.strptime(user_data['birth_date'], '%Y-%m-%d')
    birth_year = birth_date.year
    gender = user_data['gender']
    family_name = user_data['family_name']
    
    # 생년에 따른 오행
    birth_element = get_birth_element(birth_year)
    
    # 호환되는 오행
    compatible_elements = get_compatible_elements(birth_element)
    
    # 이름 생성
    names = []
    num_names = options.get('num_names', 5)  # 기본값 5개
    
    for _ in range(num_names):
        # 첫 글자 선택 (호환되는 오행 중에서)
        first_element = random.choice(compatible_elements)
        first_char = random.choice(HANJA_DB[gender][first_element])
        
        # 두 번째 글자 선택 (다른 호환되는 오행 중에서)
        second_element = random.choice([e for e in compatible_elements if e != first_element])
        second_char = random.choice(HANJA_DB[gender][second_element])
        
        # 이름 분석
        name = first_char + second_char
        first_strokes = get_strokes(first_char)
        second_strokes = get_strokes(second_char)
        total_strokes = first_strokes + second_strokes
        
        # 한자 의미 조회
        first_meaning = get_meaning(first_char)
        second_meaning = get_meaning(second_char)
        
        # 이름 데이터 생성
        name_data = {
            'name': family_name + name,
            'hanja': name,
            'meaning': f"{first_char}({first_strokes}획, {first_meaning}) {second_char}({second_strokes}획, {second_meaning})",
            'analysis': {
                'yinyang': YINYANG[first_element] + YINYANG[second_element],
                'elements': first_element + ' + ' + second_element,
                'strokes': total_strokes
            }
        }
        
        # 이름 점수 계산
        name_data['score'] = calculate_name_score(name_data, birth_element)
        
        names.append(name_data)
    
    # 점수에 따라 이름 정렬
    names.sort(key=lambda x: x['score'], reverse=True)
    
    return {
        'birth_year': birth_year,
        'birth_element': birth_element,
        'compatibility': '상생(相生)',
        'names': names
    } 