from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.database import SessionLocal
from backend.app.models.model import SalesData

router = APIRouter(prefix="/sales", tags=["Sales Data"])

# 데이터베이스 세션 의존성 주입
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 모든 매출 데이터 조회
@router.get("/")
def get_sales_data(db: Session = Depends(get_db)):
    return db.query(SalesData).all()

# 새로운 매출 데이터 추가
@router.post("/")
def add_sales_data(date: str, revenue: int, db: Session = Depends(get_db)):
    new_data = SalesData(date=date, revenue=revenue)
    db.add(new_data)
    db.commit()
    db.refresh(new_data)
    return {"message": "Sales data added successfully", "data": new_data}
