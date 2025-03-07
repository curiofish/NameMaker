import unittest
from app import app
import json
import os

class TestApp(unittest.TestCase):
    def setUp(self):
        """테스트를 위한 설정"""
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()
        
        # 테스트 데이터
        self.test_user = {
            'username': 'testuser',
            'password': 'testpass',
            'email': 'test@example.com'
        }
        
        self.test_name = {
            'name': '김철수',
            'hanja': '金哲洙',
            'meaning': '밝고 지혜로운 사람',
            'analysis': {
                'yinyang': '음양 조화',
                'elements': '목화토',
                'strokes': 25
            },
            'score': 85.5
        }
    
    def tearDown(self):
        """테스트 후 정리"""
        # 테스트 데이터베이스 파일 삭제
        if os.path.exists('test_namemaker.db'):
            try:
                os.remove('test_namemaker.db')
            except PermissionError:
                pass
    
    def test_index(self):
        """메인 페이지 테스트"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('무료 작명소'.encode('utf-8'), response.data)
    
    def test_register(self):
        """회원가입 테스트"""
        # GET 요청
        response = self.client.get('/register')
        self.assertEqual(response.status_code, 200)
        self.assertIn('회원가입'.encode('utf-8'), response.data)
        
        # POST 요청 (성공)
        response = self.client.post('/register', data=self.test_user)
        self.assertEqual(response.status_code, 302)
        self.assertIn('회원가입이 완료되었습니다'.encode('utf-8'), response.data)
        
        # POST 요청 (중복 사용자명)
        response = self.client.post('/register', data=self.test_user)
        self.assertEqual(response.status_code, 302)
        self.assertIn('이미 존재하는 사용자명입니다'.encode('utf-8'), response.data)
    
    def test_login(self):
        """로그인 테스트"""
        # 사용자 생성
        self.client.post('/register', data=self.test_user)
        
        # GET 요청
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn('로그인'.encode('utf-8'), response.data)
        
        # POST 요청 (성공)
        response = self.client.post('/login', data={
            'username': self.test_user['username'],
            'password': self.test_user['password']
        })
        self.assertEqual(response.status_code, 302)
        self.assertIn('로그인되었습니다'.encode('utf-8'), response.data)
        
        # POST 요청 (실패)
        response = self.client.post('/login', data={
            'username': self.test_user['username'],
            'password': 'wrong_password'
        })
        self.assertEqual(response.status_code, 302)
        self.assertIn('아이디 또는 비밀번호가 올바르지 않습니다'.encode('utf-8'), response.data)
    
    def test_logout(self):
        """로그아웃 테스트"""
        # 로그인
        self.client.post('/register', data=self.test_user)
        self.client.post('/login', data={
            'username': self.test_user['username'],
            'password': self.test_user['password']
        })
        
        # 로그아웃
        response = self.client.get('/logout')
        self.assertEqual(response.status_code, 302)
        self.assertIn('로그아웃되었습니다'.encode('utf-8'), response.data)
    
    def test_dashboard(self):
        """대시보드 테스트"""
        # 로그인하지 않은 상태
        response = self.client.get('/dashboard')
        self.assertEqual(response.status_code, 302)
        self.assertIn('로그인이 필요합니다'.encode('utf-8'), response.data)
        
        # 로그인
        self.client.post('/register', data=self.test_user)
        self.client.post('/login', data={
            'username': self.test_user['username'],
            'password': self.test_user['password']
        })
        
        # 로그인한 상태
        response = self.client.get('/dashboard')
        self.assertEqual(response.status_code, 200)
        self.assertIn('내 이름 관리'.encode('utf-8'), response.data)
    
    def test_generate(self):
        """이름 생성 테스트"""
        # 로그인하지 않은 상태
        response = self.client.get('/generate')
        self.assertEqual(response.status_code, 302)
        self.assertIn('로그인이 필요합니다'.encode('utf-8'), response.data)
        
        # 로그인
        self.client.post('/register', data=self.test_user)
        self.client.post('/login', data={
            'username': self.test_user['username'],
            'password': self.test_user['password']
        })
        
        # GET 요청
        response = self.client.get('/generate')
        self.assertEqual(response.status_code, 200)
        self.assertIn('이름 생성'.encode('utf-8'), response.data)
        
        # POST 요청
        response = self.client.post('/generate', data={
            'family_name': '김',
            'gender': 'male',
            'birth_year': '1990',
            'num_names': '5'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('생성된 이름'.encode('utf-8'), response.data)
    
    def test_save_name(self):
        """이름 저장 테스트"""
        # 로그인
        self.client.post('/register', data=self.test_user)
        self.client.post('/login', data={
            'username': self.test_user['username'],
            'password': self.test_user['password']
        })
        
        # 이름 저장
        response = self.client.post('/save_name', json=self.test_name)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('name_id', data)
    
    def test_download_report(self):
        """PDF 보고서 다운로드 테스트"""
        # 로그인
        self.client.post('/register', data=self.test_user)
        self.client.post('/login', data={
            'username': self.test_user['username'],
            'password': self.test_user['password']
        })
        
        # 이름 저장
        response = self.client.post('/save_name', json=self.test_name)
        data = json.loads(response.data)
        name_id = data['name_id']
        
        # PDF 다운로드
        response = self.client.get(f'/download_report/{name_id}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, 'application/pdf')

if __name__ == '__main__':
    unittest.main() 