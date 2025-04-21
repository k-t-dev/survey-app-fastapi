import logging
from App.routers.router import router
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
# from fastapi.responses import JSONResponse
from src.database import db

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

# CORSの設定
origins = [
    "https://my-react-app.amplifyapp.com",  # ReactのURL
    "http://localhost:5001",  # ローカル開発環境
]

# CORS設定 to cominucate with Reqct
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 許可するオリジン #TODO CHNAGE to origins
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],  # 許可するHTTPメソッド
    allow_headers=["*"],  # 許可するヘッダー
)


@app.on_event("startup")
async def startup():
    await db.connect()  # Ensure connection pool is established

@app.on_event("shutdown")
async def shutdown():
    await db.close()  # Close the connection pool when the app shuts down


app.include_router(router)

