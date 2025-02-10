from fastapi import APIRouter, Depends, UploadFile, File
import polars as pl
from sqlalchemy.orm import Session
from backend.app.database import SessionLocal
from backend.app.models.model import SalesData

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
    start_date: str = None,
    end_date: str = None,
    db: Session = Depends(get_db)
):
    query = db.query(SalesData)
    if start_date and end_date:
        query = query.filter(SalesData.date.between(start_date, end_date))
    
    data = query.all()
    if not data:
        return {"message": "설정 조건에 맞는 매출 데이터가 저장되어 있지 않습니다."}
    return data

# 새로운 매출 데이터 추가 (단일 데이터)
@router.post("/")
def add_sales_data(date: str, revenue: int, db: Session = Depends(get_db)):
    new_data = SalesData(date=date, revenue=revenue)
    db.add(new_data)
    db.commit()
    db.refresh(new_data)
    return {"message": "단일 매출 데이터가 성공적으로 저장되었습니다.", "data": new_data}

# 새로운 매출 데이터 추가 (CSV 파일을 업로드 방식)
@router.post("/files")
async def upload_sales_data(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        # CSV 파일을 Polars DataFrame으로 읽기
        df = pl.read_csv(file.file)

        # CSV에서 필요한 컬럼이 없는 경우
        if "date" not in df.columns or "revenue" not in df.columns:
            return {"error": "업로드한 파일에서 'date' 또는 'revenue' 컬럼을 찾을 수 없습니다."}

        # DataFrame을 리스트로 변환 후 DB에 저장
        sales_records = [
            SalesData(date=row["date"], revenue=row["revenue"])
            for row in df.iter_rows(named=True)
        ]

        db.add_all(sales_records)
        db.commit()

        return {"message": f"✅ {len(sales_records)}개의 매출 데이터가 성공적으로 저장되었습니다."}
    except Exception as e:
        return {"error": str(e)}
    