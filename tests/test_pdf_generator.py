import unittest
import os
from model.pdf_generator import create_name_report

class TestPDFGenerator(unittest.TestCase):
    def setUp(self):
        """테스트 데이터를 설정합니다."""
        self.test_name_id = 1
        self.test_name_data = {
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
        
    def test_create_name_report(self):
        """PDF 보고서 생성 테스트"""
        # PDF 생성
        report_path = create_name_report(self.test_name_data, self.test_name_id)
        
        # 파일이 생성되었는지 확인
        self.assertTrue(os.path.exists(report_path))
        
        # 파일 크기가 0보다 큰지 확인
        self.assertGreater(os.path.getsize(report_path), 0)
        
        # 파일 경로 형식 확인
        self.assertTrue(report_path.startswith('static/reports/'))
        self.assertTrue(report_path.endswith('.pdf'))
        
        # 파일명 형식 확인
        self.assertEqual(os.path.basename(report_path), f'name_report_{self.test_name_id}.pdf')
        
    def test_report_content(self):
        """보고서 내용 검증"""
        # PDF 생성
        report_path = create_name_report(self.test_name_data, self.test_name_id)
        
        # 파일이 생성되었는지 확인
        self.assertTrue(os.path.exists(report_path))
        
        # 파일 크기가 0보다 큰지 확인
        self.assertGreater(os.path.getsize(report_path), 0)
        
        # TODO: PDF 내용 검증 (복잡한 작업이므로 현재는 생략)
        
    def tearDown(self):
        """테스트 후 정리"""
        # 생성된 PDF 파일 삭제
        report_path = os.path.join('static', 'reports', f'name_report_{self.test_name_id}.pdf')
        if os.path.exists(report_path):
            os.remove(report_path)

if __name__ == '__main__':
    unittest.main() 