import subprocess
import os
from pathlib import Path
from pydub import AudioSegment
import uuid
from app.services.transcription import transcribe_audio
from app.services.diarization import diarize_audio, assign_speakers_to_transcript
from app.services.translation import translate_segments
from app.services.tts import generate_all_segments

OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

def extract_audio(video_path: str) -> str:
    audio_path = str(OUTPUT_DIR / f"{uuid.uuid4().hex}.wav")
    subprocess.run([
        "ffmpeg", "-i", video_path,
        "-ac", "1", "-ar", "16000",
        "-vn", audio_path, "-y"
    ], check=True, capture_output=True)
    return audio_path

def merge_short_segments(segments: list, min_duration: float = 1.5) -> list:
    if not segments:
        return segments
    merged = []
    buffer = segments[0].copy()
    for seg in segments[1:]:
        if (buffer["end"] - buffer["start"]) < min_duration:
            buffer["text"] += " " + seg["text"]
            buffer["end"] = seg["end"]
        else:
            if buffer["text"].strip():
                merged.append(buffer)
            buffer = seg.copy()
    if buffer["text"].strip():
        merged.append(buffer)
    return merged

def get_atempo_filter(speed: float) -> str:
    speed = max(0.5, min(4.0, speed))
    if 0.5 <= speed <= 2.0:
        return f"atempo={speed:.3f}"
    elif speed > 2.0:
        half = speed ** 0.5
        half = min(2.0, half)
        return f"atempo={half:.3f},atempo={half:.3f}"
    return "atempo=1.0"

def build_dubbed_audio(segments: list, original_duration: float) -> str:
    result = AudioSegment.empty()

    for seg in segments:
        seg_dur_ms = max(int((seg["end"] - seg["start"]) * 1000), 100)

        if not seg.get("audio_path") or not os.path.exists(seg["audio_path"]):
            result += AudioSegment.silent(duration=seg_dur_ms)
            continue

        try:
            audio = AudioSegment.from_file(seg["audio_path"])
            result += audio
        except Exception:
            result += AudioSegment.silent(duration=seg_dur_ms)

    temp_path = str(OUTPUT_DIR / f"temp_{uuid.uuid4().hex}.mp3")
    result.export(temp_path, format="mp3")

    actual_ms = len(result)
    target_ms = int(original_duration * 1000)

    if actual_ms > 0 and target_ms > 0 and abs(actual_ms - target_ms) > 500:
        speed = actual_ms / target_ms
        atempo = get_atempo_filter(speed)
        output_path = str(OUTPUT_DIR / f"{uuid.uuid4().hex}.mp3")
        subprocess.run([
            "ffmpeg", "-i", temp_path,
            "-filter:a", atempo,
            "-y", output_path
        ], check=True, capture_output=True)
        os.remove(temp_path)
        return output_path

    return temp_path

def merge_audio_video(video_path: str, audio_path: str, output_path: str):
    subprocess.run([
        "ffmpeg", "-i", video_path,
        "-i", audio_path,
        "-c:v", "copy",
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-shortest", output_path, "-y"
    ], check=True, capture_output=True)

def get_video_duration(video_path: str) -> float:
    result = subprocess.run([
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        video_path
    ], capture_output=True, text=True)
    return float(result.stdout.strip())

def run_pipeline(job_id: str, video_path: str, target_language: str, db) -> str:
    from app.models.database import Job

    def update_progress(progress: float, status: str = "processing"):
        job = db.query(Job).filter(Job.id == job_id).first()
        if job:
            job.progress = progress
            job.status = status
            db.commit()

    try:
        update_progress(5)
        audio_path = extract_audio(video_path)
        update_progress(15)
        transcript = transcribe_audio(audio_path)
        update_progress(35)
        diarization = diarize_audio(audio_path)
        update_progress(50)
        segments = assign_speakers_to_transcript(transcript["segments"], diarization)
        segments = merge_short_segments(segments, min_duration=1.5)
        update_progress(60)
        translated_segments = translate_segments(segments, target_language)
        update_progress(75)
        segments_with_audio = generate_all_segments(translated_segments, target_language)
        update_progress(85)
        duration = get_video_duration(video_path)
        dubbed_audio_path = build_dubbed_audio(segments_with_audio, duration)
        update_progress(95)
        output_filename = f"{job_id}_dubbed.mp4"
        output_path = str(OUTPUT_DIR / output_filename)
        merge_audio_video(video_path, dubbed_audio_path, output_path)
        update_progress(100, "done")
        return output_path

    except Exception as e:
        update_progress(0, "failed")
        job = db.query(Job).filter(Job.id == job_id).first()
        if job:
            job.error_message = str(e)
            db.commit()
        raise e