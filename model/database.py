import sqlite3
from datetime import datetime
import os
import hashlib
import secrets
from contextlib import contextmanager
import time
import json
from functools import lru_cache
from werkzeug.security import generate_password_hash, check_password_hash

def hash_password(password, salt=None):
    """비밀번호를 해시화합니다."""
    if salt is None:
        salt = secrets.token_hex(16)
    
    # 비밀번호와 솔트를 결합하여 해시화
    hash_obj = hashlib.sha256()
    hash_obj.update(password.encode())
    hash_obj.update(salt.encode())
    hashed_password = hash_obj.hexdigest()
    
    return hashed_password, salt

def get_db_connection(db_path):
    """데이터베이스 연결을 생성합니다."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    
    # 성능 최적화 설정
    conn.execute('PRAGMA journal_mode=WAL')
    conn.execute('PRAGMA synchronous=NORMAL')
    conn.execute('PRAGMA cache_size=2000')
    conn.execute('PRAGMA temp_store=MEMORY')
    
    return conn

def init_db(db_path):
    """데이터베이스를 초기화합니다."""
    conn = get_db_connection(db_path)
    c = conn.cursor()
    
    # 외래 키 제약 조건 일시 비활성화
    c.execute('PRAGMA foreign_keys=OFF')
    
    # 사용자 테이블 생성
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 이름 테이블 생성
    c.execute('''
        CREATE TABLE IF NOT EXISTS names (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            hanja TEXT NOT NULL,
            meaning TEXT NOT NULL,
            analysis TEXT NOT NULL,
            score REAL NOT NULL,
            gender TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # 인덱스 생성
    c.execute('CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_names_user_id ON names(user_id)')
    
    # 외래 키 제약 조건 다시 활성화
    c.execute('PRAGMA foreign_keys=ON')
    
    conn.commit()
    conn.close()

def create_user(username, password, email, db_path='namemaker.db'):
    """새로운 사용자를 생성합니다."""
    try:
        with get_db_connection(db_path) as conn:
            c = conn.cursor()
            
            # 비밀번호 해시화
            hashed_password, salt = hash_password(password)
            
            c.execute('''
                INSERT INTO users (username, email, password, salt)
                VALUES (?, ?, ?, ?)
            ''', (username, email, hashed_password, salt))
            
            conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

def authenticate_user(username, password, db_path='namemaker.db'):
    """사용자 인증을 수행합니다."""
    with get_db_connection(db_path) as conn:
        c = conn.cursor()
        
        # 사용자 정보 조회
        c.execute('''
            SELECT id, username, email, password, salt
            FROM users
            WHERE username = ?
        ''', (username,))
        
        user = c.fetchone()
        if not user:
            return None
        
        # 비밀번호 검증
        hashed_password, _ = hash_password(password, user[4])
        if hashed_password != user[3]:
            return None
        
        return {
            'id': user[0],
            'username': user[1],
            'email': user[2]
        }

@lru_cache(maxsize=100)
def get_user_by_id(user_id, db_path='namemaker.db'):
    """사용자 ID로 사용자 정보를 조회합니다."""
    with get_db_connection(db_path) as conn:
        c = conn.cursor()
        
        c.execute('''
            SELECT id, username, email, created_at
            FROM users
            WHERE id = ?
        ''', (user_id,))
        
        result = c.fetchone()
        
        if result:
            return {
                'id': result[0],
                'username': result[1],
                'email': result[2],
                'created_at': result[3]
            }
        return None

def save_name(user_id, name_data, db_path='namemaker.db'):
    """생성된 이름을 데이터베이스에 저장합니다."""
    try:
        with get_db_connection(db_path) as conn:
            c = conn.cursor()
            
            c.execute('''
                INSERT INTO names (
                    user_id, name, hanja, meaning, analysis, score
                ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                user_id,
                name_data['name'],
                name_data['hanja'],
                name_data['meaning'],
                json.dumps(name_data['analysis']),
                name_data['score']
            ))
            
            conn.commit()
            return c.lastrowid
    except Exception as e:
        print(f"Error saving name: {e}")
        return None

def get_user_names(user_id, db_path='namemaker.db'):
    """사용자의 저장된 이름 목록을 조회합니다."""
    with get_db_connection(db_path) as conn:
        c = conn.cursor()
        
        c.execute('''
            SELECT id, name, hanja, meaning, analysis, score, created_at
            FROM names
            WHERE user_id = ?
            ORDER BY created_at DESC
        ''', (user_id,))
        
        names = []
        for row in c.fetchall():
            names.append({
                'id': row[0],
                'name': row[1],
                'hanja': row[2],
                'meaning': row[3],
                'analysis': json.loads(row[4]),
                'score': row[5],
                'created_at': row[6]
            })
        
        return names

@lru_cache(maxsize=100)
def get_name_by_id(name_id, user_id, db_path='namemaker.db'):
    """이름 ID로 이름 정보를 조회합니다."""
    with get_db_connection(db_path) as conn:
        c = conn.cursor()
        
        c.execute('''
            SELECT id, name, hanja, meaning, analysis, score
            FROM names
            WHERE id = ? AND user_id = ?
        ''', (name_id, user_id))
        
        name = c.fetchone()
        if name:
            return {
                'id': name[0],
                'name': name[1],
                'hanja': name[2],
                'meaning': name[3],
                'analysis': json.loads(name[4]),
                'score': name[5]
            }
        return None 