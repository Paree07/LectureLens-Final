from fastapi import APIRouter, HTTPException
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
    Fetch transcript first, then generate AI notes.
    """

    try:
        print("\n" + "=" * 60)
        print("AI NOTES REQUEST RECEIVED")
        print("URL:", data.url)
        print("=" * 60)

        # -----------------------------------------
        # FETCH TRANSCRIPT
        # -----------------------------------------

        transcript_result = get_transcript(data.url)

        print(
            "Transcript result type:",
            type(transcript_result).__name__
        )

        # -----------------------------------------
        # VALIDATE TRANSCRIPT RESPONSE
        # -----------------------------------------

        if not isinstance(transcript_result, dict):
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

        if not transcript_result.get("success"):
            message = transcript_result.get(
                "message",
                "Transcript not available."
            )

            raise HTTPException(
                status_code=422,
                detail=message
            )

        # -----------------------------------------
        # EXTRACT TRANSCRIPT
        # -----------------------------------------

        transcript = transcript_result.get("transcript")

        if not transcript:
            raise HTTPException(
                status_code=422,
                detail=(
                    "Transcript was empty, so AI notes "
                    "could not be generated."
                )
            )

        if not isinstance(transcript, str):
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
            "Transcript characters:",
            len(transcript)
        )

        # -----------------------------------------
        # GENERATE NOTES
        # -----------------------------------------

        notes = generate_notes(transcript)

        # -----------------------------------------
        # VALIDATE NOTES
        # -----------------------------------------

        if not isinstance(notes, dict):
            raise HTTPException(
                status_code=500,
                detail=(
                    "AI service returned invalid notes."
                )
            )

        if not notes:
            raise HTTPException(
                status_code=500,
                detail="AI service returned empty notes."
            )

        print("=" * 60)
        print("AI NOTES GENERATED SUCCESSFULLY")
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
        print("TYPE:", type(e).__name__)
        print("ERROR:", repr(e))
        print("=" * 60 + "\n")

        # Important:
        # During local testing expose actual error
        raise HTTPException(
            status_code=500,
            detail=(
                f"AI notes generation failed: "
                f"{type(e).__name__}: {str(e)}"
            )
        )