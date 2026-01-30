from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import chat, ingest

app = FastAPI(title="Hệ thống RAG")

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