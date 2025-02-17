from fastapi import Query
from backend.app.utils.validators import validate_date, validate_positive_number

def get_valid_keyword(
        keyword: str = Query(..., min_length=1, max_length=100, title="검색 키워드")
        ) -> str:
        return keyword

def get_valid_date(
        date: str = Query(..., regex=r"^\d{4}-\d{2}-\d{2}$")
        ) -> str:
        return validate_date(date)

def get_valid_revenue(
        revenue: int = Query(...)
        ) -> int:
        return validate_positive_number(revenue)
