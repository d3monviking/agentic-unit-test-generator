from src import config
from src.llm_client import call_llm
from src.codeutil import extract_code


def _ensure_import(tests: str, func_name: str) -> str:
    """The model occasionally forgets the `from solution import ...` line
    despite being told to include it, which fails every test with a
    NameError rather than an assertion. Deterministically guarantee it's
    there instead of relying on prompt compliance alone."""
    import_line = f"from solution import {func_name}"
    if import_line in tests or f"import solution" in tests:
        return tests
    return f"{import_line}\n{tests}"

SYSTEM_PROMPT = (
    "You are a software test engineer practicing coverage-based unit testing. "
    "Do not write any prose, explanation, or reasoning before the code - not "
    "even one sentence. Begin your response immediately with the ```python "
    "fence; work out expected values silently. "
    "Given a Python function, write pytest test cases that together cover "
    "every statement, every branch (if/else) and every loop path (zero "
    "iterations, one iteration, multiple iterations where applicable) in the "
    "function. Import the function with `from solution import {func_name}`. "
    "Use at most 8 test functions total, and do not repeat near-identical "
    "cases - pick the minimum set of inputs needed for full coverage. "
    "\n\n"
    "CRITICAL - derive each expected value from the PROBLEM DESCRIPTION, "
    "never by mentally tracing what the given function's code happens to "
    "compute. The function may be buggy; a test that merely reproduces the "
    "function's own behavior can never catch that bug, and defeats the "
    "purpose of testing. Work out the correct answer as if you were "
    "solving the original problem from scratch, then check whether the "
    "function matches it - don't reason in the other direction. "
    "\n\n"
    "Expected values are a common source of error: you are prone to mistakes "
    "when hand-computing the result of multi-step logic (e.g. dynamic "
    "programming, running totals, index arithmetic) for arbitrary inputs. "
    "To avoid this, prefer the SIMPLEST input that still exercises each "
    "branch/loop path - e.g. a 1x1 or 2x2 matrix instead of a 4x4 one, "
    "all-equal or all-zero elements instead of arbitrary distinct numbers, "
    "a single iteration instead of five - so the correct expected value is "
    "obvious by inspection rather than something you have to simulate "
    "mentally. Only use a larger/more complex input on one test if a "
    "simple input genuinely cannot reach some branch or loop path. "
    "\n\n"
    "Output ONLY the test file contents inside a single ```python fenced "
    "code block, with no explanation."
)

RETRY_SYSTEM_PROMPT = (
    "You previously wrote pytest tests for a function, but coverage analysis "
    "shows some lines are still not executed by any test. Add or modify test "
    "cases so that the missing lines are covered too. Keep the existing tests "
    "and import style. Prefer the simplest input that reaches the missing "
    "line/branch - e.g. a small matrix with equal/zero values rather than an "
    "arbitrary one - so you can determine the correct expected value by "
    "inspection instead of simulating multi-step logic by hand. Output ONLY "
    "the full, updated test file inside a "
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
    tests = _ensure_import(extract_code(llm_call["response_text"]), func_name)
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
    tests = _ensure_import(extract_code(llm_call["response_text"]), func_name)
    return {"tests": tests, "llm_call": llm_call}
