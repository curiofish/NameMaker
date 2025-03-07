import unittest
from datetime import datetime
from model.name_generator import (
    generate_name, get_birth_element, get_compatible_elements,
    get_opposing_elements, calculate_name_score
)
from model.hanja_data import get_strokes, get_meaning, get_yinyang_score, get_strokes_score

class TestNameGenerator(unittest.TestCase):
    def setUp(self):
        self.test_data = {
            'family_name': '김',
            'gender': 'male',
            'birth_date': '1990-01-01'
        }

    def test_birth_element(self):
        """생년 오행 테스트"""
        # 1990년은 목(木)의 해
        self.assertEqual(get_birth_element(1990), 'wood')
        # 1991년은 화(火)의 해
        self.assertEqual(get_birth_element(1991), 'fire')
        # 1992년은 토(土)의 해
        self.assertEqual(get_birth_element(1992), 'earth')

    def test_compatible_elements(self):
        """상생 원리 테스트"""
        # 목(木)은 화(火)와 토(土)와 상생
        self.assertEqual(get_compatible_elements('wood'), ['fire', 'earth'])
        # 화(火)는 토(土)와 금(金)과 상생
        self.assertEqual(get_compatible_elements('fire'), ['earth', 'metal'])
        # 토(土)는 금(金)과 수(水)와 상생
        self.assertEqual(get_compatible_elements('earth'), ['metal', 'water'])

    def test_opposing_elements(self):
        """상극 원리 테스트"""
        # 목(木)은 금(金)과 수(水)와 상극
        self.assertEqual(get_opposing_elements('wood'), ['metal', 'water'])
        # 화(火)는 수(水)와 목(木)과 상극
        self.assertEqual(get_opposing_elements('fire'), ['water', 'wood'])
        # 토(土)는 목(木)과 화(火)와 상극
        self.assertEqual(get_opposing_elements('earth'), ['wood', 'fire'])

    def test_generate_name(self):
        """이름 생성 테스트"""
        # 기본 이름 생성
        result = generate_name(self.test_data)
        
        # 기본 구조 확인
        self.assertIn('birth_year', result)
        self.assertIn('birth_element', result)
        self.assertIn('compatibility', result)
        self.assertIn('names', result)
        
        # 이름 목록 확인
        self.assertEqual(len(result['names']), 5)
        
        # 각 이름의 구조 확인
        for name_data in result['names']:
            self.assertIn('name', name_data)
            self.assertIn('hanja', name_data)
            self.assertIn('meaning', name_data)
            self.assertIn('analysis', name_data)
            self.assertIn('score', name_data)
            
            # 한자 획수 확인
            hanja = name_data['hanja']
            total_strokes = sum(get_strokes(char) for char in hanja)
            self.assertEqual(total_strokes, name_data['analysis']['strokes'])
            
            # 점수 범위 확인
            self.assertGreaterEqual(name_data['score'], 0)
            self.assertLessEqual(name_data['score'], 100)
        
        # 옵션을 사용한 이름 생성
        result = generate_name(self.test_data, {'num_names': 3})
        self.assertEqual(len(result['names']), 3)

    def test_name_sorting(self):
        """이름 정렬 테스트"""
        result = generate_name(self.test_data)
        names = result['names']
        
        # 점수에 따른 정렬 확인
        for i in range(len(names) - 1):
            self.assertGreaterEqual(names[i]['score'], names[i + 1]['score'])

    def test_yinyang_balance(self):
        """음양 조화 테스트"""
        result = generate_name(self.test_data)
        
        for name_data in result['names']:
            hanja = name_data['hanja']
            yinyang = name_data['analysis']['yinyang']
            
            # 음양 문자열 형식 확인
            self.assertEqual(len(yinyang), 2)
            self.assertIn(yinyang[0], ['음', '양'])
            self.assertIn(yinyang[1], ['음', '양'])
            
            # 음양 점수 확인
            score = get_yinyang_score(hanja)
            self.assertGreaterEqual(score, 60)
            self.assertLessEqual(score, 100)

    def test_strokes_analysis(self):
        """획수 분석 테스트"""
        result = generate_name(self.test_data)
        
        for name_data in result['names']:
            total_strokes = name_data['analysis']['strokes']
            score = get_strokes_score(total_strokes)
            
            # 획수 점수 확인
            self.assertGreaterEqual(score, 60)
            self.assertLessEqual(score, 100)

    def test_name_score_calculation(self):
        """이름 점수 계산 테스트"""
        # 테스트용 이름 데이터
        name_data = {
            'hanja': '木火',
            'analysis': {
                'yinyang': '양양',
                'elements': 'wood + fire',
                'strokes': 8
            }
        }
        
        # 1990년(목) 기준으로 점수 계산
        score = calculate_name_score(name_data, 'wood')
        
        # 점수 범위 확인
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 100)
        
        # 상극 원리에 따른 감점 확인
        self.assertLess(score, 100)  # 상극 원리로 인해 감점됨

    def test_gender_specific_names(self):
        """성별별 이름 생성 테스트"""
        # 남성 이름 생성
        male_data = self.test_data.copy()
        male_result = generate_name(male_data)
        
        # 여성 이름 생성
        female_data = self.test_data.copy()
        female_data['gender'] = 'female'
        female_result = generate_name(female_data)
        
        # 성별별 한자 선택 확인
        for male_name in male_result['names']:
            for female_name in female_result['names']:
                self.assertNotEqual(male_name['hanja'], female_name['hanja'])

if __name__ == '__main__':
    unittest.main() 