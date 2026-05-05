from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.api import chat, ingest
from app.service.rag_service import rag_service

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Khởi tạo Scheduler
    scheduler = AsyncIOScheduler()
    
    # Cấu hình cronjob chạy lúc 02:00 sáng mỗi ngày
    scheduler.add_job(
        rag_service.sync_website_data,
        trigger='cron',
        hour=2,
        minute=0,
        args=["https://hau.edu.vn/"],
        id='sync_website_job',
        replace_existing=True
    )
    
    # Khởi động scheduler
    scheduler.start()
    print("⏰ Đã khởi động Cronjob thu thập dữ liệu web lúc 02:00 sáng hàng ngày.")
    
    yield
    
    # Tắt scheduler khi app bị tắt
    scheduler.shutdown()
    print("🛑 Đã tắt Cronjob.")

app = FastAPI(title="Hệ thống RAG", lifespan=lifespan)

# CORS Middleware config
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Kết nối API route
app.include_router(chat.router, prefix="/api/v1")
app.include_router(ingest.router, prefix="/api/v1")

@app.get("/")
def home():
    return {"message": "Server RAG đang hoạt động!"}