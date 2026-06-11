import json
from anthropic import Anthropic
from backend.config import ANTHROPIC_API_KEY

client = Anthropic(api_key=ANTHROPIC_API_KEY)

_sessions: dict[str, list[dict]] = {}


def get_session(session_id: str) -> list[dict]:
    if session_id not in _sessions:
        _sessions[session_id] = []
    return _sessions[session_id]


def add_turn(session_id: str, question: str, answer: str, cypher: str = ""):
    history = get_session(session_id)
    history.append({"role": "user", "question": question, "cypher": cypher, "answer": answer})
    if len(history) > 20:
        _sessions[session_id] = history[-20:]


def resolve_references(session_id: str, question: str) -> str:
    history = get_session(session_id)
    if not history:
        return question

    needs_resolution = any(w in question.lower() for w in [
        "it", "they", "them", "that", "this", "those", "the company",
        "the person", "he", "she", "his", "her", "their",
        "what about", "how about", "and", "also",
    ])

    if not needs_resolution:
        return question

    context_lines = []
    for turn in history[-5:]:
        context_lines.append(f"Q: {turn['question']}")
        context_lines.append(f"A: {turn['answer'][:200]}")

    prompt = f"""Given this conversation history:
{chr(10).join(context_lines)}

The user now asks: "{question}"

Rewrite this question to be self-contained by resolving any pronouns or references to previous context. If the question is already self-contained, return it unchanged.

Return ONLY the rewritten question, nothing else."""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=256,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text.strip()


def clear_session(session_id: str):
    _sessions.pop(session_id, None)


def list_sessions() -> list[str]:
    return list(_sessions.keys())
