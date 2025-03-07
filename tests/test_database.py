import unittest
import os
import sqlite3
from model.database import (
    init_db, create_user, authenticate_user,
    get_user_by_id, save_name, get_saved_names
)

class TestDatabase(unittest.TestCase):
    def setUp(self):
        """각 테스트 전에 실행됩니다."""
        self.test_db = 'test_namemaker.db'
        # 테스트 데이터베이스 초기화
        init_db(self.test_db)
    
    def tearDown(self):
        """각 테스트 후에 실행됩니다."""
        # 테스트 데이터베이스 삭제
        if os.path.exists(self.test_db):
            try:
                os.remove(self.test_db)
            except PermissionError:
                # Windows에서 파일이 아직 사용 중일 수 있음
                pass
    
    def test_create_user(self):
        """사용자 생성 테스트"""
        # 정상적인 사용자 생성
        self.assertTrue(create_user('testuser', 'test@example.com', 'password123', self.test_db))
        
        # 중복된 사용자명으로 생성 시도
        self.assertFalse(create_user('testuser', 'another@example.com', 'password123', self.test_db))
    
    def test_authenticate_user(self):
        """사용자 인증 테스트"""
        # 테스트 사용자 생성
        create_user('testuser', 'test@example.com', 'password123', self.test_db)
        
        # 올바른 인증 정보
        user_id = authenticate_user('testuser', 'password123', self.test_db)
        self.assertIsNotNone(user_id)
        
        # 잘못된 비밀번호
        self.assertIsNone(authenticate_user('testuser', 'wrongpassword', self.test_db))
        
        # 존재하지 않는 사용자
        self.assertIsNone(authenticate_user('nonexistent', 'password123', self.test_db))
    
    def test_get_user_by_id(self):
        """사용자 정보 조회 테스트"""
        # 테스트 사용자 생성
        create_user('testuser', 'test@example.com', 'password123', self.test_db)
        user_id = authenticate_user('testuser', 'password123', self.test_db)
        
        # 사용자 정보 조회
        user = get_user_by_id(user_id, self.test_db)
        self.assertIsNotNone(user)
        self.assertEqual(user['username'], 'testuser')
        self.assertEqual(user['email'], 'test@example.com')
        
        # 존재하지 않는 사용자 ID
        self.assertIsNone(get_user_by_id(999, self.test_db))
    
    def test_save_and_get_names(self):
        """이름 저장 및 조회 테스트"""
        # 테스트 사용자 생성
        create_user('testuser', 'test@example.com', 'password123', self.test_db)
        user_id = authenticate_user('testuser', 'password123', self.test_db)
        
        # 테스트 데이터
        name_data = {
            'name': '홍길동',
            'hanja': '洪吉同',
            'meaning': '길하고 동일한',
            'analysis': {
                'yinyang': '양양음',
                'elements': '화화목',
                'strokes': 15
            }
        }
        user_data = {
            'gender': '남성',
            'birth_date': '1990-01-01'
        }
        
        # 이름 저장
        save_name(name_data, user_data, user_id, self.test_db)
        
        # 저장된 이름 조회
        saved_names = get_saved_names(user_id=user_id, db_path=self.test_db)
        self.assertEqual(len(saved_names), 1)
        self.assertEqual(saved_names[0]['name'], '홍길동')
        self.assertEqual(saved_names[0]['hanja'], '洪吉同')
        self.assertEqual(saved_names[0]['meaning'], '길하고 동일한')
        self.assertEqual(saved_names[0]['gender'], '남성')
        self.assertEqual(saved_names[0]['birth_date'], '1990-01-01')
        self.assertEqual(saved_names[0]['yinyang'], '양양음')
        self.assertEqual(saved_names[0]['elements'], '화화목')
        self.assertEqual(saved_names[0]['strokes'], 15)

if __name__ == '__main__':
    unittest.main() 