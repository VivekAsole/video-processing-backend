from ..celery_app import celery_app
from ..services.video_services import trim_video 
from ..services.overlay_services import apply_overlays_to_video, save_overlay

@celery_app.task(bind=True, name="app.jobs.trim_video_task")
def trim_video_task(start_time, end_time, saved_filename):
    return trim_video(start_time, end_time, saved_filename)

@celery_app.task(bind=True, name="app.jobs.call_overlay_task")
def call_overlay_task(self, input_file, overlays):
    job_id = self.request.id
    
    # Process video
    overlay_filename = apply_overlays_to_video(input_file, overlays)    
    # Save result to DB
    save_overlay(job_id,overlay_filename, overlays )
    
    return {"job_id": job_id}
    
    
    
