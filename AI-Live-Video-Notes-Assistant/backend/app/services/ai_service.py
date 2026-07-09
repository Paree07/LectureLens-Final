import os
import json
import re

from dotenv import load_dotenv
from groq import Groq


# =========================================================
# LOAD ENVIRONMENT VARIABLES
# =========================================================

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")


# =========================================================
# CREATE GROQ CLIENT
# =========================================================

def get_groq_client():
    """
    Create client lazily so the entire backend does not crash
    during import if environment variables are misconfigured.
    """

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise ValueError(
            "GROQ_API_KEY not found. "
            "Add GROQ_API_KEY to backend/.env"
        )

    return Groq(api_key=api_key)


# =========================================================
# CLEAN AI JSON RESPONSE
# =========================================================

def clean_json_response(text: str):
    """
    Extract and parse a JSON object from AI response.
    """

    if not text:
        raise ValueError(
            "AI returned an empty response"
        )

    text = text.strip()

    # Remove markdown fences
    text = re.sub(
        r"^```json\s*",
        "",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"^```\s*",
        "",
        text
    )

    text = re.sub(
        r"\s*```$",
        "",
        text
    )

    text = text.strip()

    # First try direct JSON parse
    try:
        parsed = json.loads(text)

        if not isinstance(parsed, dict):
            raise ValueError(
                "AI JSON response must be an object"
            )

        return parsed

    except json.JSONDecodeError:
        pass

    # Fallback: extract outer JSON object
    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1 or end <= start:
        raise ValueError(
            "No valid JSON object found "
            "in AI response"
        )

    json_text = text[start:end + 1]

    try:
        parsed = json.loads(json_text)

    except json.JSONDecodeError as e:
        print("INVALID JSON TEXT:")
        print(json_text)

        raise ValueError(
            f"AI returned invalid JSON: {str(e)}"
        )

    if not isinstance(parsed, dict):
        raise ValueError(
            "AI JSON response must be an object"
        )

    return parsed


# =========================================================
# REDUCE LONG TRANSCRIPTS
# =========================================================

