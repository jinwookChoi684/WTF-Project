import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from pathlib import Path
from urllib.parse import quote_plus

#환경 변수 로드
dotenv_path = Path(__file__).parent / '.env'
print(f"DEBUG: .env 파일 경로: {dotenv_path}")
load_dotenv(dotenv_path=dotenv_path)

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

# --- 추가된 디버깅 코드 ---
print("--- .env 파일 로드 결과 ---")
print(f"DB_HOST: {DB_HOST}")
print(f"DB_PORT: {DB_PORT}")
print(f"DB_USER: {DB_USER}")
print(f"DB_PASSWORD: {'설정됨' if DB_PASSWORD else '설정 안됨'}")
print(f"DB_NAME: {DB_NAME}")
print("--------------------------")

# 비밀번호에 포함된 특수문자를 URL 인코딩 처리
encoded_password = quote_plus(DB_PASSWORD) if DB_PASSWORD else ""

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{encoded_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
print(f"DEBUG: 최종 생성된 DATABASE_URL: '{DATABASE_URL}'") # 이 값이 가장 중요합니다!
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

#ORM 모델의 기본 클래스 , 클래스를 상속받아 데이터 베이스 테이블과 매핑되는 모델 정의
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
