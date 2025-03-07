import random
from datetime import datetime
from .data import HANJA_DATA, ELEMENT_RELATIONS, GENDER_PROPERTIES, STROKE_FORTUNE, HANJA_STROKES

def calculate_stroke_fortune(strokes):
    """획수의 길흉을 판단합니다."""
    return STROKE_FORTUNE.get(strokes % 20, '길')

def is_compatible_elements(element1, element2):
    """두 오행의 상성을 확인합니다."""
    if element1 == element2:
        return True
    return ELEMENT_RELATIONS[element1]['생'] == element2

def get_compatible_chars(gender, first_char=None):
    """성별과 첫 글자에 맞는 한자를 찾습니다."""
    gender_props = GENDER_PROPERTIES[gender]
    preferred_elements = gender_props['preferred_elements']
    preferred_yinyang = gender_props['preferred_yinyang']
    
    compatible_chars = []
    
    for char, data in HANJA_DATA.items():
        # 첫 글자가 있는 경우 오행 상성 검사
        if first_char and not is_compatible_elements(
            HANJA_DATA[first_char]['element'],
            data['element']
        ):
            continue
            
        # 성별에 따른 선호 요소 검사
        if (data['element'] in preferred_elements or
            data['yinyang'] == preferred_yinyang):
            compatible_chars.append(char)
    
    return compatible_chars

def generate_name(data):
    """
    이름을 생성하는 함수
    
    Args:
        data (dict): 사용자 입력 데이터
            - family_name (str): 성씨
            - gender (str): 성별
            - birth_date (str): 생년월일
    
    Returns:
        dict: 생성된 이름과 관련 정보
    """
    gender = data['gender']
    birth_date = datetime.strptime(data['birth_date'], '%Y-%m-%d')
    
    # 이름 생성 (2글자)
    names = []
    for _ in range(3):  # 3개의 이름 조합을 생성
        # 첫 번째 글자 선택
        first_chars = get_compatible_chars(gender)
        first_char = random.choice(first_chars)
        
        # 두 번째 글자 선택
        second_chars = get_compatible_chars(gender, first_char)
        second_char = random.choice(second_chars)
        
        # 획수 계산
        name_strokes = (
            HANJA_STROKES[HANJA_DATA[first_char]['hanja']] +
            HANJA_STROKES[HANJA_DATA[second_char]['hanja']]
        )
        
        # 이름 정보 생성
        name_info = {
            'name': first_char + second_char,
            'hanja': HANJA_DATA[first_char]['hanja'] + HANJA_DATA[second_char]['hanja'],
            'meaning': f"{HANJA_DATA[first_char]['meaning']}, {HANJA_DATA[second_char]['meaning']}",
            'analysis': {
                'yinyang': f"{HANJA_DATA[first_char]['yinyang']}/{HANJA_DATA[second_char]['yinyang']}",
                'elements': f"{HANJA_DATA[first_char]['element']}/{HANJA_DATA[second_char]['element']}",
                'strokes': name_strokes
            }
        }
        names.append(name_info)
    
    return {
        'names': names,
        'birth_year': birth_date.year,
        'compatibility': calculate_stroke_fortune(names[0]['analysis']['strokes'])
    } 