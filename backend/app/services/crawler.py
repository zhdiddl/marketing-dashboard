import requests
import json
from sqlalchemy.orm import Session
from backend.app.database import SessionLocal
from backend.app.models.model import MarketingData
from dotenv import load_dotenv
import os

# .env 파일 로드
load_dotenv()

# 환경 변수 가져오기
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

# 네이버 데이터랩 API 요청
def get_search_volume(keyword: str, start_date: str, end_date: str):
    url = "https://openapi.naver.com/v1/datalab/search"

    headers = {
        "X-Naver-Client-Id": CLIENT_ID,
        "X-Naver-Client-Secret": CLIENT_SECRET,
        "Content-Type": "application/json"
    }

    body = {
        "startDate": start_date,
        "endDate": end_date,
        "timeUnit": "date",
        "keywordGroups": [{"groupName": keyword, "keywords": [keyword]}]
    }

    response = requests.post(url, headers=headers, data=json.dumps(body))
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error {response.status_code}: {response.text}")
        return None

# 데이터베이스 저장 함수
def save_search_volume(keyword: str, start_date: str, end_date: str):
    db: Session = SessionLocal()
    data = get_search_volume(keyword, start_date, end_date)

    if data:
        for result in data["results"]:
            for period in result["data"]:
                date = period["period"]
                search_volume = period["ratio"]
                
                # 중복 저장 방지 (기존 데이터 확인)
                existing = db.query(MarketingData).filter_by(keyword=keyword, date=date).first()
                if not existing:
                    new_entry = MarketingData(keyword=keyword, date=date, search_volume=search_volume)
                    db.add(new_entry)
        
        db.commit()
        print(f"✅ {keyword} 검색량 데이터 저장 완료!")
    db.close()
