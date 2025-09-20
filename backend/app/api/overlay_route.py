from fastapi import APIRouter, Depends, File, Form, UploadFile, HTTPException
from fastapi.responses import FileResponse
from typing import Optional
from sqlalchemy.orm import Session
import json

from app.db import get_db, Overlay
from app.services.video_services import save_file, get_video_by_id
from app.services.overlay_services import validate_overlays
from app.jobs.celery_tasks import call_overlay_task
from app.schemas.schemas import TaskStatusResponse
from app.utils import get_task_status, get_upload_path


router = APIRouter(prefix="/process", tags=["process"])

"""
    Schedule the overlay process. 
    In single request max 3 overlay can be schedule
    "text", "image" and "video" overlay support
"""
@router.post("/overlay")
async def process_video_overlay_request(
    video_id: str = Form(...),
    overlays: str = Form(...),
    overlay_file_1: Optional[UploadFile] = File(None),
    overlay_file_2: Optional[UploadFile] = File(None),
    overlay_file_3: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
            
    try:
        overlays_data = json.loads(overlays)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON for overlays")
    
    file_map = {
        "overlay_file_1": overlay_file_1,
        "overlay_file_2": overlay_file_2,
        "overlay_file_3": overlay_file_3
    }
    # Validate overlays
    is_valid, errors = validate_overlays(overlays_data, file_map, max_overlays=3)
    if not is_valid:
        raise HTTPException(status_code=400, detail=errors)
    
    # Save files and update overlay paths
    for key, file in file_map.items():
        if file is not None:
            saved_filename, file_path = await save_file(file, "overlay_items")
            
            # Update overlays where file_key == current key
            for overlay in overlays_data:
                if overlay.get("file_key") == key:
                    overlay["file_key"] = str(file_path)
    
    video_data = get_video_by_id(db, video_id)
    input_file=video_data.saved_filename

    # pass the process in job queue
    job = call_overlay_task.delay(input_file=input_file, overlays=overlays_data)
        
    return {"job_id": job.id}


# download the overlay processed video
@router.get("/result/{job_id}")
def get_overlay_file(job_id: str, db: Session = Depends(get_db)):
    overlay = db.query(Overlay).filter(Overlay.job_id == job_id).first()
    
    if not overlay:
        raise HTTPException(status_code=404, detail="Overlay not found")
    
    overlays_folder = get_upload_path('overlays')
    overlay_filename = overlay.overlay_filename
    
    path = overlays_folder / overlay_filename    
    
    return FileResponse(
            path=path,
            filename=overlay_filename,
            media_type="video/mp4"
        )
    
    
# check the status of job    
@router.get("/status/{job_id}", response_model=TaskStatusResponse)
def status_request(job_id: str):
    """
    Check the status of a Celery task by its ID.
    """
    try:
        job_status = get_task_status(job_id)
    except Exception as e:
        # Raise HTTP 500 if something goes wrong
        raise HTTPException(status_code=500, detail=f"Error fetching task status: {str(e)}")

    # Ensure 'result' is JSON serializable
    if job_status.get("result") is not None:
        job_status["result"] = str(job_status["result"])

    return job_status