from fastapi import APIRouter, Depends
from backend.app.services.crawler import save_search_volume
from backend.app.dependencies import get_valid_keyword

router = APIRouter(prefix="/crawl", tags=["Crawler"])

# 특정 키워드의 검색량 데이터 크롤링 API
@router.post("/marketing")
def crawl_marketing_data(
    start_date: str,
    end_date: str,
    keyword: str = Depends(get_valid_keyword)
  ):
    save_search_volume(keyword, start_date, end_date)
    return {"message": f"✅ {keyword} 검색량 데이터 크롤링 완료!"}
