from src import config
from src.llm_client import call_llm
from src.codeutil import extract_code

SYSTEM_PROMPT = (
    "You are a Python programmer. Given a problem description, write a single "
    "self-contained Python function that solves it. Output ONLY the function "
    "inside a ```python fenced code block, with no explanation, no example "
    "usage, and no extra top-level code."
)


def generate(problem_description: str) -> dict:
    """Generates a Python function for the given problem description.

    Returns a dict with the extracted `code`, the function `name` (best-effort),
    and the full `llm_call` record (for logging prompts/settings).
    """
    llm_call = call_llm(
        system_prompt=SYSTEM_PROMPT,
        user_prompt=problem_description,
        temperature=config.CODE_GEN_TEMPERATURE,
    )
    code = extract_code(llm_call["response_text"])
    func_name = _extract_function_name(code)

    return {"code": code, "func_name": func_name, "llm_call": llm_call}


def _extract_function_name(code: str) -> str | None:
    for line in code.splitlines():
        line = line.strip()
        if line.startswith("def "):
            return line[4:].split("(")[0].strip()
    return None
