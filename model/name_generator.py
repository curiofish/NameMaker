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
    # TODO: 실제 이름 생성 로직 구현
    # 현재는 테스트용 더미 데이터를 반환
    return {
        'names': [
            {
                'name': '길동',
                'meaning': '길한 동쪽',
                'hanja': '吉東',
                'analysis': {
                    'yinyang': '양',
                    'elements': '목',
                    'strokes': 12
                }
            }
        ],
        'total_strokes': 12,
        'compatibility': '길함'
    } 