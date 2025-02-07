import sys
import os

# 현재 스크립트의 디렉토리를 시스템 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import engine
from models.model import Base

# 테이블 생성
print("Creating database tables...")
Base.metadata.create_all(bind=engine)
print("Tables created successfully!")
