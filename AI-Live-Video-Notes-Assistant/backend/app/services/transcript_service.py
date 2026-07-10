import os
import re
import shutil
import tempfile
from typing import Optional, Dict, Any

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    RequestBlocked,
    IpBlocked,
    VideoUnavailable,
    TranscriptsDisabled,
    NoTranscriptFound,
)




# =========================================================
# GLOBAL WHISPER MODEL CACHE
# =========================================================

_whisper_model = None


def get_whisper_model():
    """
    Load Whisper model once and reuse it.
    """

    global _whisper_model

    if _whisper_model is None:
        from faster_whisper import WhisperModel

        print("=" * 60)
        print("Loading Whisper base model...")

        _whisper_model = WhisperModel(
            "base",
            device="cpu",
            compute_type="int8",
        )

        print("Whisper model loaded successfully.")

    return _whisper_model


# =========================================================
# YOUTUBE VIDEO ID EXTRACTION
# =========================================================

def extract_video_id(url: str) -> Optional[str]:
    """
    Extract YouTube video ID from common URL formats.
    """

    if not url:
        return None

    patterns = [
        r"(?:youtube\.com/watch\?(?:.*&)?v=)([A-Za-z0-9_-]{11})",
        r"(?:youtu\.be/)([A-Za-z0-9_-]{11})",
        r"(?:youtube\.com/embed/)([A-Za-z0-9_-]{11})",
        r"(?:youtube\.com/shorts/)([A-Za-z0-9_-]{11})",
        r"(?:youtube\.com/live/)([A-Za-z0-9_-]{11})",
    ]

    for pattern in patterns:
        match = re.search(
            pattern,
            url,
            flags=re.IGNORECASE,
        )

        if match:
            return match.group(1)

    return None


# =========================================================
# TRANSCRIBE AUDIO WITH WHISPER
# =========================================================

def transcribe_audio_with_whisper(
    file_path: str,
    language: Optional[str] = None,
) -> Optional[str]:
    """
    Transcribe local audio/video file using faster-whisper.
    """

    try:
        model = get_whisper_model()

        print("=" * 60)
        print("Starting Whisper transcription...")
        print("File:", file_path)
        print("Language:", language or "auto")

        segments, info = model.transcribe(
            file_path,
            language=language,
            beam_size=1,
            vad_filter=True,
            condition_on_previous_text=False,
        )

        text_parts = []

        for segment in segments:
            text = getattr(
                segment,
                "text",
                "",
            )

            if isinstance(text, str):
                cleaned_text = text.strip()

                if cleaned_text:
                    text_parts.append(cleaned_text)

        full_text = " ".join(text_parts).strip()

        if not full_text:
            print(
                "Whisper returned empty transcript."
            )
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
# YOUTUBE AUDIO + WHISPER FALLBACK
# =========================================================

def get_transcript_with_whisper_fallback(
    url: str,
) -> Optional[str]:
    """
    Fallback:

    1. Download YouTube audio using yt-dlp
    2. Transcribe with faster-whisper
    3. Delete temporary files
    """

    temp_dir = None

    try:
        import yt_dlp

        print("=" * 60)
        print("Trying yt-dlp + Whisper fallback...")

        temp_dir = tempfile.mkdtemp(
            prefix="lecturelens_"
        )

        output_template = os.path.join(
            temp_dir,
            "audio.%(ext)s",
        )

        ydl_options = {
        "format": "bestaudio[ext=m4a]/bestaudio/best",
        "outtmpl": output_template,
        "quiet": False,
        "no_warnings": False,
        "noplaylist": True,
        "retries": 3,
        "fragment_retries": 3,
        "socket_timeout": 30,
        "max_filesize": 200 * 1024 * 1024,

        # Try an alternate YouTube player client.
        "extractor_args": {
        "youtube": {
                 "player_client": ["android_vr"],
                }
            },
        }
        with yt_dlp.YoutubeDL(
            ydl_options
        ) as ydl:

            print("Downloading YouTube audio...")

            info = ydl.extract_info(
                url,
                download=True,
            )

            downloaded_file = ydl.prepare_filename(
                info
            )

        print(
            "yt-dlp reported file:",
            downloaded_file,
        )

        # Sometimes actual extension/path differs
        if not os.path.exists(downloaded_file):

            files = [
                os.path.join(
                    temp_dir,
                    name,
                )
                for name in os.listdir(temp_dir)
                if os.path.isfile(
                    os.path.join(
                        temp_dir,
                        name,
                    )
                )
            ]

            if not files:
                print(
                    "Whisper fallback failed: "
                    "No downloaded audio file found."
                )
                return None

            # Prefer largest file
            downloaded_file = max(
                files,
                key=os.path.getsize,
            )

        print(
            "Audio downloaded successfully:",
            downloaded_file,
        )

        transcript = transcribe_audio_with_whisper(
            file_path=downloaded_file,
            language=None,
        )

        return transcript

    except Exception as e:
        print(
            "YouTube Whisper Fallback Error:",
            type(e).__name__,
            str(e),
        )

        return None

    finally:
        if temp_dir and os.path.exists(temp_dir):

            try:
                shutil.rmtree(
                    temp_dir,
                    ignore_errors=True,
                )

                print(
                    "Temporary YouTube files cleaned."
                )

            except Exception as cleanup_error:
                print(
                    "Cleanup Error:",
                    str(cleanup_error),
                )


