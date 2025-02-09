from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.database import SessionLocal
from backend.app.models.model import MarketingData, SalesData
from backend.app.dependencies import get_valid_keyword

router = APIRouter(prefix="/analytics", tags=["Data Analytics"])

def get_db():
  db = SessionLocal()
  try:
    yield db
  finally:
    db.close()

# 특정 날짜 검색량 및 매출 비교
@router.get("/marketing-sales")
def compare_marketing_and_sales(
    date: str,
    keyword: str = Depends(get_valid_keyword),
    db: Session = Depends(get_db)
  ):

  # 특정 날짜의 키워드 검색량 조회
  marketing_record = (
    db.query(MarketingData)
    .filter(MarketingData.keyword == keyword, MarketingData.date == date)
    .first()
  )

  # 특정 날짜의 매출 조회
  sales_record = (
    db.query(SalesData)
    .filter(SalesData.date == date)
    .first()
  )

  # 조회 시 데이터가 없으면 예외 처리
  if not marketing_record:
    raise HTTPException(status_code=404, detail=f"{keyword}에 맞는 검색량 데이터가 존재하지 않습니다.")
  if not sales_record:
    raise HTTPException(status_code=404, detail=f"{keyword}에 맞는 매출 데이터가 존재하지 않습니다.")
  
  # 결과 반환
  return {
    "keyword": keyword,
    "date": date,
    "search_volume": marketing_record.search_volume,
    "revenue": sales_record.revenue
  }
