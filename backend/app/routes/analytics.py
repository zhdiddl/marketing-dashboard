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

# 특정 기간의 검색량 및 매출 비교
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
        db.query(SalesData).filter(SalesData.date.between(start_date, end_date)).all()
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

    # 데이터 변환
    result = []
    sales_dict = {s.date: s for s in sales_records}  # dict로 변환해 빠르게 조회

    for record in marketing_records:
        sales_data = sales_dict.get(record.date)  # 날짜 기준 조회
        if sales_data:
            result.append(
                {
                    "keyword": record.keyword,
                    "date": record.date,
                    "search_volume": record.search_volume,
                    "revenue": sales_data.revenue,
                }
            )

    return {
        "message": "데이터 조회 성공",
        "missing_data": [],
        "data": result,  # 응답 확장을 위해 data 키를 사용
    }
