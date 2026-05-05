from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.service.rag_service import rag_service
from pydantic import BaseModel

router = APIRouter()

class IngestRequest(BaseModel):
    directory_path: str = "./data"

@router.post("/ingest")
async def ingest_data(request: IngestRequest, background_tasks: BackgroundTasks):
    """
    Trigger data ingestion in the background.
    """
    try:
        # Run ingestion in background to avoid blocking the API
        background_tasks.add_task(rag_service.ingest_documents, request.directory_path)
        return {"message": "Ingestion process started in background.", "target_directory": request.directory_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class WebIngestRequest(BaseModel):
    start_url: str = "https://hau.edu.vn/"

@router.post("/ingest/web")
async def ingest_web_data(request: WebIngestRequest, background_tasks: BackgroundTasks):
    """
    Trigger web data ingestion from start url using recursive crawler in the background.
    """
    try:
        background_tasks.add_task(rag_service.sync_website_data, request.start_url)
        return {"message": "Tiến trình đồng bộ Website đã được kích hoạt chạy ngầm...", "start_url": request.start_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
