import os
import re
import tempfile
from typing import Optional

from youtube_transcript_api import YouTubeTranscriptApi


# =========================================================
# GLOBAL WHISPER MODEL CACHE
# =========================================================

_whisper_model = None


def get_whisper_model():
    """
    Load Whisper model only once.
    Reuse the same model for future transcriptions.
    """

    global _whisper_model

    if _whisper_model is None:
        from faster_whisper import WhisperModel

        print("Loading Whisper base model...")

        _whisper_model = WhisperModel(
            "base",
            device="cpu",
            compute_type="int8",
        )

        print("Whisper model loaded successfully.")

    return _whisper_model


# =========================================================
# YOUTUBE VIDEO ID
# =========================================================

def extract_video_id(url: str) -> Optional[str]:
    """
    Extract YouTube video ID from supported YouTube URLs.
    """

    if not url:
        return None

    patterns = [
        r"(?:youtube\.com/watch\?v=)([A-Za-z0-9_-]{11})",
        r"(?:youtu\.be/)([A-Za-z0-9_-]{11})",
        r"(?:youtube\.com/embed/)([A-Za-z0-9_-]{11})",
        r"(?:youtube\.com/shorts/)([A-Za-z0-9_-]{11})",
    ]

    for pattern in patterns:
        match = re.search(pattern, url)

        if match:
            return match.group(1)

    return None


# =========================================================
# TRANSCRIBE AUDIO WITH WHISPER
# =========================================================

def transcribe_with_whisper(
    file_path: str,
    language: Optional[str] = None,
) -> Optional[str]:
    """
    Transcribe an audio/video file using faster-whisper.
    """

    try:
        model = get_whisper_model()

        print("Starting Whisper transcription...")

        segments, info = model.transcribe(
            file_path,
            language=language,
            beam_size=1,
            vad_filter=False,
            condition_on_previous_text=False,
        )

        text_parts = []

        for segment in segments:
            text = getattr(segment, "text", "")

            if text:
                cleaned_text = text.strip()

                if cleaned_text:
                    text_parts.append(cleaned_text)

        full_text = " ".join(text_parts).strip()

        if not full_text:
            print("Whisper Error: Empty transcript")
            return None

        detected_language = getattr(
            info,
            "language",
            "unknown",
        )

        print(
            "Whisper transcription successful."
        )

        print(
            "Detected language:",
            detected_language,
        )

        print(
            "Characters:",
            len(full_text),
        )

        return full_text

    except Exception as e:
        print(
            "Whisper Transcription Error:",
            type(e).__name__,
            str(e),
        )

        return None


# =========================================================
# YOUTUBE AUDIO FALLBACK
# =========================================================

def get_youtube_transcript_with_whisper(
    url: str,
) -> Optional[str]:
    """
    Fallback method:
    Download YouTube audio using yt-dlp,
    then transcribe it using faster-whisper.
    """

    try:
        import yt_dlp

        print(
            "Trying YouTube audio + Whisper fallback..."
        )

        with tempfile.TemporaryDirectory() as temp_dir:

            output_template = os.path.join(
                temp_dir,
                "lecture.%(ext)s",
            )

            ydl_opts = {
                "format": "bestaudio/best",
                "outtmpl": output_template,
                "quiet": True,
                "no_warnings": True,
                "noplaylist": True,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(
                    url,
                    download=True,
                )

                downloaded_file = ydl.prepare_filename(
                    info
                )

            if not os.path.exists(downloaded_file):
                print(
                    "YouTube Fallback Error:",
                    "Downloaded audio file not found",
                )
                return None

            print(
                "YouTube audio downloaded successfully."
            )

            return transcribe_with_whisper(
                downloaded_file,
                language=None,
            )

    except Exception as e:
        print(
            "YouTube Whisper Fallback Error:",
            type(e).__name__,
            str(e),
        )

        return None


# =========================================================
# YOUTUBE TRANSCRIPT
# =========================================================

def get_transcript(url: str) -> Optional[str]:
    """
    Fetch transcript from YouTube.

    Strategy:
    1. Try YouTube Transcript API
    2. If blocked/fails, try yt-dlp + Whisper
    """

    video_id = extract_video_id(url)

    if not video_id:
        print(
            "Transcript Error:",
            "Invalid YouTube URL",
        )
        return None

    # -----------------------------------------------------
    # METHOD 1: YouTube Transcript API
    # -----------------------------------------------------

    try:
        print(
            "Trying YouTube Transcript API..."
        )

        ytt_api = YouTubeTranscriptApi()

        transcript = ytt_api.fetch(
            video_id,
            languages=[
                "en",
                "en-US",
                "en-GB",
                "hi",
            ],
        )

        text_parts = []

        for item in transcript:
            text = getattr(
                item,
                "text",
                None,
            )

            if text:
                text_parts.append(text)

        full_text = " ".join(
            text_parts
        ).strip()

        if full_text:
            print(
                "YouTube transcript fetched successfully:",
                len(full_text),
                "characters",
            )

            return full_text

        print(
            "YouTube transcript was empty."
        )

    except Exception as e:
        print(
            "YouTube Transcript API Error:",
            type(e).__name__,
            str(e),
        )

    # -----------------------------------------------------
    # METHOD 2: yt-dlp + Whisper fallback
    # -----------------------------------------------------

    print(
        "Primary transcript method failed."
    )

    print(
        "Switching to Whisper fallback..."
    )

    return get_youtube_transcript_with_whisper(
        url
    )


# =========================================================
# LANGUAGE MAPPING
# =========================================================

def get_whisper_language(
    language: str,
) -> Optional[str]:
    """
    Convert frontend language names
    into Whisper language codes.
    """

    normalized_language = (
        language or "English"
    ).strip().lower()

    language_map = {
        "english": "en",
        "hindi": "hi",

        # Auto detection for Hinglish
        "hinglish": None,

        "auto": None,
        "automatic": None,
    }

    return language_map.get(
        normalized_language,
        None,
    )


# =========================================================
# UPLOADED FILE TRANSCRIPTION
# =========================================================

def transcribe_uploaded_file(
    file_path: str,
    language: str = "English",
) -> Optional[str]:
    """
    Transcribe uploaded audio/video
    using faster-whisper.
    """

    if not file_path:
        print(
            "Upload Transcript Error:",
            "File path missing",
        )
        return None

    try:
        whisper_language = get_whisper_language(
            language
        )

        print(
            "Starting uploaded file transcription."
        )

        print(
            "Language:",
            whisper_language or "auto",
        )

        return transcribe_with_whisper(
            file_path=file_path,
            language=whisper_language,
        )

    except ImportError as e:
        print(
            "Upload Transcript Error:",
            "faster-whisper is not installed.",
            str(e),
        )

        return None

    except Exception as e:
        print(
            "Upload Transcript Error:",
            type(e).__name__,
            str(e),
        )

        return None