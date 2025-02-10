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

# 특정 키워드의 검색량 데이터 조회 API (기간 설정 가능)
@router.get("/search-volume")
def get_marketing_data(
    start_date: str = None,
    end_date: str = None,
    keyword: str = Depends(get_valid_keyword),
    db: Session = Depends(get_db)
):

    query = db.query(MarketingData).filter(MarketingData.keyword == keyword)

    if start_date and end_date:
        query = query.filter(MarketingData.date.between(start_date, end_date))

    data = query.all()
    if not data:
        return {"message": f"설정 조건에 맞는 {keyword}에 대한 검색량 데이터가 저장되어 있지 않습니다."}
    return data

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
@router.get("/search-volulme-trend")
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
