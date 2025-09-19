from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.db import get_db, Video
from app.services.video_services import save_file, save_video_metadata, get_video_by_id, trim_video, save_trim_video_metadata
from app.schemas.schemas import VideoSchema, TrimVideoRequest



router = APIRouter(prefix="/video", tags=["videos"])

@router.get("/get", response_model=list[VideoSchema])
def get_all_videos(db: Session = Depends(get_db)):
    """
    Fetch all videos with error handling.
    """
    try:
        videos = db.query(Video).all()
        return videos

    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Unexpected error occurred."
        )


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(),
    db: Session = Depends(get_db),
):
    try:
        # Save file to disk
        original_filename = file.filename
        saved_filename, file_path = await save_file(file)
        
        response = save_video_metadata(original_filename, saved_filename, db, file_path=str(file_path))              

        return {"message": "Upload successful", "result": response}

    except Exception as e:
        print(f"Error uploading file: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to upload file")


@router.post("/trim")
def trim_video_request(request: TrimVideoRequest, db: Session = Depends(get_db)):
    try:
        start_time = request.start_time
        end_time = request.end_time
        
        duration = end_time - start_time
        if duration <= 0:
            raise ValueError("End time must be greater than start time.")   
        
             
        video_data = get_video_by_id(db, request.video_id)
        # Check if video exists
        if not video_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Video with ID {request.video_id} not found"
            )
        
        if video_data.duration < duration:
            raise ValueError("Trim duration must be smaller than video duration.")
        
        # trim video
        saved_filename = trim_video(start_time, end_time, saved_filename=video_data.saved_filename)

        trimmed_video_metadata = save_trim_video_metadata(original_file_id=video_data.id, saved_filename=saved_filename, db=db)

        return FileResponse(
            path=trimmed_video_metadata.saved_filename,
            filename=saved_filename,
            media_type="video/mp4"
        )
    
    except Exception as e:
        print(f"An error occurred while trimming the video: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while trimming the video: {str(e)}"
        )
    
    

    