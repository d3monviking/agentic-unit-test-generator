import json
import os
import subprocess
import sys

from src import config


def run(problem_id: str, code: str, tests: str) -> dict:
    """Writes the generated code + tests to results/<problem_id>/, executes
    them with pytest under coverage, and returns a verdict dict.

    This runs the LLM-generated code as a real subprocess on the local
    machine (no sandboxing beyond a timeout) - fine for small MBPP-style
    functions, not for untrusted code in general.
    """
    run_dir = os.path.join(config.RESULTS_DIR, problem_id)
    os.makedirs(run_dir, exist_ok=True)

    solution_path = os.path.join(run_dir, "solution.py")
    test_path = os.path.join(run_dir, "test_solution.py")
    coverage_json_path = os.path.join(run_dir, "coverage.json")

    with open(solution_path, "w") as f:
        f.write(code)
    with open(test_path, "w") as f:
        f.write(tests)

    pytest_result = _run_subprocess(
        [sys.executable, "-m", "coverage", "run", "--branch", "-m", "pytest", "test_solution.py", "-q"],
        cwd=run_dir,
    )

    _run_subprocess([sys.executable, "-m", "coverage", "json", "-o", "coverage.json"], cwd=run_dir)

    coverage_percent = None
    branch_coverage_percent = None
    missing_lines: list[int] = []
    missing_branches: list[list[int]] = []
    if os.path.exists(coverage_json_path):
        with open(coverage_json_path) as f:
            cov_data = json.load(f)
        file_report = cov_data.get("files", {}).get("solution.py")
        if file_report:
            coverage_percent = file_report["summary"]["percent_statements_covered"]
            branch_coverage_percent = file_report["summary"]["percent_branches_covered"]
            missing_lines = file_report["missing_lines"]
            missing_branches = file_report["missing_branches"]

    verdict = {
        "problem_id": problem_id,
        "passed": pytest_result["returncode"] == 0,
        "returncode": pytest_result["returncode"],
        "stdout": pytest_result["stdout"],
        "stderr": pytest_result["stderr"],
        "coverage_percent": coverage_percent,
        "branch_coverage_percent": branch_coverage_percent,
        "missing_lines": missing_lines,
        "missing_branches": missing_branches,
    }

    with open(os.path.join(run_dir, "verdict.json"), "w") as f:
        json.dump(verdict, f, indent=2)

    return verdict


def _run_subprocess(cmd: list[str], cwd: str) -> dict:
    try:
        proc = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=config.SUBPROCESS_TIMEOUT_SECONDS,
        )
        return {"returncode": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr}
    except subprocess.TimeoutExpired as e:
        return {"returncode": -1, "stdout": e.stdout or "", "stderr": f"TIMEOUT after {config.SUBPROCESS_TIMEOUT_SECONDS}s"}
