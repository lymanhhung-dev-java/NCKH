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
