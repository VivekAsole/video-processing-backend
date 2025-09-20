##  **Video Processing**

This project is a **Video Processing Backend** built with **FastAPI**, **PostgreSQL**, **SQLAlchemy**, **Celery**, **Redis**, and **ffmpeg-python**. It provides a robust API-driven solution for uploading, processing, and managing videos with advanced features like trimming and overlays.

Key features include:

1. **Upload & Metadata Management**

   * Upload video files via API.
   * Store video metadata (filename, duration, size, upload timestamp) in a PostgreSQL database.
   * List all uploaded videos through a dedicated API.

2. **Video Trimming**

   * Trim videos by providing start and end timestamps.
   * Return the trimmed video directly via API.
   * Save trimmed video information in the database with a reference to the original video.

3. **Video Overlay Processing**

   * Add **text**, **image**, or **video overlays** with configurable positions and timings.
   * Overlay processing runs asynchronously using **Celery + Redis**.
   * APIs for checking job status (`GET /status/{job_id}`) and retrieving processed videos (`GET /result/{job_id}`).

4. **Video Processing Engine**

   * Uses **ffmpeg-python** with **ffmpeg.exe** and **ffprobe.exe** (locally stored) to handle video manipulations efficiently.
   * Supports high-performance, background video processing for scalable workflows.


**API Endpoints**

```markdown
video process: /video
- `GET /get/` - List all video_metadata in db
- `POST /upload/` - upload new video (store in local)
- `POST /trim/` - return trim-video

overlay: /process
- `POST /overlay/` - Schedule the overlay process
- `GET /status/{job_id}/` - check job status
- `GET /result/{job_id}/` - return overlay done video
````


**Features**

```markdown
- REST API with FastAPI
- PostgreSQL database integration with SQLAlchemy
- Background tasks with Celery and Redis
- File uploads
- Async endpoints
```

---

 **Installation**

Explain how to set up the project locally. Include **virtual environment**, **dependencies**, and **database setup**.

1. Clone the repository:
```bash
git clone https://github.com/VivekAsole/video-processing-backend.git
cd project
````

2. Create and activate a virtual environment:

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Set up environment variables:
   Create a `.env` file in the root directory:

```
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
REDIS_URL=redis://localhost:6379/0
```


**Usage**

Start the FastAPI server:
```bash
uvicorn main:app --reload
````

Start Celery worker:

```bash
python start_celery.py
```

---


