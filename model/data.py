# 한자 데이터
HANJA_DATA = {
    '길': {'hanja': '吉', 'meaning': '길하다, 상서롭다', 'yinyang': '양', 'element': '목'},
    '동': {'hanja': '東', 'meaning': '동쪽', 'yinyang': '양', 'element': '목'},
    '해': {'hanja': '海', 'meaning': '바다', 'yinyang': '음', 'element': '수'},
    '산': {'hanja': '山', 'meaning': '산', 'yinyang': '양', 'element': '토'},
    '강': {'hanja': '康', 'meaning': '편안하다', 'yinyang': '양', 'element': '수'},
    '민': {'hanja': '民', 'meaning': '백성', 'yinyang': '음', 'element': '토'},
    '준': {'hanja': '俊', 'meaning': '뛰어나다', 'yinyang': '양', 'element': '인'},
    '서': {'hanja': '瑞', 'meaning': '상서롭다', 'yinyang': '양', 'element': '금'},
    '현': {'hanja': '賢', 'meaning': '현명하다', 'yinyang': '양', 'element': '금'},
    '지': {'hanja': '智', 'meaning': '지혜롭다', 'yinyang': '양', 'element': '화'},
    '우': {'hanja': '宇', 'meaning': '우주', 'yinyang': '음', 'element': '토'},
    '진': {'hanja': '眞', 'meaning': '참되다', 'yinyang': '양', 'element': '금'},
}

# 음양오행 상생 관계
ELEMENT_RELATIONS = {
    '목': {'생': '화', '극': '토'},
    '화': {'생': '토', '극': '금'},
    '토': {'생': '금', '극': '수'},
    '금': {'생': '수', '극': '목'},
    '수': {'생': '목', '극': '화'}
}

# 성별에 따른 이름 특성
GENDER_PROPERTIES = {
    'male': {
        'preferred_elements': ['화', '목'],
        'preferred_yinyang': '양'
    },
    'female': {
        'preferred_elements': ['금', '수'],
        'preferred_yinyang': '음'
    }
}

# 획수 길흉 판단
STROKE_FORTUNE = {
    1: '길', 2: '흉', 3: '길', 4: '흉', 5: '길',
    6: '흉', 7: '길', 8: '흉', 9: '길', 10: '길',
    11: '길', 12: '흉', 13: '길', 14: '흉', 15: '길',
    16: '흉', 17: '길', 18: '길', 19: '길', 20: '흉'
}

# 한자 획수
HANJA_STROKES = {
    '吉': 6, '東': 8, '海': 9, '山': 3, '康': 11,
    '民': 5, '俊': 9, '瑞': 13, '賢': 16, '智': 12,
    '宇': 5, '眞': 10
} 