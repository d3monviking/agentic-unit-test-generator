from src import config
from src.llm_client import call_llm
from src.codeutil import extract_code

SYSTEM_PROMPT = (
    "You are a software test engineer practicing coverage-based unit testing. "
    "Given a Python function, write pytest test cases that together cover "
    "every statement, every branch (if/else) and every loop path (zero "
    "iterations, one iteration, multiple iterations where applicable) in the "
    "function. Import the function with `from solution import {func_name}`. "
    "Use at most 8 test functions total, and do not repeat near-identical "
    "cases - pick the minimum set of inputs needed for full coverage. "
    "Output ONLY the test file contents inside a single ```python fenced "
    "code block, with no explanation."
)

RETRY_SYSTEM_PROMPT = (
    "You previously wrote pytest tests for a function, but coverage analysis "
    "shows some lines are still not executed by any test. Add or modify test "
    "cases so that the missing lines are covered too. Keep the existing tests "
    "and import style. Output ONLY the full, updated test file inside a "
    "```python fenced code block, with no explanation."
)


def generate(code: str, func_name: str, problem_description: str) -> dict:
    user_prompt = (
        f"Problem description:\n{problem_description}\n\n"
        f"Function under test:\n```python\n{code}\n```"
    )
    llm_call = call_llm(
        system_prompt=SYSTEM_PROMPT.format(func_name=func_name),
        user_prompt=user_prompt,
        temperature=config.TEST_GEN_TEMPERATURE,
    )
    tests = extract_code(llm_call["response_text"])
    return {"tests": tests, "llm_call": llm_call}


def regenerate_for_missing_lines(
    code: str,
    func_name: str,
    existing_tests: str,
    missing_lines: list[int],
    missing_branches: list[list[int]] | None = None,
) -> dict:
    gaps = []
    if missing_lines:
        gaps.append(f"uncovered line numbers: {missing_lines}")
    if missing_branches:
        gaps.append(
            f"uncovered branches (as [from_line, to_line] jumps not taken): {missing_branches}"
        )
    gap_text = "; ".join(gaps)

    user_prompt = (
        f"Function under test:\n```python\n{code}\n```\n\n"
        f"Current tests:\n```python\n{existing_tests}\n```\n\n"
        f"Coverage report shows the following gaps - {gap_text}. "
        f"Add tests to cover them, in particular inputs that force each branch "
        f"(e.g. the opposite condition, or zero/one/multiple loop iterations) "
        f"to be taken."
    )
    llm_call = call_llm(
        system_prompt=RETRY_SYSTEM_PROMPT,
        user_prompt=user_prompt,
        temperature=config.TEST_GEN_TEMPERATURE,
    )
    tests = extract_code(llm_call["response_text"])
    return {"tests": tests, "llm_call": llm_call}
