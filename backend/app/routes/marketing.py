from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.app.database import SessionLocal, engine
from backend.app.models.model import MarketingData
from backend.app.dependencies import get_valid_keyword
from backend.app.services.crawler import save_search_volume
from datetime import datetime, timedelta
from pydantic import BaseModel

router = APIRouter(prefix="/marketing", tags=["Marketing Data"])

# 데이터베이스 세션 의존성 주입
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 모든 마케팅 데이터 조회 API
@router.get("/")
def get_marketing_data(db: Session = Depends(get_db)):
    return db.query(MarketingData).all()

# 새로운 마케팅 데이터 추가 API
@router.post("/")
def add_marketing_data( 
    date: str, 
    search_volume: int, 
    db: Session = Depends(get_db),
    keyword: str = Depends(get_valid_keyword)
  ):
    new_data = MarketingData(keyword=keyword, date=date, search_volume=search_volume)
    db.add(new_data)
    db.commit()
    db.refresh(new_data)
    return {"message": "Marketing data added successfully", "data": new_data}

# JSON Body 스키마 정의 (크롤링 API용)
class CrawlRequest(BaseModel):
    keyword: str
    start_date: str
    end_date: str

# 특정 키워드의 검색량 데이터 크롤링 API
@router.post("/search-volume")
def crawl_marketing_data(request: CrawlRequest):
    save_search_volume(request.keyword, request.start_date, request.end_date)
    return {"message": f"✅ {request.keyword} 검색량 데이터 크롤링 완료!"}

# 특정 키워드의 검색량 증가율 분석 API (최근 7일 vs 이전 7일)
@router.get("/search-trend")
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
