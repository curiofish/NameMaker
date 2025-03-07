# NameMaker - AI 기반 이름 생성 서비스

AI를 활용한 한글 이름 생성 서비스입니다. 사용자의 성별, 출생년도 등을 고려하여 운세와 의미가 있는 이름을 생성합니다.

## 주요 기능

- AI 기반 이름 생성
- 운세 점수 분석
- 한자 의미 분석
- PDF 리포트 생성
- 이름 저장 및 관리
- 다크 모드 지원

## 기술 스택

- Python 3.9
- Flask
- SQLite
- ReportLab (PDF 생성)
- Bootstrap 5
- jQuery

## 설치 및 실행

1. 저장소 클론
```bash
git clone https://github.com/your-username/namemaker.git
cd namemaker
```

2. 가상환경 생성 및 활성화
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. 의존성 설치
```bash
pip install -r requirements.txt
```

4. 데이터베이스 초기화
```bash
python init_db.py
```

5. 서버 실행
```bash
python app.py
```

6. 브라우저에서 접속
```
http://localhost:5000
```

## 라이선스

MIT License 