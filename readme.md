# 🚀 마케팅 데이터 & 매출 분석 대시보드

이 프로젝트는 Naver DataLab에서 검색량 데이터를 수집하고, 매출 데이터를 업로드하여 한눈에 분석할 수 있도록 돕는 대시보드입니다.

## 📌 프로젝트 목표
- Naver DataLab에서 키워드 검색량을 자동으로 크롤링
- 매출 데이터를 업로드하여 검색량과 비교 분석
- FastAPI로 백엔드 API 제공
- Streamlit을 이용한 대시보드 시각화

## 🛠️ 기술 스택
- **백엔드:** FastAPI, SQLAlchemy, PostgreSQL
- **웹 크롤링:** Selenium / Requests + BeautifulSoup
- **데이터 분석:** Polars
- **프론트엔드:** Streamlit
- **배포:** Docker

## 🚀 실행 방법
1. **가상 환경 설정**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Mac/Linux
   venv\Scripts\activate  # Windows
```

2. **필요한 패키지 설치**
```
pip install -r requirements.txt
```