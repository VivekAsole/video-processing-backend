from pydantic import BaseModel
from datetime import datetime

class VideoSchema(BaseModel):
    id: str
    original_filename: str 
    saved_filename: str
    size: int | None = None
    duration: float | None = None
    upload_time: datetime | None = None

    class Config:
        orm_mode = True

class TrimVideoRequest(BaseModel):
    video_id: str
    start_time: float
    end_time: float
    
class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    result: str | None
    
class TrimmedVideoSchema(BaseModel):
    id: int
    original_file_id: str 
    saved_filename: str
    upload_time: datetime | None = None

    class Config:
        orm_mode = True