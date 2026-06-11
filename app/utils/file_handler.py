import os
import uuid
import shutil
from pathlib import Path

UPLOAD_DIR = Path("uploads")
OUTPUT_DIR = Path("outputs")

UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {".mp4", ".avi", ".mov", ".mkv", ".webm"}
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB

def save_upload(file_content: bytes, filename: str) -> str:
    """Save uploaded file and return unique filename"""
    ext = Path(filename).suffix.lower()
    
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(f"File type {ext} not allowed. Use: {ALLOWED_EXTENSIONS}")
    
    unique_filename = f"{uuid.uuid4()}{ext}"
    file_path = UPLOAD_DIR / unique_filename
    
    with open(file_path, "wb") as f:
        f.write(file_content)
    
    return unique_filename

def get_upload_path(filename: str) -> Path:
    return UPLOAD_DIR / filename

def get_output_path(filename: str) -> Path:
    return OUTPUT_DIR / filename

def cleanup_files(job_id: str):
    """Delete temp files after job is done"""
    for directory in [UPLOAD_DIR, OUTPUT_DIR]:
        for file in directory.glob(f"{job_id}*"):
            file.unlink(missing_ok=True)