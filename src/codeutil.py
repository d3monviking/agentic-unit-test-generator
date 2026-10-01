import json
import re

_FENCE_RE = re.compile(r"```(?:python)?\s*\n(.*?)```", re.DOTALL)
_JSON_FENCE_RE = re.compile(r"```(?:json)?\s*\n(.*?)```", re.DOTALL)


def extract_code(text: str) -> str:
    """Pulls the first fenced code block out of an LLM response, or returns
    the text unchanged if there is no fence."""
    match = _FENCE_RE.search(text)
    return match.group(1).strip() if match else text.strip()


def extract_json(text: str) -> dict:
    """Pulls a JSON object out of an LLM response, whether it's bare or
    wrapped in a ```json fenced code block."""
    match = _JSON_FENCE_RE.search(text)
    candidate = match.group(1).strip() if match else text.strip()
    return json.loads(candidate)
