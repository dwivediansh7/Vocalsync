# Design Decisions

Some notes on why I built things the way I did.

## Whisper over other ASR options

I went with Whisper base model. It's not the most accurate model out there
but it's fast enough to run locally without a GPU and handles accented English
reasonably well. For a 1-minute video it transcribes in under 30 seconds on
CPU which felt acceptable. If accuracy becomes a bottleneck, swapping to
whisper-small or whisper-medium is a one-line change.

## pyannote.audio for diarization

Honestly this was the hardest part to get right. I tried a few approaches for
speaker detection and pyannote 3.1 gave the cleanest results for separating
two speakers in a conversation. The gated model access on HuggingFace is
annoying but worth it — the output quality is noticeably better than older
versions.

## Midpoint-based speaker assignment

When merging transcript segments with diarization output I used the midpoint
of each transcript segment to find which speaker is talking. It's a simple
heuristic but works well in practice. The edge cases (someone speaking right
at a diarization boundary) are rare enough that I didn't over-engineer it.

## deep-translator over paid APIs

Google Translate API needs billing setup and has costs at scale. deep-translator
wraps the free version and covers all 10 languages I wanted to support. For a
demo and most real use cases it's more than good enough. The auto source
detection also means users don't need to specify the input language.

## gTTS for voice synthesis

I considered ElevenLabs for voice cloning but it needs an API key and has
usage limits on the free tier. gTTS is completely free, works offline after
the first call, and supports all the target languages. The per-speaker
differentiation using slow/normal speed isn't perfect but it's enough to tell
speakers apart in the output. For production you'd swap this out for a proper
TTS service.

## SQLite over PostgreSQL

This is a single-server application and jobs are processed sequentially.
SQLite is zero-config, works out of the box in Docker, and handles the job
tracking use case without any issues. Switching to PostgreSQL later would
just need a connection string change in the config.

## Background tasks over Celery

FastAPI's built-in BackgroundTasks handles async job processing without
needing a message broker like Redis or RabbitMQ. For the scale this
application targets it's perfectly fine. If I needed to run 50 concurrent
jobs I'd move to Celery but that felt like over-engineering for now.

## ffmpeg for everything audio/video

ffmpeg handles both the audio extraction and the final video merge. It's
battle-tested, available on every platform, and the Docker image pulls it
cleanly. I didn't want two separate tools for what is essentially the same
job.

## Streamlit for the frontend

The FastAPI docs at /docs work fine for testing but aren't something you'd
show a non-technical person. Streamlit let me build a clean upload interface
in about 50 lines of Python without touching HTML or CSS. It also made the
demo a lot easier to record.
