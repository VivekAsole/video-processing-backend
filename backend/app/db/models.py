from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from .base import Base
from sqlalchemy.dialects.postgresql import JSONB

class Video(Base):
    __tablename__ = "videos" 

    id = Column(String, primary_key=True, index=True)
    original_filename = Column(String, nullable=False)
    saved_filename = Column(String, nullable=False, unique=True)
    size = Column(Integer)
    duration = Column(Float)
    upload_time = Column(DateTime, default=datetime.now(timezone.utc))
    
    # relation to TrimmedVideo
    trimmed_videos = relationship("TrimmedVideo", back_populates='original_video', cascade="all, delete-orphan")
    
class TrimmedVideo(Base):
    __tablename__ = "trimmed_videos"

    id = Column(String, primary_key=True, index=True)
    original_file_id = Column(String, ForeignKey("videos.id"), nullable=False)
    saved_filename = Column(String, nullable=False)
    upload_time = Column(DateTime, default=datetime.now(timezone.utc))
    
    # relationship back to Video
    original_video = relationship("Video", back_populates="trimmed_videos")
    
class Overlay(Base):
    __tablename__ = "overlays"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String, index=True, nullable=False)
    overlay_filename = Column(String, nullable=False)
    overlay = Column(JSONB, nullable=False)