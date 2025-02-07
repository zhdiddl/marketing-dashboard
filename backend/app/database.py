from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

# 환경 변수 로드
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://marketing_user:marketing_password@localhost:5432/marketing_db")

# 데이터베이스 엔진 생성
engine = create_engine(DATABASE_URL)

# 세션 팩토리 설정
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
