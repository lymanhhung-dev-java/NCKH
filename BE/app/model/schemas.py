from typing import List, Optional
from pydantic import BaseModel

class ChatRequest(BaseModel):
    question: str

class Source(BaseModel):
    filename: str
    page: Optional[int] = None
    content: Optional[str] = None

class ChatResponse(BaseModel):
    answer: str
    sources: List[Source] = []