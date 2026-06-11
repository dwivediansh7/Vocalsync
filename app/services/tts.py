from gtts import gTTS
import os
from pathlib import Path
import uuid

OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

SPEAKER_VOICE_MAP = {
    "SPEAKER_00": {"slow": False},
    "SPEAKER_01": {"slow": True},
    "SPEAKER_02": {"slow": False},
}

def generate_audio_for_segment(text: str, language: str, speaker: str, index: int) -> str:
    if not text or len(text.strip()) < 2:
        return None
    try:
        voice_config = SPEAKER_VOICE_MAP.get(speaker, {"slow": False})
        tts = gTTS(text=text.strip(), lang=language, slow=voice_config["slow"])
        filename = f"seg_{index}_{speaker}_{uuid.uuid4().hex[:8]}.mp3"
        filepath = str(OUTPUT_DIR / filename)
        tts.save(filepath)
        return filepath
    except Exception:
        return None

def generate_all_segments(segments: list, language: str) -> list:
    result = []
    for i, seg in enumerate(segments):
        audio_path = generate_audio_for_segment(
            text=seg["text"],
            language=language,
            speaker=seg.get("speaker", "SPEAKER_00"),
            index=i
        )
        result.append({
            "start": seg["start"],
            "end": seg["end"],
            "text": seg["text"],
            "original_text": seg.get("original_text", ""),
            "speaker": seg.get("speaker", "SPEAKER_00"),
            "audio_path": audio_path
        })
    return result