from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.database import SessionLocal, engine
from backend.app.models.model import MarketingData

router = APIRouter(prefix="/marketing", tags=["Marketing Data"])

# 데이터베이스 세션 의존성 주입
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 모든 마케팅 데이터 조회
@router.get("/")
def get_marketing_data(db: Session = Depends(get_db)):
    return db.query(MarketingData).all()

# 새로운 마케팅 데이터 추가
@router.post("/")
def add_marketing_data(keyword: str, date: str, search_volume: int, db: Session = Depends(get_db)):
    new_data = MarketingData(keyword=keyword, date=date, search_volume=search_volume)
    db.add(new_data)
    db.commit()
    db.refresh(new_data)
    return {"message": "Marketing data added successfully", "data": new_data}
