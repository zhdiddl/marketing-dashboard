from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.app.database import SessionLocal
from backend.app.models.model import MarketingData
from datetime import datetime, timedelta
from backend.app.dependencies import get_valid_keyword

router = APIRouter(prefix="/analytics", tags=["Analytics"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 특정 키워드의 검색량 증가율 분석 API
@router.get("/trend")
def get_search_trend(
    keyword: str = Depends(get_valid_keyword), 
    db: Session = Depends(get_db)
  ):
    today = datetime.today()
    last_week = today - timedelta(days=7)
    two_weeks_ago = today - timedelta(days=14)

    # 최근 7일 검색량 합산
    current_volume = db.query(func.sum(MarketingData.search_volume)).filter(
        MarketingData.keyword == keyword,
        MarketingData.date >= last_week.strftime("%Y-%m-%d")
    ).scalar() or 0

    # 이전 7일 검색량 합산
    previous_volume = db.query(func.sum(MarketingData.search_volume)).filter(
        MarketingData.keyword == keyword,
        (MarketingData.date >= two_weeks_ago.strftime("%Y-%m-%d")) & (MarketingData.date < last_week.strftime("%Y-%m-%d"))
    ).scalar() or 0

    # 증가율 계산
    if previous_volume == 0:
        change_rate = "N/A"
    else:
        change_rate = ((current_volume - previous_volume) / previous_volume * 100)

    return {
        "keyword": keyword,
        "search_volume": current_volume,
        "last_week_search_volume": previous_volume,
        "change_rate": f"{change_rate:.2f}%" if change_rate != "N/A" else "데이터가 부족합니다. 데이터가 쌓이면 정상적으로 분석됩니다."
    }
