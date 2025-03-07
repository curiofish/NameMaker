import random
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 이름 데이터
NAMES = {
    '남': {
        'first': ['준', '현', '민', '서', '도', '시', '지', '예', '주', '승'],
        'second': ['서', '우', '준', '윤', '호', '원', '민', '준', '현', '영']
    },
    '여': {
        'first': ['서', '지', '민', '하', '윤', '채', '수', '예', '다', '은'],
        'second': ['연', '우', '서', '은', '윤', '원', '민', '아', '인', '지']
    }
}

def generate_name(family_name, gender, birth_year, num_names=5):
    """이름 생성 함수"""
    try:
        # 입력값 검증
        if not isinstance(family_name, str) or len(family_name) == 0:
            raise ValueError("성을 입력해주세요.")
        
        if gender not in ['남', '여']:
            raise ValueError("성별은 '남' 또는 '여'만 가능합니다.")
        
        if not isinstance(birth_year, int) or birth_year < 1900 or birth_year > 2100:
            raise ValueError("출생년도는 1900-2100 사이여야 합니다.")
        
        if not isinstance(num_names, int) or num_names < 1 or num_names > 10:
            raise ValueError("생성할 이름 개수는 1-10 사이여야 합니다.")
        
        # 결과 저장
        results = []
        name_data = NAMES[gender]
        
        # 이름 생성
        for _ in range(num_names):
            first = random.choice(name_data['first'])
            second = random.choice(name_data['second'])
            name = first + second
            
            # 운세 점수 계산 (간단한 버전)
            fortune_score = random.randint(70, 100)
            
            # 결과 추가
            results.append({
                'name': f"{family_name}{name}",
                'hanja': '未定',  # "미정"
                'meaning': f"{first}: 첫번째 글자의 의미\n{second}: 두번째 글자의 의미",
                'analysis': f"이름의 총 획수는 {len(name) * 5}획이며, {fortune_score}점의 운세를 가지고 있습니다.",
                'score': fortune_score
            })
        
        logger.info(f"Generated {num_names} names for {family_name} ({gender})")
        return results
        
    except Exception as e:
        logger.error(f"Name generation error: {str(e)}")
        raise ValueError(str(e)) 