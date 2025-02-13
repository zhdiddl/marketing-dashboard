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
    # 특정 기간의 키워드 검색량 조회
    marketing_records = (
        db.query(MarketingData)
        .filter(
            MarketingData.keyword == keyword,
            MarketingData.date.between(start_date, end_date),
        )
        .all()
    )

    # 특정 기간의 매출 조회
    sales_records = (
        db.query(SalesData)
        .filter(SalesData.date.between(start_date, end_date))
        .all()
    )

    # 부족한 데이터가 있는 경우 응답에 메시지로 반환
    missing_data = []
    if not marketing_records:
        missing_data.append(f"'{start_date}부터 {end_date}까지의 {keyword}'의 검색량 데이터 없음")
    if not sales_records:
        missing_data.append(f"'{start_date}부터 {end_date}까지의 매출 데이터 없음")

    if missing_data:
        return {
            "message": "데이터 부족으로 분석이 어렵습니다.",
            "missing_data": missing_data,
            "data": [],
        }

    # 빠른 조회를 위해 딕셔너리로 변환
    sales_dict = {s.date: s for s in sales_records}
    marketing_dict = {m.date: m for m in marketing_records}

    result = []
    prev_search_volume = None
    prev_revenue = None

    for date in sorted(set(sales_dict.keys()).union(marketing_dict.keys())):
        search_volume = marketing_dict.get(date).search_volume if date in marketing_dict else None
        revenue = sales_dict.get(date).revenue if date in sales_dict else None

        # 변화율 계산
        search_volume_change = None
        revenue_change = None

        if prev_search_volume is not None and search_volume is not None:
            search_volume_change = ((search_volume - prev_search_volume) / prev_search_volume * 100)
        
        if prev_revenue is not None and revenue is not None:
            revenue_change = ((revenue - prev_revenue) / prev_revenue * 100)

        result.append({
            "keyword": keyword,
            "date": date,
            "search_volume_change_rate": round(search_volume_change, 2) if search_volume_change is not None else None,
            "revenue_change_rate": round(revenue_change, 2) if revenue_change is not None else None
        })

        prev_search_volume = search_volume
        prev_revenue = revenue

    return {
        "message": "데이터 조회 성공",
        "missing_data": [],
        "data": result,  # 응답 확장을 위해 data 키를 사용
    }
