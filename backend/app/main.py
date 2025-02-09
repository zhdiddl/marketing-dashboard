from fastapi import FastAPI
from backend.app.routes.marketing import router as marketing_router
from backend.app.routes.sales import router as sales_router
from backend.app.routes.marketing_sales import router as marketing_sales_router
from backend.app.routes.marketing_sales import router as data_router

app = FastAPI()

app.include_router(marketing_router)
app.include_router(sales_router)
app.include_router(marketing_sales_router)
app.include_router(data_router)

@app.get("/ping")
def ping():
    return {"message": "Server is running!"}
