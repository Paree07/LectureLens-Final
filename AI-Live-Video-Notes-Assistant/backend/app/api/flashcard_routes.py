from fastapi import APIRouter
from pydantic import BaseModel

from app.services.transcript_service import get_transcript
from app.services.ai_service import generate_notes
from app.services.flashcard_service import generate_flashcards


router = APIRouter()


class YouTubeRequest(BaseModel):
    url: str


@router.post("/ai/flashcards")
def ai_flashcards(data: YouTubeRequest):

    try:
        print("=" * 50)
        print("Flashcards request received")
        print("URL:", data.url)
        print("=" * 50)

        # Get structured transcript response
        transcript_result = get_transcript(data.url)

        # Validate response
        if not isinstance(transcript_result, dict):
            return {
                "success": False,
                "error": "invalid_transcript_response",
                "message": "Transcript service returned an invalid response."
            }

        # Check transcript success
        if not transcript_result.get("success"):
            return {
                "success": False,
                "error": transcript_result.get(
                    "error",
                    "transcript_unavailable"
                ),
                "message": transcript_result.get(
                    "message",
                    "Transcript not available."
                )
            }

        # Extract actual transcript string
        transcript = transcript_result.get("transcript")

        if not transcript:
            return {
                "success": False,
                "error": "empty_transcript",
                "message": "Transcript is empty."
            }

        if not isinstance(transcript, str):
            return {
                "success": False,
                "error": "invalid_transcript_type",
                "message": "Transcript must be text."
            }

        print(
            "Transcript characters:",
            len(transcript)
        )

        # Generate notes from actual string
        notes = generate_notes(transcript)

        if not notes:
            return {
                "success": False,
                "error": "notes_generation_failed",
                "message": "Could not generate notes for flashcards."
            }

        # Generate flashcards
        flashcards_result = generate_flashcards(notes)

        if not flashcards_result:
            return {
                "success": False,
                "error": "flashcards_generation_failed",
                "message": "Flashcard service returned empty response."
            }

        # Support dict response
        if isinstance(flashcards_result, dict):
            flashcards = flashcards_result.get(
                "flashcards",
                []
            )
        else:
            flashcards = flashcards_result

        if not flashcards:
            return {
                "success": False,
                "error": "empty_flashcards",
                "message": "No flashcards were generated."
            }

        print("Flashcards generated successfully")

        return {
            "success": True,
            "flashcards": flashcards
        }

    except Exception as e:
        print(
            "FLASHCARDS ROUTE ERROR:",
            type(e).__name__,
            str(e)
        )

        return {
            "success": False,
            "error": type(e).__name__,
            "message": f"Could not generate flashcards: {str(e)}"
        }