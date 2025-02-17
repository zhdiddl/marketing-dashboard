from fastapi import APIRouter, Depends, UploadFile, File
import polars as pl
from sqlalchemy.orm import Session
from backend.app.database import SessionLocal
from backend.app.models.model import SalesData
from backend.app.utils.validators import validate_date, validate_positive_number, validate_csv_data, validate_no_duplicate_date_in_db

router = APIRouter(prefix="/sales", tags=["Sales Data"])

# 데이터베이스 세션 의존성 주입
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 모든 매출 데이터 조회 (기간 설정 가능)
@router.get("/")
def get_sales_data(
    start_date: str = Depends(validate_date),
    end_date: str = Depends(validate_date),
    db: Session = Depends(get_db)
):
    query = db.query(SalesData)
    if start_date and end_date:
        query = query.filter(SalesData.date.between(start_date, end_date))
    
    data = query.all()
    if not data:
        return [] # 빈 리스트 반환
    return data

# 새로운 매출 데이터 추가 (단일 데이터)
@router.post("/")
def add_sales_data(
    date: str = Depends(validate_date), 
    revenue: int = Depends(validate_positive_number), 
    db: Session = Depends(get_db)
):
    validate_no_duplicate_date_in_db(db, date)

    new_data = SalesData(date=date, revenue=revenue)
    db.add(new_data)
    db.commit()
    db.refresh(new_data)
    return {"message": "단일 매출 데이터가 성공적으로 저장되었습니다.", "data": new_data}

# 새로운 매출 데이터 추가 (CSV 파일을 업로드 방식)
@router.post("/files")
def upload_sales_data(
    file: UploadFile = File(...), 
    db: Session = Depends(get_db)
):
    try:
        # CSV 파일을 Polars DataFrame으로 읽고 검증 함수 호출
        df = pl.read_csv(file.file)
        validate_csv_data(df)

        # DB에서 날짜 데이터를 객체 리스트로 반환해 set으로 저장
        existing_dates = {row.date.strftime("%Y-%m-%d") for row in db.query(SalesData.date).all()}

        new_records = []
        skipped_dates = []

        # 날짜가 중복이면 데이터를 저장하지 않음
        for row in df.iter_rows(named=True):
            if row["date"] in existing_dates:
                skipped_dates.append(row["date"]) # 알림을 위한 중복 날짜 기록
                continue
            new_records.append(SalesData(date=row["date"], revenue=row["revenue"]))

        # 모든 날짜가 중복이면 메시지 반환
        if not new_records:
            return {
                "message": "❌ 모든 날짜의 데이터가 이미 존재합니다. 새로 업데이트한 데이터가 없습니다.",
                "skipped_dates": skipped_dates
            }

        # 객체 리스트를 DB에 저장
        db.add_all(new_records)
        db.commit()

        # 저장 내역에 대한 메시지 반환
        return {
            "message": f"✅ {len(new_records)}개의 매출 데이터가 성공적으로 저장되었습니다.",
            "skipped_dates": f"{skipped_dates}"
        }
    except Exception as e:
        return {"error": str(e)}
    