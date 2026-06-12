import json
from anthropic import Anthropic
from backend.config import ANTHROPIC_API_KEY

client = Anthropic(api_key=ANTHROPIC_API_KEY)


def detect_language(text: str) -> str:
    sample = text[:500]

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=32,
        messages=[{"role": "user", "content": f"What language is this text? Return ONLY the ISO 639-1 code (e.g. 'en', 'es', 'fr', 'de', 'zh', 'ja', 'ko', 'ar', 'pt', 'ru').\n\nText: {sample}"}],
    )
    code = response.content[0].text.strip().lower()[:2]
    return code if len(code) == 2 else "en"


def extract_entities_multilang(text: str, language: str, schema: dict) -> list[dict]:
    entity_types = [et["label"] for et in schema.get("entity_types", [])]
    rel_types = [rt["type"] for rt in schema.get("relationship_types", [])]

    lang_names = {
        "en": "English", "es": "Spanish", "fr": "French", "de": "German",
        "zh": "Chinese", "ja": "Japanese", "ko": "Korean", "ar": "Arabic",
        "pt": "Portuguese", "ru": "Russian", "it": "Italian", "nl": "Dutch",
        "hi": "Hindi", "tr": "Turkish", "pl": "Polish",
    }
    lang_name = lang_names.get(language, language)

    prompt = f"""Extract entities from this {lang_name} text. Return all entity names translated/transliterated to English.

Entity types to look for: {', '.join(entity_types)}

Text:
{text[:3000]}

Return a JSON array:
[{{"name": "English name", "original_name": "original script name", "label": "entity type", "language": "{language}", "properties": {{}}}}]

Return ONLY the JSON array."""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}],
    )

    result_text = response.content[0].text.strip()
    if result_text.startswith("```"):
        result_text = result_text.split("\n", 1)[1] if "\n" in result_text else result_text[3:]
        if result_text.endswith("```"):
            result_text = result_text[:-3]
        result_text = result_text.strip()

    try:
        return json.loads(result_text)
    except json.JSONDecodeError:
        return []
