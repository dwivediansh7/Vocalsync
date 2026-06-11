import pytest
import io
import os
from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app
from app.models.database import Base, engine

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

# --- Core API Tests ---

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["name"] == "VocalSync AI"

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "All operations working smoothly"

def test_get_languages():
    response = client.get("/api/v1/languages")
    assert response.status_code == 200
    data = response.json()
    assert "languages" in data
    assert "hi" in data["languages"]
    assert "es" in data["languages"]
    assert len(data["languages"]) == 10

def test_get_job_not_found():
    response = client.get("/api/v1/jobs/nonexistent-id")
    assert response.status_code == 404

def test_download_job_not_found():
    response = client.get("/api/v1/jobs/nonexistent-id/download")
    assert response.status_code == 404

# --- Job Lifecycle Tests ---

@patch("app.api.routes.run_pipeline_task")
def test_create_job_returns_job_id(mock_pipeline):
    files = {"file": ("test.mp4", io.BytesIO(b"fake video"), "video/mp4")}
    response = client.post("/api/v1/jobs?target_language=hi", files=files)
    assert response.status_code == 200
    data = response.json()
    assert "job_id" in data
    assert data["status"] == "pending"

@patch("app.api.routes.run_pipeline_task")
def test_job_status_after_upload(mock_pipeline):
    files = {"file": ("test.mp4", io.BytesIO(b"fake video"), "video/mp4")}
    create_res = client.post("/api/v1/jobs?target_language=es", files=files)
    job_id = create_res.json()["job_id"]

    status_res = client.get(f"/api/v1/jobs/{job_id}")
    assert status_res.status_code == 200
    data = status_res.json()
    assert data["job_id"] == job_id
    assert data["status"] == "pending"
    assert data["target_language"] == "es"
    assert data["progress"] == 0.0

@patch("app.api.routes.run_pipeline_task")
def test_download_before_completion_returns_400(mock_pipeline):
    files = {"file": ("test.mp4", io.BytesIO(b"fake video"), "video/mp4")}
    create_res = client.post("/api/v1/jobs", files=files)
    job_id = create_res.json()["job_id"]

    download_res = client.get(f"/api/v1/jobs/{job_id}/download")
    assert download_res.status_code == 400
    assert "not ready" in download_res.json()["detail"].lower()

# --- Service Unit Tests ---

def test_translate_empty_string():
    from app.services.translation import translate_text
    result = translate_text("", "hi")
    assert result == ""

def test_translate_segments_structure():
    from app.services.translation import translate_segments
    segments = [
        {"start": 0.0, "end": 2.0, "text": "Hello", "speaker": "SPEAKER_00"},
        {"start": 2.0, "end": 4.0, "text": "World", "speaker": "SPEAKER_01"}
    ]
    with patch("app.services.translation.GoogleTranslator") as mock:
        mock.return_value.translate.side_effect = ["नमस्ते", "दुनिया"]
        result = translate_segments(segments, "hi")
    assert len(result) == 2
    assert result[0]["original_text"] == "Hello"
    assert result[1]["original_text"] == "World"
    assert "speaker" in result[0]

def test_assign_speakers_to_transcript():
    from app.services.diarization import assign_speakers_to_transcript
    transcript_segs = [
        {"start": 0.0, "end": 2.0, "text": "Hello"},
        {"start": 3.0, "end": 5.0, "text": "World"}
    ]
    diar_segs = [
        {"start": 0.0, "end": 2.5, "speaker": "SPEAKER_00"},
        {"start": 2.5, "end": 6.0, "speaker": "SPEAKER_01"}
    ]
    result = assign_speakers_to_transcript(transcript_segs, diar_segs)
    assert result[0]["speaker"] == "SPEAKER_00"
    assert result[1]["speaker"] == "SPEAKER_01"

def test_assign_speakers_fallback():
    from app.services.diarization import assign_speakers_to_transcript
    transcript_segs = [{"start": 0.0, "end": 2.0, "text": "Hello"}]
    result = assign_speakers_to_transcript(transcript_segs, [])
    assert result[0]["speaker"] == "SPEAKER_00"