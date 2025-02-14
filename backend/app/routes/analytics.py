from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import pandas as pd
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

# 특정 기간의 검색량 및 매출 변화율 비교 API
@router.get("/marketing-sales")
def compare_marketing_and_sales(
    start_date: str,
    end_date: str,
    keyword: str = Depends(get_valid_keyword),
    db: Session = Depends(get_db),
):
    
    # JOIN으로 조회 쿼리 한 번 실행
    query = (
        db.query(MarketingData.date, MarketingData.search_volume, SalesData.revenue)
        .outerjoin(SalesData, MarketingData.date == SalesData.date)  # 날짜 기준 LEFT JOIN
        .filter(
            MarketingData.keyword == keyword,
            MarketingData.date.between(start_date, end_date),
        )
        .order_by(MarketingData.date)
    )

    records = query.all()

    # 해당 기간 데이터가 없는 경우 알림 메시지 반환
    if not records:
        return {
            "message": "데이터 부족으로 분석이 어렵습니다.",
            "missing_data": [f"{start_date}부터 {end_date}까지 {keyword}의 데이터 없음"],
            "data": [],
        }

    # 변화율을 루프에서 계산
    result = []
    prev_search_volume = None
    prev_revenue = None

    for record in records:
        date, search_volume, revenue = record
        search_volume_change = None
        revenue_change = None

        if prev_search_volume is not None and search_volume is not None:
            search_volume_change = round(((search_volume - prev_search_volume) / prev_search_volume * 100), 2)

        if prev_revenue is not None and revenue is not None:
            revenue_change = round(((revenue - prev_revenue) / prev_revenue * 100), 2)

        result.append({
            "keyword": keyword,
            "date": date,
            "search_volume_change_rate": search_volume_change,
            "revenue_change_rate": revenue_change,
        })

        prev_search_volume = search_volume
        prev_revenue = revenue

    return {
        "message": "데이터 조회 성공",
        "missing_data": [],
        "data": result
    }
