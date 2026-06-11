from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import uuid
import os
from app.models.database import get_db, Job, SessionLocal
from app.utils.file_handler import save_upload, get_output_path
from app.services.pipeline import run_pipeline

router = APIRouter()

def run_pipeline_task(job_id: str, video_path: str, target_language: str):
    db = SessionLocal()
    try:
        run_pipeline(job_id, video_path, target_language, db)
    finally:
        db.close()

@router.post("/jobs")
async def create_job(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    target_language: str = "hi",
    db: Session = Depends(get_db)
):
    content = await file.read()
    if len(content) > 500 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large. Max 500MB.")
    filename = save_upload(content, file.filename)
    video_path = f"uploads/{filename}"
    job = Job(
        id=str(uuid.uuid4()),
        status="pending",
        input_file=filename,
        target_language=target_language
    )
    db.add(job)
    db.commit()
    background_tasks.add_task(run_pipeline_task, job.id, video_path, target_language)
    return {"job_id": job.id, "status": "pending"}

@router.get("/jobs/{job_id}")
def get_job_status(job_id: str, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return {
        "job_id": job.id,
        "status": job.status,
        "progress": job.progress,
        "target_language": job.target_language,
        "error_message": job.error_message,
        "created_at": job.created_at
    }

@router.get("/jobs/{job_id}/download")
def download_result(job_id: str, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.status != "done":
        raise HTTPException(status_code=400, detail=f"Job not ready. Current status: {job.status}")
    output_path = get_output_path(f"{job_id}_dubbed.mp4")
    if not os.path.exists(output_path):
        raise HTTPException(status_code=404, detail="Output file not found")
    return FileResponse(
        path=str(output_path),
        media_type="video/mp4",
        filename=f"vocalsync_{job_id}.mp4"
    )

@router.get("/languages")
def get_supported_languages():
    return {
        "languages": {
            "hi": "Hindi",
            "es": "Spanish",
            "fr": "French",
            "de": "German",
            "zh": "Chinese",
            "ar": "Arabic",
            "pt": "Portuguese",
            "ru": "Russian",
            "ja": "Japanese",
            "ko": "Korean"
        }
    }