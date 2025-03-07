import random
from datetime import datetime
from .hanja_data import (
    get_strokes, get_meaning, get_yinyang_score,
    get_strokes_score, get_name_score
)
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

def generate_name(family_name, gender, birth_year, num_names=5):
    """이름 생성 함수"""
    try:
        logger.info(f"Generating {num_names} names for {family_name}, {gender}, {birth_year}")
        
        # 입력값 검증
        if not family_name or not gender or not birth_year:
            raise ValueError("모든 필드를 입력해주세요.")
            
        if not isinstance(birth_year, int) or birth_year < 1900 or birth_year > 2100:
            raise ValueError("올바른 출생년도를 입력해주세요.")
            
        if gender not in ['남', '여']:
            raise ValueError("올바른 성별을 선택해주세요.")
            
        # 샘플 이름 목록
        male_names = ['준서', '현우', '민준', '서준', '도윤', '시우', '지호', '예준', '주원', '승우']
        female_names = ['서연', '지우', '서현', '민서', '하은', '하윤', '윤서', '지민', '채원', '수아']
        
        # 성별에 따른 이름 선택
        name_list = male_names if gender == '남' else female_names
        
        # 결과 저장
        results = []
        for _ in range(num_names):
            name = random.choice(name_list)
            fortune_score = random.randint(70, 100)
            results.append({
                'name': f"{family_name}{name}",
                'hanja': '漢字',  # 실제 한자로 대체 필요
                'meaning': f"{name}의 의미입니다.",
                'analysis': f"{name}의 분석 결과입니다.",
                'score': fortune_score
            })
            
        logger.info(f"Successfully generated {num_names} names")
        return results
        
    except Exception as e:
        logger.error(f"Error generating names: {str(e)}")
        raise 