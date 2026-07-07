from fastapi import APIRouter
from pydantic import BaseModel

from app.services.transcript_service import get_transcript
from app.services.ai_service import generate_notes


router = APIRouter()


# =========================================================
# REQUEST MODEL
# =========================================================

class NotesRequest(BaseModel):
    url: str


# =========================================================
# GENERATE AI NOTES
# =========================================================

@router.post("/ai/notes")
def generate_ai_notes(data: NotesRequest):
    """
    Generate AI notes from a YouTube video transcript.

    Flow:
    1. Try to fetch transcript
    2. Check structured transcript response
    3. If unavailable, return clean error
    4. If available, send transcript text to AI
    5. Return generated notes
    """

    try:
        print("AI Notes request received.")
        print("URL:", data.url)

        # -----------------------------------------
        # STEP 1: FETCH TRANSCRIPT
        # -----------------------------------------

        transcript_result = get_transcript(
            data.url
        )

        # -----------------------------------------
        # STEP 2: VALIDATE TRANSCRIPT RESPONSE
        # -----------------------------------------

        if not transcript_result:
            print(
                "AI Notes Error:",
                "Transcript service returned no response."
            )

            return {
                "success": False,
                "notes": None,
                "error": "transcript_service_error",
                "message": "Transcript service returned no response."
            }

        # -----------------------------------------
        # STEP 3: HANDLE TRANSCRIPT FAILURE
        # -----------------------------------------

        if not transcript_result.get(
            "success",
            False
        ):
            error_code = transcript_result.get(
                "error",
                "transcript_unavailable"
            )

            error_message = transcript_result.get(
                "message",
                "Transcript not available."
            )

            print(
                "AI Notes Transcript Error:",
                error_code,
                error_message
            )

            return {
                "success": False,
                "notes": None,
                "error": error_code,
                "message": error_message
            }

        # -----------------------------------------
        # STEP 4: EXTRACT ACTUAL TRANSCRIPT TEXT
        # -----------------------------------------

        transcript = transcript_result.get(
            "transcript"
        )

        if not transcript:
            print(
                "AI Notes Error:",
                "Transcript text is empty."
            )

            return {
                "success": False,
                "notes": None,
                "error": "empty_transcript",
                "message": "Transcript text is empty."
            }

        print(
            "Transcript ready for AI notes:",
            len(transcript),
            "characters"
        )

        # -----------------------------------------
        # STEP 5: GENERATE NOTES
        # -----------------------------------------

        notes = generate_notes(
            transcript
        )

        # -----------------------------------------
        # STEP 6: VALIDATE AI RESPONSE
        # -----------------------------------------

        if not notes:
            print(
                "AI Notes Error:",
                "AI service returned empty notes."
            )

            return {
                "success": False,
                "notes": None,
                "error": "empty_ai_response",
                "message": "AI service returned empty notes."
            }

        # -----------------------------------------
        # SUCCESS
        # -----------------------------------------

        print(
            "AI notes generated successfully."
        )

        return {
            "success": True,
            "notes": notes,
            "error": None,
            "message": "AI notes generated successfully."
        }

    except Exception as e:
        print(
            "AI Notes Error:",
            type(e).__name__,
            str(e)
        )

        return {
            "success": False,
            "notes": None,
            "error": type(e).__name__,
            "message": "Could not generate AI notes."
        }