import re

_FENCE_RE = re.compile(r"```(?:python)?\s*\n(.*?)```", re.DOTALL)


def extract_code(text: str) -> str:
    """Pulls the first fenced code block out of an LLM response, or returns
    the text unchanged if there is no fence."""
    match = _FENCE_RE.search(text)
    return match.group(1).strip() if match else text.strip()
