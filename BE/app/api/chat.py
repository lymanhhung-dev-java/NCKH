from fastapi import APIRouter, HTTPException
from app.model.schemas import ChatRequest, ChatResponse
from app.service.rag_service import rag_service

router = APIRouter()

@router.post("/ask", response_model=ChatResponse)
async def ask_bot(request: ChatRequest):
    try:
        result = rag_service.ask_question(request.question)
        return ChatResponse(
            answer=result["answer"],
            sources=result["sources"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))