import logging
from App.routers.router import router
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
# from fastapi.responses import JSONResponse
from src.database import db
from mangum import Mangum

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Alert API",
    description="The backend API",
    version="0.0.1",
    docs_url="/"
) 


# CORS設定 to cominucate with Reqct
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://main.d3dmogmcqruj9x.amplifyapp.com", "https://main.dspqpfuklsqqw.amplifyapp.com", "http://localhost:3000", "https://www.upreapp.com", "https://survey.upreapp.com"],  # 許可するオリジン #TODO CHNAGE to origins
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # 許可するHTTPメソッド
    allow_headers=["*"],  # 許可するヘッダー
)

@app.on_event("startup")
async def startup():
    await db.connect()  # Ensure connection pool is established

@app.on_event("shutdown")
async def shutdown():
    await db.close()  # Close the connection pool when the app shuts down

app.include_router(router)

# # Lambdaハンドラーを作成
handler = Mangum(app)