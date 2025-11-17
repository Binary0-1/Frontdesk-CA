import os
import json
import google.generativeai as genai
from config import settings


genai.configure(api_key=settings.GEMINI_API_KEY)


async def extract_kb_metadata(question: str, answer: str):
    """
    Uses Gemini to convert a (question, answer) pair into structured KB metadata.
    Always returns a dict, with safe fallback on failure.
    """

    prompt = f"""
    Extract structured metadata from this Q/A pair.
    Return ONLY valid JSON — no explanation.

    Question: "{question}"
    Answer: "{answer}"

    Fields:
    - key: machine-friendly identifier (snake_case)
    - canonical_question: clean rewritten question
    - category: one-word category
    - tags: list of keywords

    Output JSON only.
    """

    model = genai.GenerativeModel("gemini-2.5-flash")

    try:
        resp = await model.generate_content_async(prompt)
        return json.loads(resp.text)

    except Exception:
        return {
            "key": "uncategorized",
            "canonical_question": question,
            "category": "general",
            "tags": []
        }
