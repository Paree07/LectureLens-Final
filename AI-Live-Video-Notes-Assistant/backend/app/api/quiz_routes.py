from fastapi import APIRouter
from pydantic import BaseModel

from app.services.transcript_service import get_transcript
from app.services.ai_service import generate_notes
from app.services.quiz_service import generate_quiz


router = APIRouter()


class YouTubeRequest(BaseModel):
    url: str


@router.post("/ai/quiz")
def ai_quiz(data: YouTubeRequest):

    try:
        print("=" * 50)
        print("Quiz request received")
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

        # Generate notes
        notes = generate_notes(transcript)

        if not notes:
            return {
                "success": False,
                "error": "notes_generation_failed",
                "message": "Could not generate notes for quiz."
            }

        # Generate quiz
        quiz_result = generate_quiz(notes)

        if not quiz_result:
            return {
                "success": False,
                "error": "quiz_generation_failed",
                "message": "Quiz service returned empty response."
            }

        # Support dict response
        if isinstance(quiz_result, dict):
            quiz = quiz_result.get(
                "quiz",
                []
            )
        else:
            quiz = quiz_result

        if not quiz:
            return {
                "success": False,
                "error": "empty_quiz",
                "message": "No quiz questions were generated."
            }

        print("Quiz generated successfully")

        return {
            "success": True,
            "quiz": quiz
        }

    except Exception as e:
        print(
            "QUIZ ROUTE ERROR:",
            type(e).__name__,
            str(e)
        )

        return {
            "success": False,
            "error": type(e).__name__,
            "message": f"Could not generate quiz: {str(e)}"
        }