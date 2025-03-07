import sqlite3
from datetime import datetime

def init_db():
    """데이터베이스와 필요한 테이블을 초기화합니다."""
    conn = sqlite3.connect('namemaker.db')
    c = conn.cursor()
    
    # 저장된 이름 테이블 생성
    c.execute('''
        CREATE TABLE IF NOT EXISTS saved_names (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            hanja TEXT NOT NULL,
            meaning TEXT NOT NULL,
            gender TEXT NOT NULL,
            birth_date TEXT NOT NULL,
            yinyang TEXT NOT NULL,
            elements TEXT NOT NULL,
            strokes INTEGER NOT NULL,
            created_at TEXT NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()

def save_name(name_data, user_data):
    """생성된 이름을 데이터베이스에 저장합니다."""
    conn = sqlite3.connect('namemaker.db')
    c = conn.cursor()
    
    c.execute('''
        INSERT INTO saved_names (
            name, hanja, meaning, gender, birth_date,
            yinyang, elements, strokes, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        name_data['name'],
        name_data['hanja'],
        name_data['meaning'],
        user_data['gender'],
        user_data['birth_date'],
        name_data['analysis']['yinyang'],
        name_data['analysis']['elements'],
        name_data['analysis']['strokes'],
        datetime.now().isoformat()
    ))
    
    conn.commit()
    conn.close()

def get_saved_names(limit=10):
    """저장된 이름 목록을 조회합니다."""
    conn = sqlite3.connect('namemaker.db')
    c = conn.cursor()
    
    c.execute('''
        SELECT * FROM saved_names
        ORDER BY created_at DESC
        LIMIT ?
    ''', (limit,))
    
    columns = [description[0] for description in c.description]
    results = []
    
    for row in c.fetchall():
        results.append(dict(zip(columns, row)))
    
    conn.close()
    return results 