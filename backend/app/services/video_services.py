from fastapi import UploadFile
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, NoResultFound
from datetime import datetime, timezone
from app.db.models import Video, TrimmedVideo
from app.utils import get_upload_path, create_file_name
import ffmpeg
import os
import uuid

async def save_file(file: UploadFile, subfolder: str = "videos") -> str:
    '''
    Save the uploaded file in local folder
    '''
    upload_dir = get_upload_path(subfolder)
    _, ext = os.path.splitext(file.filename)
    saved_filename = create_file_name(ext)
    
    file_path = upload_dir / saved_filename
    
    with open(file_path, 'wb') as f:
        f.write(await file.read())
        
    return saved_filename, file_path

def get_video_by_id(db: Session, video_id: str) -> Video:
    """
    Retrieve a video from the database by its ID.

    Args:
        session (Session): SQLAlchemy session object.
        video_id (str): The ID of the video to retrieve.

    Returns:
        Video: The video object if found.

    Raises:
        ValueError: If no video is found with the given ID.
        SQLAlchemyError: If a database error occurs.
        RuntimeError: If an unexpected error occurs.
    """
    try:
        video = db.query(Video).filter(Video.id == video_id).one()
            
        return video

    except NoResultFound:
        raise ValueError(f"No video found with ID {video_id}.")

    except SQLAlchemyError as e:
        # Propagate SQLAlchemy errors with a clear message
        raise SQLAlchemyError(f"Database error occurred while fetching video ID {video_id}: {e}")

    except Exception as e:
        # Catch any other unexpected errors
        raise RuntimeError(f"An unexpected error occurred while fetching video ID {video_id}: {e}")

def save_video_metadata(original_filename: str, saved_filename: str, db: Session, file_path: str) -> Video:
    """
    Save a new video record to the database.
    """
    
    try:
        response = ffmpeg.probe(str(file_path))
        metadata = response.get('format')
        
        duration = metadata.get('duration')
        size = metadata.get('size')
        
        existing_video = db.query(Video).filter(Video.saved_filename == saved_filename).first()
        if existing_video:
            raise ValueError(f"A video with saved_filename '{saved_filename}' already exists.")

        new_video = Video(
            id=uuid.uuid4().hex,
            original_filename=original_filename,
            saved_filename=saved_filename,
            size=size,
            duration=duration,
            upload_time=datetime.now(timezone.utc)
        )
        db.add(new_video)
        db.commit()
        db.refresh(new_video)
        
        return new_video

    except ffmpeg.Error as e:
        print("FFmpeg error:", e.stderr.decode(errors="ignore"))
        raise
    except Exception as e:
        print("Unexpected error:", str(e))
        raise
    
    
def trim_video(start_time: float, end_time: float, saved_filename: str) -> str:
    """
    Trim a video using ffmpeg-python.

    Args:
        saved_filename (str): uploaded file name.
        start_time (float): Start time in seconds.
        end_time (float): End time in seconds.
    """
    

    try:
        upload_dir = get_upload_path()
        _, ext = os.path.splitext(saved_filename)
        trimmed_filename = create_file_name(ext)
        input_path = upload_dir / saved_filename
        trimmed_path = upload_dir / trimmed_filename
        
        # print(f"Trimmed video saved to: \n{trimmed_path}\n{input_path}")
        
        # trim the video        
        (
            ffmpeg
            .input(str(input_path), ss=start_time, to=end_time)
            .output(str(trimmed_path), c='copy')  # use copy to avoid re-encoding
            .overwrite_output()
            .run(quiet=True)
        )
        
        return str(trimmed_path)
    
    except ffmpeg.Error as e:
        print("Error trimming video:", e.stderr.decode())
        raise
    
def save_trim_video_metadata(original_file_id: str, saved_filename: str, db: Session) -> TrimmedVideo:
    """
    Save a trimmed video record to the database.
    """
    try:
        new_video = TrimmedVideo(
            id=uuid.uuid4().hex,
            original_file_id=original_file_id,
            saved_filename=saved_filename,
            upload_time=datetime.now(timezone.utc)
        )
        
        db.add(new_video)
        db.commit()
        db.refresh(new_video)
        
        return new_video
        
    except:
        db.rollback()
        raise
    
    
    
    
    
    
    