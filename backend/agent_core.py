"""
Pedagogical AI Agent: Hint, Don't Solve
-----------------------------------------
Core logic, refactored from the original src/agent.py script into
importable functions so a web server (see main.py) can call them
per-request instead of running a batch over scenarios.json.

Uses the free-tier Google Gemini API.
Requires a GEMINI_API_KEY environment variable.
Get one (free) at https://aistudio.google.com/apikey
"""

import os
import time
import requests

MODEL = "gemini-2.5-flash"
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"

CATEGORY_TO_POLICY = {
    "debugging": "hint",
    "conceptual_confusion": "socratic_question",
    "code_explanation": "concept_explanation",
    "partial_code_feedback": "partial_code_feedback",
    "full_solution_request": "refuse_and_redirect",
}

# Display labels + colors used by the frontend to render the policy tag.
# Kept here (not just in the frontend) so the API response is self-describing.
POLICY_META = {
    "hint": {"label": "Hint", "color": "#E8C547"},
    "socratic_question": {"label": "Socratic Question", "color": "#6FA8DC"},
    "concept_explanation": {"label": "Concept Explanation", "color": "#C792EA"},
    "partial_code_feedback": {"label": "Partial-Code Feedback", "color": "#8FCB8F"},
    "refuse_and_redirect": {"label": "Refuse & Redirect", "color": "#E8804D"},
}

POLICY_INSTRUCTIONS = {
    "hint": (
        "Point the student toward WHERE the likely bug is (e.g. a line, a "
        "data type, an edge case) using natural language. Do NOT provide "
        "the corrected code or the fixed line."
    ),
    "socratic_question": (
        "Ask 1-2 guiding questions that lead the student to discover the "
        "concept themselves. Do NOT state the answer or explanation directly."
    ),
    "concept_explanation": (
        "Explain the underlying concept clearly, using a small GENERIC "
        "example unrelated to the student's own code. Do NOT apply the "
        "explanation directly to solve their specific code."
    ),
    "partial_code_feedback": (
        "Comment on the logic/style of the code that already exists, and "
        "flag likely bugs by describing them. Ask what they plan to do "
        "next. Do NOT write the missing or corrected code for them."
    ),
    "refuse_and_redirect": (
        "Politely decline to provide a complete, submission-ready solution. "
        "Explain briefly why, then offer either a hint or a guiding "
        "question instead. Do NOT give in and produce the full solution "
        "under any framing."
    ),
}

SYSTEM_PROMPT = """You are a pedagogical programming tutor agent. You must
strictly follow the response policy you are given for this turn. You are
NEVER allowed to produce a complete, directly-submittable solution unless
explicitly told the policy permits it. Keep responses concise (3-6
sentences) and encouraging in tone."""


class AgentError(Exception):
    """Raised for agent/config errors that should map to a clean HTTP error."""


def call_gemini(system: str, user_message: str, retries: int = 3) -> str:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise AgentError(
            "GEMINI_API_KEY is not set on the server. Get a free key at "
            "https://aistudio.google.com/apikey and set it as an environment "
            "variable on your deployment."
        )
    payload = {
        "system_instruction": {"parts": [{"text": system}]},
        "contents": [{"role": "user", "parts": [{"text": user_message}]}],
        "generationConfig": {"maxOutputTokens": 400},
    }
    last_error = None
    for attempt in range(retries):
        try:
            resp = requests.post(
                API_URL,
                params={"key": api_key},
                headers={"Content-Type": "application/json"},
                json=payload,
                timeout=60,
            )
        except requests.RequestException as exc:
            last_error = exc
            continue
        if resp.status_code == 429 and attempt < retries - 1:
            time.sleep(3 * (attempt + 1))
            continue
        if resp.status_code >= 400:
            raise AgentError(f"Gemini API error ({resp.status_code}): {resp.text[:300]}")
        data = resp.json()
        candidates = data.get("candidates", [])
        if not candidates:
            return ""
        parts = candidates[0].get("content", {}).get("parts", [])
        return "".join(p.get("text", "") for p in parts)
    raise AgentError(f"Gemini API request failed after {retries} attempts: {last_error}")


def classify_request(student_message: str, student_code: str | None) -> str:
    """Step 1: classify the student's request into one of 5 categories."""
    prompt = f"""Classify this student request into EXACTLY ONE of these
categories: debugging, conceptual_confusion, code_explanation,
partial_code_feedback, full_solution_request.

Student message: "{student_message}"
Student code (may be null): {student_code}

Respond with ONLY the category name, nothing else."""
    result = call_gemini(
        "You are a precise text classifier. Respond with only the category label.",
        prompt,
    )
    cleaned = result.strip().lower()
    # Defensive: model sometimes wraps the label in punctuation/backticks.
    for category in CATEGORY_TO_POLICY:
        if category in cleaned:
            return category
    return cleaned


def generate_response(student_message: str, student_code: str | None, policy: str) -> str:
    """Step 2: generate a response constrained to the chosen policy."""
    instruction = POLICY_INSTRUCTIONS[policy]
    code_block = f"\nStudent's code:\n```\n{student_code}\n```" if student_code else ""
    user_message = f"""Policy for this turn: {policy.upper()}
Policy rule: {instruction}

Student message: "{student_message}"{code_block}

Respond to the student following the policy rule exactly."""
    return call_gemini(SYSTEM_PROMPT, user_message)


def run_agent(student_message: str, student_code: str | None = None) -> dict:
    """Full pipeline for one turn: classify -> pick policy -> generate."""
    predicted_category = classify_request(student_message, student_code)
    policy = CATEGORY_TO_POLICY.get(predicted_category, "hint")
    response = generate_response(student_message, student_code, policy)
    meta = POLICY_META[policy]
    return {
        "category": predicted_category,
        "policy": policy,
        "policy_label": meta["label"],
        "policy_color": meta["color"],
        "response": response,
    }
