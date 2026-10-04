import argparse
import json
import os

import requests

from src import config
from src.agents import code_generator, test_generator, test_executor
from src.dataset_loader import load_problems, get_problem


def has_gaps(v: dict) -> bool:
    return bool(v.get("missing_lines")) or bool(v.get("missing_branches"))


def run_problem(problem: dict) -> dict:
    problem_id = str(problem.get("task_id", problem.get("id", "unknown")))
    description = problem["text"] if "text" in problem else problem["prompt"]
    run_dir = os.path.join(config.RESULTS_DIR, problem_id)
    os.makedirs(run_dir, exist_ok=True)

    log = {"problem_id": problem_id, "description": description, "steps": []}

    # 1. Code Generator Agent
    code_result = code_generator.generate(description)
    log["steps"].append({"agent": "code_generator", "llm_call": code_result["llm_call"]})
    code = code_result["code"]
    func_name = code_result["func_name"]

    # 2. Test Case Generator Agent
    test_result = test_generator.generate(code, func_name, description)
    log["steps"].append({"agent": "test_generator", "llm_call": test_result["llm_call"]})
    tests = test_result["tests"]

    # 3. Test Case Executor Agent
    verdict = test_executor.run(problem_id, code, tests)
    log["steps"].append({"agent": "test_executor", "verdict": verdict})

    # Coverage-gap retry: if coverage.py reports lines/branches never
    # executed, ask for more tests to close the gap. This is the only repair
    # loop in the pipeline - it uses only information the Test Executor
    # Agent's own coverage.py run produced (missing lines/branches), nothing
    # external.
    attempt = 0
    while attempt < config.MAX_REPAIR_ATTEMPTS and has_gaps(verdict):
        attempt += 1
        try:
            retry_result = test_generator.regenerate_for_missing_lines(
                code, func_name, tests, verdict["missing_lines"], verdict["missing_branches"]
            )
            log["steps"].append({"agent": "test_generator_retry", "llm_call": retry_result["llm_call"]})
            tests = retry_result["tests"]
        except (ValueError, requests.exceptions.RequestException) as e:
            log["steps"].append({"agent": "repair_error", "error": str(e)})
            break

        verdict = test_executor.run(problem_id, code, tests)
        log["steps"].append({"agent": "test_executor_retry", "verdict": verdict})

    log["final_code"] = code
    log["final_tests"] = tests
    log["final_verdict"] = verdict
    log["coverage_repair_attempts"] = attempt

    with open(os.path.join(run_dir, "log.json"), "w") as f:
        json.dump(log, f, indent=2)

    return log


def _failure_reason(pytest_stdout: str) -> str:
    """Pulls the FAILED summary lines out of pytest output for a compact
    console message, instead of dumping the full stdout."""
    failed_lines = [line for line in pytest_stdout.splitlines() if line.startswith("FAILED ")]
    return "; ".join(failed_lines) if failed_lines else pytest_stdout.strip().splitlines()[-1] if pytest_stdout.strip() else "unknown"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--problem-id", type=int, default=None, help="Run only this single MBPP task_id")
    parser.add_argument("--limit", type=int, default=3, help="Number of MBPP problems to run (ignored with --problem-id)")
    parser.add_argument("--start", type=int, default=0, help="Skip this many dataset records before starting (ignored with --problem-id)")
    args = parser.parse_args()

    if args.problem_id is not None:
        problem = get_problem(args.problem_id)
        if problem is None:
            print(f"No MBPP problem found with task_id={args.problem_id}")
            return
        problems = [problem]
    else:
        problems = load_problems(limit=args.limit, start=args.start)
    os.makedirs(config.RESULTS_DIR, exist_ok=True)

    summary_path = os.path.join(config.RESULTS_DIR, "summary.json")
    summary = []
    if os.path.exists(summary_path):
        with open(summary_path) as f:
            summary = json.load(f)

    def upsert_summary(entry: dict) -> None:
        for i, existing in enumerate(summary):
            if existing["problem_id"] == entry["problem_id"]:
                summary[i] = entry
                return
        summary.append(entry)

    for problem in problems:
        problem_id = str(problem.get("task_id", problem.get("id")))
        print(f"Running problem {problem_id}...")
        try:
            log = run_problem(problem)
        except (ValueError, requests.exceptions.RequestException) as e:
            print(f"  -> ERROR: {e}")
            upsert_summary({"problem_id": problem_id, "error": str(e)})
            continue
        verdict = log["final_verdict"]
        upsert_summary(
            {
                "problem_id": log["problem_id"],
                "passed": verdict["passed"],
                "coverage_percent": verdict["coverage_percent"],
                "branch_coverage_percent": verdict["branch_coverage_percent"],
                "coverage_repair_attempts": log["coverage_repair_attempts"],
            }
        )
        print(
            f"  -> passed={verdict['passed']} "
            f"statement_coverage={verdict['coverage_percent']} "
            f"branch_coverage={verdict['branch_coverage_percent']}"
        )
        if not verdict["passed"]:
            print(f"     reason: {_failure_reason(verdict['stdout'])}")
        if has_gaps(verdict):
            print(
                f"     WARNING: coverage criterion NOT fully satisfied after "
                f"{log['coverage_repair_attempts']} repair attempt(s) "
                f"(max {config.MAX_REPAIR_ATTEMPTS}) - "
                f"missing_lines={verdict['missing_lines']} "
                f"missing_branches={verdict['missing_branches']}"
            )

    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)

    _print_coverage_stats(summary)


def _print_coverage_stats(summary: list[dict]) -> None:
    """Prints aggregate coverage stats across a run: how many problems
    reached full statement/branch coverage, and the average coverage."""
    scored = [e for e in summary if "coverage_percent" in e and e["coverage_percent"] is not None]
    if not scored:
        return

    full_coverage = sum(1 for e in scored if e["coverage_percent"] == 100.0 and e["branch_coverage_percent"] == 100.0)
    passed = sum(1 for e in scored if e["passed"])
    avg_statement = sum(e["coverage_percent"] for e in scored) / len(scored)
    avg_branch = sum(e["branch_coverage_percent"] for e in scored) / len(scored)

    print("\nCoverage summary:")
    print(f"  problems measured: {len(scored)}")
    print(f"  tests passed: {passed}/{len(scored)}")
    print(f"  reached 100% statement + branch coverage: {full_coverage}/{len(scored)}")
    print(f"  average statement coverage: {avg_statement:.1f}%")
    print(f"  average branch coverage: {avg_branch:.1f}%")


if __name__ == "__main__":
    main()
