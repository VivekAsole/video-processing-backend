import app.ffmpeg_config
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.video_process_route import router as video_router
from app.api.overlay_route import router as process_router

from app.db import Base, engine

# Create bd table if not exist
# Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Video processing",
    description="A local video processing server",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# include routes
app.include_router(video_router)
app.include_router(process_router)


@app.get("/", summary="Root endpoint")
def read_root():
    """FastAPI based video processing backend."""
    return {"message": "FastAPI based video processing backend."}
