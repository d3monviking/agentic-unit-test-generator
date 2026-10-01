import os
import re
import subprocess
import sys

from src import config

_DEF_RE = re.compile(r"^\s*def\s+(\w+)\s*\(", re.MULTILINE)


def _reference_func_name(reference_code: str) -> str | None:
    match = _DEF_RE.search(reference_code)
    return match.group(1) if match else None


def check(problem_id: str, local_func_name: str, reference_code: str, reference_test_list: list[str]) -> dict:
    """Runs MBPP's own reference test_list against the candidate function
    already written to results/<problem_id>/solution.py, aliasing the
    reference function name to whatever the Code Generator Agent actually
    named it.

    This is a deterministic ground-truth check (not an LLM call): if the
    candidate passes the dataset's own reference assertions, any failure in
    our LLM-generated tests must be a wrong expected value in the test, not a
    bug in the generated code - and vice versa.
    """
    reference_func_name = _reference_func_name(reference_code)
    if not reference_func_name or not reference_test_list:
        return {"ran": False, "oracle_passed": None, "stdout": "", "stderr": "no reference code/tests available"}

    run_dir = os.path.join(config.RESULTS_DIR, problem_id)
    os.makedirs(run_dir, exist_ok=True)

    import_line = f"from solution import {local_func_name} as {reference_func_name}"
    script = "\n".join([import_line] + list(reference_test_list) + ["print('ORACLE_OK')"])

    script_path = os.path.join(run_dir, "oracle_check.py")
    with open(script_path, "w") as f:
        f.write(script)

    try:
        proc = subprocess.run(
            [sys.executable, "oracle_check.py"],
            cwd=run_dir,
            capture_output=True,
            text=True,
            timeout=config.SUBPROCESS_TIMEOUT_SECONDS,
        )
        oracle_passed = proc.returncode == 0 and "ORACLE_OK" in proc.stdout
        return {"ran": True, "oracle_passed": oracle_passed, "stdout": proc.stdout, "stderr": proc.stderr}
    except subprocess.TimeoutExpired as e:
        return {"ran": True, "oracle_passed": False, "stdout": e.stdout or "", "stderr": "TIMEOUT"}
