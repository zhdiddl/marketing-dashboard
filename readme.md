# 🚀 마케팅 데이터 & 매출 분석 대시보드
> Naver DataLab에서 검색량 데이터를 수집하고, 매출 데이터를 업로드하여 한눈에 분석할 수 있도록 돕는 대시보드입니다.


## 📌 프로젝트 목표
- Naver DataLab에서 키워드 검색량을 자동으로 크롤링
- 매출 데이터를 업로드하여 검색량과 비교 분석
- 검색량 및 매출 변화율 비교 분석
- FastAPI로 백엔드 API 제공
- Streamlit을 이용한 대시보드 시각화
---
## 🛠️ 기술 스택
- **백엔드:** FastAPI, SQLAlchemy, PostgreSQL
- **웹 크롤링:** Naver DataLab API
- **데이터 처리:** Pandas (데이터 분석), Polars (파일 업로드)
- **프론트엔드:** Streamlit (웹 애플리케이션), Plotly (데이터 시각화)
---
## 📊 주요 기능
1. 검색량 및 매출 데이터 수집
- 네이버 DataLab에서 검색량 크롤링
- 매출 데이터를 CSV 또는 단일 입력 방식으로 업로드
2. 검색량 및 매출 비교 분석
- 특정 키워드의 검색량 및 매출 데이터를 조회
- 검색량과 매출의 변동률(%)을 계산하여 비교
3. 데이터 시각화 (Streamlit)
- 검색량 및 매출 데이터를 차트로 제공
- 검색량 및 매출의 일별 변화율을 비교 차트로 제공
---
## 📡 API 엔드포인트

### 검색량 데이터 (Marketing)

| 메서드 | 엔드포인트 | 설명 |
| --- | --- | --- |
| `GET` | `/marketing/search-volume` | 특정 키워드의 검색량 데이터 조회 |
| `POST` | `/marketing/search-volume` | 특정 키워드의 검색량 데이터를 크롤링하여 저장 |
| `GET` | `/marketing/search-volume-trend` | 최근 7일 vs 이전 7일 검색량 증가율 분석 |

### 매출 데이터 (Sales)

| 메서드 | 엔드포인트 | 설명 |
| --- | --- | --- |
| `GET` | `/sales` | 저장된 매출 데이터 조회 |
| `POST` | `/sales` | 단일 매출 데이터 저장 |
| `POST` | `/sales/files` | CSV 파일을 업로드하여 매출 데이터 저장 |

### 검색량 & 매출 변화율 비교 분석 (Analytics)

| 메서드 | 엔드포인트 | 설명 |
| --- | --- | --- |
| `GET` | `/analytics/marketing-sales` | 특정 기간의 검색량 및 매출 변화율 비교 |

---
## 📝 CSV 업로드 가이드

### 매출 데이터 CSV 형식 예시

| date | revenue |
| --- | --- |
| 2024-01-01 | 150000 |
| 2024-01-02 | 180000 |
| 2024-01-03 | 120000 |
- `date` 컬럼은 YYYY-MM-DD 형식 (매출 일자)
- `revenue` 컬럼은 정수 값 (매출 금액)

---
## 🚀 실행 방법
1. **가상 환경 설정**
```bash
python -m venv venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate  # Windows
```

2. **필요한 패키지 설치**
```bash
pip install -r requirements.txt
```

3. **FastAPI 실행**
```bash
uvicorn backend.app.main:app --reload
```

4. **API 문서 확인 (Swagger UI)**
➡️ 브라우저에서 http://127.0.0.1:8000/docs 접속

5. **Streamlit 실행**
```bash
streamlit run streamlit_app.py
```

---

## 🎨 대시보드 미리보기
