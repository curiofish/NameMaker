import unittest
import sys
import os

# 테스트 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# 테스트 모듈 가져오기
from tests.test_name_generator import TestNameGenerator
from tests.test_database import TestDatabase
from tests.test_pdf_generator import TestPDFGenerator

def run_tests():
    """모든 테스트를 실행합니다."""
    # 테스트 스위트 생성
    test_suite = unittest.TestSuite([
        unittest.TestLoader().loadTestsFromTestCase(TestNameGenerator),
        unittest.TestLoader().loadTestsFromTestCase(TestDatabase),
        unittest.TestLoader().loadTestsFromTestCase(TestPDFGenerator)
    ])
    
    # 테스트 실행
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # 테스트 결과 반환
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1) 