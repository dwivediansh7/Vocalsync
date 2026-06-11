from deep_translator import GoogleTranslator
import concurrent.futures
import time

def translate_text(text: str, target_language: str = "hi") -> str:
    if not text.strip():
        return text
    def _translate():
        return GoogleTranslator(source="auto", target=target_language).translate(text)
    try:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(_translate)
            result = future.result(timeout=8)
            return result if result else text
    except Exception:
        return text

def translate_segments(segments: list, target_language: str = "hi") -> list:
    result = []
    for i, seg in enumerate(segments):
        translated = translate_text(seg["text"], target_language)
        result.append({
            "start": seg["start"],
            "end": seg["end"],
            "text": translated,
            "original_text": seg["text"],
            "speaker": seg.get("speaker", "SPEAKER_00")
        })
        if i % 5 == 4:
            time.sleep(0.5)
    return result