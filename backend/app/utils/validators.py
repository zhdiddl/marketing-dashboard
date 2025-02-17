from datetime import datetime
from fastapi import HTTPException
import polars as pl
from sqlalchemy.orm import Session
from backend.app.models.model import SalesData

# 실존하는 날짜인지 검증
def validate_date(date_str: str) -> str:
  try:
    datetime.strptime(date_str, "%Y-%m-%d")
    return date_str
  except ValueError:
    raise HTTPException(status_code=400, detail=f"날짜 입력 값 오류: {date_str}, YYYY-MM-DD 형식으로 입력해주세요.")

# 매출이 양수인지 검증
def validate_positive_number(value: int) -> int:
  if value <= 0:
    raise HTTPException(status_code=400, detail=f"숫자 입력 값 오류: {value}, 값이 0보다 커야 합니다.")
  
# CSV 파일 내용 검증
def validate_csv_data(df: pl.DataFrame):
  required_columns = {"date", "revenue"}

  # 필요한 칼럼 유무 검증
  if not required_columns.issubset(set(df.columns)):
    raise HTTPException(status_code=400, detail="CSV 파일에 'date' 또는 'revenue'가 존재하지 않습니다.")
  
  # 입력된 날짜 형식 검증
  if not all(df["date"].str.contains(r"^\d{4}-\d{2}-\d{2}$")):
    raise HTTPException(status_code=400, detail="CSV 파일에 'date' 칼럼 값이 잘못된 날짜 형식으로 입력되었습니다.")
  
  # 매출 값 검증
  if not all(df["revenue"] > 0):
    raise HTTPException(status_code=400, detail="CSV 파일에 'revenue' 칼럼 값은 0보다 커야 합니다.")
  
  # 중복 날짜 검증
  if df["date"].is_duplicated().any():
    raise HTTPException(status_code=400, detail="CSV 파일에 중복된 날짜 데이터가 포함되어 있습니다.")

# DB에 중복된 날짜가 있는지 검증
def validate_no_duplicate_date_in_db(db: Session, date: str):
  existing_data = db.query(SalesData).filter(SalesData.date == date).first()
  if existing_data:
    raise HTTPException(status_code=400, detail="중복 날짜: {date}, DB에 이미 매출 데이터가 존재합니다.")
