from pyannote.audio import Pipeline
import os
import torch
import soundfile as sf
from dotenv import load_dotenv

load_dotenv()

pipeline = None

def load_pipeline():
    global pipeline
    if pipeline is None:
        pipeline = Pipeline.from_pretrained(
            "pyannote/speaker-diarization-3.1",
            token=os.getenv("HF_TOKEN")
        )
    return pipeline

def get_annotation(result):
    if hasattr(result, 'itertracks'):
        return result

    for attr in ['diarization', 'annotation', 'output']:
        try:
            candidate = getattr(result, attr)
            if hasattr(candidate, 'itertracks'):
                return candidate
        except AttributeError:
            continue

    try:
        for value in vars(result).values():
            if hasattr(value, 'itertracks'):
                return value
    except TypeError:
        pass

    raise ValueError(
        f"Type: {type(result).__name__} | Attributes: {[x for x in dir(result) if not x.startswith('_')]}"
    )

def diarize_audio(audio_path: str) -> list:
    p = load_pipeline()

    waveform, sample_rate = sf.read(audio_path, dtype="float32", always_2d=True)
    waveform = torch.tensor(waveform.T)
    audio_input = {"waveform": waveform, "sample_rate": sample_rate}

    result = p(audio_input)
    annotation = get_annotation(result)

    segments = []
    for turn, _, speaker in annotation.itertracks(yield_label=True):
        segments.append({
            "start": round(turn.start, 2),
            "end": round(turn.end, 2),
            "speaker": speaker
        })

    return segments

def assign_speakers_to_transcript(transcript_segments: list, diarization_segments: list) -> list:
    result = []
    for t_seg in transcript_segments:
        t_mid = (t_seg["start"] + t_seg["end"]) / 2
        speaker = "SPEAKER_00"

        for d_seg in diarization_segments:
            if d_seg["start"] <= t_mid <= d_seg["end"]:
                speaker = d_seg["speaker"]
                break

        result.append({
            "start": t_seg["start"],
            "end": t_seg["end"],
            "text": t_seg["text"],
            "speaker": speaker
        })

    return result