from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from app.services.transcript_service import get_transcript
from app.services.ai_service import generate_notes


router = APIRouter()


# =========================================================
# REQUEST MODEL
# =========================================================

class NotesRequest(BaseModel):
    url: str
    transcript: Optional[str] = None


# =========================================================
# GENERATE AI NOTES
# =========================================================

@router.post("/ai/notes")
def generate_ai_notes(data: NotesRequest):
    """
    Generate AI notes.

    Priority:
    1. Use transcript sent by frontend
    2. If missing, fetch transcript from URL
    """

    try:
        print("\n" + "=" * 60)
        print("AI NOTES REQUEST RECEIVED")
        print("URL:", data.url)
        print(
            "Frontend transcript received:",
            bool(data.transcript)
        )
        print("=" * 60)

        transcript = None

        # -----------------------------------------
        # METHOD 1:
        # USE TRANSCRIPT SENT BY FRONTEND
        # -----------------------------------------

        if (
            isinstance(data.transcript, str)
            and data.transcript.strip()
        ):
            transcript = data.transcript.strip()

            print(
                "Using transcript sent by frontend."
            )

            print(
                "Transcript characters:",
                len(transcript)
            )

        # -----------------------------------------
        # METHOD 2:
        # FALLBACK TO BACKEND TRANSCRIPT FETCH
        # -----------------------------------------

        else:
            print(
                "No frontend transcript received."
            )

            print(
                "Fetching transcript from backend..."
            )

            transcript_result = get_transcript(
                data.url
            )

            print(
                "Transcript result type:",
                type(transcript_result).__name__
            )

            if not isinstance(
                transcript_result,
                dict
            ):
                raise HTTPException(
                    status_code=500,
                    detail=(
                        "Transcript service returned "
                        "an invalid response."
                    )
                )

            print(
                "Transcript success:",
                transcript_result.get("success")
            )

            if not transcript_result.get(
                "success"
            ):
                message = transcript_result.get(
                    "message",
                    "Transcript not available."
                )

                raise HTTPException(
                    status_code=422,
                    detail=message
                )

            transcript = transcript_result.get(
                "transcript"
            )

        # -----------------------------------------
        # VALIDATE TRANSCRIPT
        # -----------------------------------------

        if not transcript:
            raise HTTPException(
                status_code=422,
                detail=(
                    "Transcript was empty, so AI notes "
                    "could not be generated."
                )
            )

        if not isinstance(
            transcript,
            str
        ):
            raise HTTPException(
                status_code=500,
                detail="Transcript must be text."
            )

        transcript = transcript.strip()

        if len(transcript) < 20:
            raise HTTPException(
                status_code=422,
                detail="Transcript is too short."
            )

        print(
            "Final transcript characters:",
            len(transcript)
        )

        # -----------------------------------------
        # GENERATE NOTES
        # -----------------------------------------

        notes = generate_notes(
            transcript
        )

        # -----------------------------------------
        # VALIDATE NOTES
        # -----------------------------------------

        if not isinstance(
            notes,
            dict
        ):
            raise HTTPException(
                status_code=500,
                detail=(
                    "AI service returned invalid notes."
                )
            )

        if not notes:
            raise HTTPException(
                status_code=500,
                detail=(
                    "AI service returned empty notes."
                )
            )

        print("=" * 60)
        print(
            "AI NOTES GENERATED SUCCESSFULLY"
        )
        print("=" * 60 + "\n")

        # -----------------------------------------
        # SUCCESS RESPONSE
        # -----------------------------------------

        return {
            "success": True,
            "notes": notes
        }

    except HTTPException:
        raise

    except Exception as e:
        print("\n" + "=" * 60)
        print("AI NOTES ROUTE ERROR")
        print(
            "TYPE:",
            type(e).__name__
        )
        print(
            "ERROR:",
            repr(e)
        )
        print("=" * 60 + "\n")

        raise HTTPException(
            status_code=500,
            detail=(
                f"AI notes generation failed: "
                f"{type(e).__name__}: {str(e)}"
            )
        )