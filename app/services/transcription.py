import whisper
import os
from pathlib import Path

model = None

def load_model():
    global model
    if model is None:
        print("Loading Whisper model...")
        model = whisper.load_model("base")
        print("Whisper model loaded!")
    return model

def transcribe_audio(audio_path: str) -> dict:
  
    m = load_model()
    print(f"Transcribing: {audio_path}")
    
    result = m.transcribe(
        audio_path,
        language="en",
        word_timestamps=True,
        verbose=False
    )
    
    segments = []
    for seg in result["segments"]:
        segments.append({
            "start": seg["start"],
            "end": seg["end"],
            "text": seg["text"].strip()
        })
    
    return {
        "text": result["text"],
        "segments": segments
    }