def reduce_transcript(
    transcript: str,
    max_chars: int = 10000
):
    """
    Reduce long transcript while preserving:
    - beginning
    - middle
    - ending
    """

    if not transcript:
        return ""

    transcript = transcript.strip()

    if len(transcript) <= max_chars:
        print(
            "Transcript within safe limit:",
            len(transcript),
            "characters"
        )

        return transcript

    print(
        "Long transcript detected:",
        len(transcript),
        "characters"
    )

    part_size = max_chars // 3

    beginning = transcript[:part_size]

    middle_start = max(
        0,
        (len(transcript) // 2)
        - (part_size // 2)
    )

    middle = transcript[
        middle_start:
        middle_start + part_size
    ]

    ending = transcript[-part_size:]

    reduced = (
        "LECTURE BEGINNING:\n\n"
        f"{beginning}\n\n"
        "LECTURE MIDDLE:\n\n"
        f"{middle}\n\n"
        "LECTURE END:\n\n"
        f"{ending}"
    )

    print(
        "Transcript reduced to:",
        len(reduced),
        "characters"
    )

    return reduced


# =========================================================
# NORMALIZE NOTES
# =========================================================

def normalize_notes(notes: dict):
    """
    Ensure frontend always receives predictable structure.
    """

    summary = notes.get("summary", "")

    key_concepts = notes.get(
        "key_concepts",
        []
    )

    definitions = notes.get(
        "definitions",
        []
    )

    exam_tips = notes.get(
        "exam_tips",
        []
    )

    # -----------------------------------------
    # SUMMARY
    # -----------------------------------------

    if not isinstance(summary, str):
        summary = str(summary)

    # -----------------------------------------
    # KEY CONCEPTS
    # -----------------------------------------

    if not isinstance(key_concepts, list):
        key_concepts = []

    normalized_concepts = []

    for item in key_concepts:
        if isinstance(item, str):
            normalized_concepts.append(item)

        elif isinstance(item, dict):
            value = (
                item.get("concept")
                or item.get("title")
                or item.get("name")
                or item.get("text")
            )

            if value:
                normalized_concepts.append(
                    str(value)
                )

    # -----------------------------------------
    # DEFINITIONS
    # -----------------------------------------

    if not isinstance(definitions, list):
        definitions = []

    normalized_definitions = []

    for item in definitions:

        if isinstance(item, dict):
            term = (
                item.get("term")
                or item.get("name")
                or item.get("title")
                or ""
            )

            meaning = (
                item.get("meaning")
                or item.get("definition")
                or item.get("description")
                or ""
            )

            if term or meaning:
                normalized_definitions.append({
                    "term": str(term),
                    "meaning": str(meaning)
                })

        elif isinstance(item, str):
            normalized_definitions.append({
                "term": "Concept",
                "meaning": item
            })

    # -----------------------------------------
    # EXAM TIPS
    # -----------------------------------------

    if not isinstance(exam_tips, list):
        exam_tips = []

    normalized_tips = []

    for item in exam_tips:
        if isinstance(item, str):
            normalized_tips.append(item)

        elif isinstance(item, dict):
            value = (
                item.get("tip")
                or item.get("text")
                or item.get("description")
            )

            if value:
                normalized_tips.append(
                    str(value)
                )

    return {
        "summary": summary.strip(),
        "key_concepts": normalized_concepts,
        "definitions": normalized_definitions,
        "exam_tips": normalized_tips
    }


# =========================================================
# VALIDATE NOTES
# =========================================================

def validate_notes(notes: dict):

    if not isinstance(notes, dict):
        raise ValueError(
            "Notes must be a JSON object"
        )

    required_keys = [
        "summary",
        "key_concepts",
        "definitions",
        "exam_tips"
    ]

    for key in required_keys:
        if key not in notes:
            raise ValueError(
                f"Missing required field: {key}"
            )

    if not notes["summary"]:
        raise ValueError(
            "AI returned empty summary"
        )

    if not isinstance(
        notes["key_concepts"],
        list
    ):
        raise ValueError(
            "key_concepts must be a list"
        )

    if not isinstance(
        notes["definitions"],
        list
    ):
        raise ValueError(
            "definitions must be a list"
        )

    if not isinstance(
        notes["exam_tips"],
        list
    ):
        raise ValueError(
            "exam_tips must be a list"
        )


# =========================================================
# GENERATE AI NOTES
# =========================================================

def generate_notes(transcript: str):

    if not transcript:
        raise ValueError(
            "Transcript is empty"
        )

    if not isinstance(transcript, str):
        raise TypeError(
            "Transcript must be a string"
        )

    transcript = transcript.strip()

    if len(transcript) < 20:
        raise ValueError(
            "Transcript is too short"
        )

    # -----------------------------------------
    # REDUCE TRANSCRIPT
    # -----------------------------------------

    safe_transcript = reduce_transcript(
    transcript,
    max_chars=4500
    )

    # -----------------------------------------
    # CREATE CLIENT
    # -----------------------------------------

    client = get_groq_client()

    # -----------------------------------------
    # SYSTEM PROMPT
    # -----------------------------------------

    system_prompt = (
        "You are an expert multilingual academic "
        "lecture assistant. You understand English, "
        "Hindi, Hinglish, and mixed-language lectures. "
        "Always produce final study notes in natural "
        "English. Preserve technical meaning. "
        "Return only valid JSON. Do not use markdown."
    )

    # -----------------------------------------
    # USER PROMPT
    # -----------------------------------------

    user_prompt = f"""
Analyze the following lecture transcript.

The transcript may contain:
- English
- Hindi
- Hinglish
- Mixed Hindi-English
- Speech-to-text mistakes

Understand the meaning of the lecture and generate
clear academic study notes in ENGLISH.

Return ONLY valid JSON using exactly this structure:

{{
  "summary": "Clear concise English summary",
  "key_concepts": [
    "Concept 1",
    "Concept 2",
    "Concept 3",
    "Concept 4",
    "Concept 5"
  ],
  "definitions": [
    {{
      "term": "Important term",
      "meaning": "Clear explanation"
    }}
  ],
  "exam_tips": [
    "Exam tip 1",
    "Exam tip 2"
  ]
}}

Rules:
- Output English only.
- Do not output markdown.
- Do not use code fences.
- Do not write text before JSON.
- Do not write text after JSON.
- Give 5 to 8 key concepts.
- Give 3 to 6 definitions when possible.
- Give 2 to 5 useful exam tips.
- Do not invent unsupported facts.
- Correct obvious transcript mistakes only when meaning is clear.
- Preserve formulas and technical terminology.

LECTURE TRANSCRIPT:

{safe_transcript}
"""

    # -----------------------------------------
    # DEBUG
    # -----------------------------------------

    print("\n" + "=" * 60)
    print("GENERATING AI NOTES")
    print(
        "Original transcript characters:",
        len(transcript)
    )
    print(
        "Characters sent to AI:",
        len(safe_transcript)
    )
    print(
        "Model:",
        "llama-3.1-8b-instant"
    )
    print("=" * 60)

    # -----------------------------------------
    # CALL GROQ
    # -----------------------------------------

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",

            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],

            temperature=0.1,

            # Intentionally removed response_format
            # for broader compatibility

            max_tokens=1600
        )

    except Exception as e:
        print("\n" + "=" * 60)
        print("GROQ API CALL FAILED")
        print("TYPE:", type(e).__name__)
        print("ERROR:", repr(e))
        print("=" * 60 + "\n")

        raise RuntimeError(
            f"Groq API call failed: "
            f"{type(e).__name__}: {str(e)}"
        )

    # -----------------------------------------
    # VALIDATE GROQ RESPONSE
    # -----------------------------------------

    if not response:
        raise ValueError(
            "Groq returned no response"
        )

    if not response.choices:
        raise ValueError(
            "Groq returned no choices"
        )

    result = response.choices[0].message.content

    if not result:
        raise ValueError(
            "Groq returned empty content"
        )

    # -----------------------------------------
    # DEBUG RAW RESPONSE
    # -----------------------------------------

    print("\nRAW AI RESPONSE:")
    print(result)

    # -----------------------------------------
    # PARSE JSON
    # -----------------------------------------

    try:
        notes = clean_json_response(result)

    except Exception as e:
        print("\n" + "=" * 60)
        print("AI JSON PARSING FAILED")
        print("TYPE:", type(e).__name__)
        print("ERROR:", repr(e))
        print("RAW RESPONSE:")
        print(result)
        print("=" * 60 + "\n")

        raise

    # -----------------------------------------
    # NORMALIZE
    # -----------------------------------------

    notes = normalize_notes(notes)

    # -----------------------------------------
    # VALIDATE
    # -----------------------------------------

    validate_notes(notes)

    print("\n" + "=" * 60)
    print("AI NOTES GENERATED SUCCESSFULLY")
    print("=" * 60 + "\n")

    return notes