from fastapi import FastAPI
from app.api import chat

app = FastAPI(title="Hệ thống RAG")

# Kết nối API route
app.include_router(chat.router, prefix="/api/v1")

@app.get("/")
def home():
    return {"message": "Server RAG đang hoạt động!"}