# =========================================================
# MAIN YOUTUBE TRANSCRIPT FUNCTION
# =========================================================

def get_transcript(
    url: str,
) -> Dict[str, Any]:
    """
    Transcript strategy:

    METHOD 0:
        Supadata

    METHOD 1:
        YouTube Transcript API

    METHOD 2:
        yt-dlp + Whisper

    Returns structured response.
    """

    print("=" * 60)
    print("Starting transcript request...")
    print("URL:", url)

    video_id = extract_video_id(url)

    if not video_id:
        print("Invalid YouTube URL.")

        return {
            "success": False,
            "transcript": None,
            "source": None,
            "error": "invalid_youtube_url",
            "message": "Invalid YouTube URL.",
        }

    print("Video ID:", video_id)


    # =====================================================
    # METHOD 1: YOUTUBE TRANSCRIPT API
    # =====================================================

    print("=" * 60)
    print("METHOD 1: YOUTUBE TRANSCRIPT API")

    method_1_error_code = None

    try:
        print(
            "Trying YouTube transcript API..."
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

            if isinstance(text, str):
                cleaned_text = text.strip()

                if cleaned_text:
                    text_parts.append(
                        cleaned_text
                    )

        full_text = " ".join(
            text_parts
        ).strip()

        if full_text:
            print(
                "YouTube transcript fetched successfully:",
                len(full_text),
                "characters",
            )

            return {
                "success": True,
                "transcript": full_text,
                "source": "youtube_captions",
                "error": None,
                "message": (
                    "Transcript fetched successfully "
                    "from YouTube captions."
                ),
            }

        print(
            "YouTube captions returned empty text."
        )

        method_1_error_code = (
            "empty_captions"
        )

    except (RequestBlocked, IpBlocked) as e:
        print(
            "YouTube blocked this server's IP:",
            str(e),
        )

        method_1_error_code = "ip_blocked"

    except TranscriptsDisabled:
        print(
            "Captions are disabled for this video."
        )

        method_1_error_code = (
            "captions_disabled"
        )

    except NoTranscriptFound:
        print(
            "No transcript found in requested languages."
        )

        method_1_error_code = (
            "no_transcript_found"
        )

    except VideoUnavailable:
        print(
            "Video unavailable, private, deleted, "
            "or region locked."
        )

        method_1_error_code = (
            "video_unavailable"
        )

    except Exception as e:
        print(
            "YouTube Transcript API Error:",
            type(e).__name__,
            str(e),
        )

        method_1_error_code = (
            "unknown_error"
        )

    print(
        "Primary transcript method failed:",
        method_1_error_code,
    )

    # =====================================================
    # METHOD 2: YT-DLP + WHISPER
    # =====================================================

    print("=" * 60)
    print("METHOD 2: YT-DLP + WHISPER")

    whisper_transcript = (
        get_transcript_with_whisper_fallback(
            url
        )
    )

    if whisper_transcript:
        print(
            "SUCCESS: Transcript generated via Whisper."
        )

        return {
            "success": True,
            "transcript": whisper_transcript,
            "source": "whisper_fallback",
            "error": None,
            "message": (
                "Transcript generated from video "
                "audio using Whisper."
            ),
        }

    # =====================================================
    # ALL METHODS FAILED
    # =====================================================

    print("=" * 60)
    print("ALL TRANSCRIPT METHODS FAILED")

    final_error = (
        method_1_error_code
        or "all_transcript_methods_failed"
    )

    return {
        "success": False,
        "transcript": None,
        "source": None,
        "error": final_error,
        "message": (
            "Could not retrieve or generate a transcript. "
            "Supadata, YouTube captions, and Whisper "
            "fallback all failed."
        ),
    }


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
            "Upload Transcript Error: "
            "File path missing."
        )
        return None

    if not os.path.exists(file_path):
        print(
            "Upload Transcript Error: "
            "File does not exist:",
            file_path,
        )
        return None

    whisper_language = get_whisper_language(
        language
    )

    return transcribe_audio_with_whisper(
        file_path=file_path,
        language=whisper_language,
    )