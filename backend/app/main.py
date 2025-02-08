from fastapi import FastAPI
from backend.app.routes.marketing import router as marketing_router
from backend.app.routes.sales import router as sales_router
from backend.app.routes.crawler import router as crawler_router
from backend.app.routes.analytics import router as analytics_router 

app = FastAPI()

# 마케팅 데이터 & 매출 데이터 라우터 등록
app.include_router(marketing_router)
app.include_router(sales_router)
app.include_router(crawler_router) 
app.include_router(analytics_router)

@app.get("/ping")
def ping():
    return {"message": "Server is running!"}
