import argparse
import json
import os

import requests

from src import config, oracle
from src.agents import code_generator, test_generator, test_executor
from src.dataset_loader import load_problems


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

    # 3. Test Case Executor Agent (with one retry loop if coverage is incomplete)
    verdict = test_executor.run(problem_id, code, tests)
    log["steps"].append({"agent": "test_executor", "verdict": verdict})

    def has_gaps(v: dict) -> bool:
        return bool(v.get("missing_lines")) or bool(v.get("missing_branches"))

    reference_code = problem.get("code", "")
    reference_test_list = problem.get("test_list", [])

    # Repair loop: a failing test could mean the generated code is buggy, or
    # that the test's hand-computed expected value is wrong. Rather than ask
    # an LLM to arbitrate (unreliable - it tends to "fix" code that was
    # already correct), we use MBPP's own reference solution + test_list as a
    # deterministic oracle to decide which side is actually at fault. If
    # tests pass but coverage is incomplete, fall back to generating more
    # tests for the missing lines/branches.
    attempt = 0
    while attempt < config.MAX_REPAIR_ATTEMPTS and (not verdict["passed"] or has_gaps(verdict)):
        attempt += 1
        try:
            if not verdict["passed"]:
                oracle_result = oracle.check(problem_id, func_name, reference_code, reference_test_list)
                log["steps"].append({"agent": "oracle_check", "result": oracle_result})

                if oracle_result["oracle_passed"]:
                    # Code agrees with the official reference -> our generated
                    # tests have the wrong expected values.
                    fix_result = test_generator.fix_failing_assertions(
                        code, func_name, tests, verdict["stdout"]
                    )
                    log["steps"].append({"agent": "test_generator_fix", "llm_call": fix_result["llm_call"]})
                    tests = fix_result["tests"]
                else:
                    # Code disagrees with the reference (or no reference
                    # available) -> regenerate the function, then fresh tests
                    # for it since the old ones targeted the old code.
                    code_result = code_generator.generate(description)
                    log["steps"].append({"agent": "code_generator_retry", "llm_call": code_result["llm_call"]})
                    code = code_result["code"]
                    func_name = code_result["func_name"]

                    test_result = test_generator.generate(code, func_name, description)
                    log["steps"].append({"agent": "test_generator_retry", "llm_call": test_result["llm_call"]})
                    tests = test_result["tests"]
            else:
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
    parser.add_argument("--limit", type=int, default=3, help="Number of MBPP problems to run")
    parser.add_argument("--start", type=int, default=0, help="Skip this many dataset records before starting")
    args = parser.parse_args()

    problems = load_problems(limit=args.limit, start=args.start)
    os.makedirs(config.RESULTS_DIR, exist_ok=True)

    summary_path = os.path.join(config.RESULTS_DIR, "summary.json")
    summary = []
    if args.start and os.path.exists(summary_path):
        with open(summary_path) as f:
            summary = json.load(f)
    for problem in problems:
        problem_id = str(problem.get("task_id", problem.get("id")))
        print(f"Running problem {problem_id}...")
        try:
            log = run_problem(problem)
        except (ValueError, requests.exceptions.RequestException) as e:
            print(f"  -> ERROR: {e}")
            summary.append({"problem_id": problem_id, "error": str(e)})
            continue
        verdict = log["final_verdict"]
        summary.append(
            {
                "problem_id": log["problem_id"],
                "passed": verdict["passed"],
                "coverage_percent": verdict["coverage_percent"],
                "branch_coverage_percent": verdict["branch_coverage_percent"],
            }
        )
        print(
            f"  -> passed={verdict['passed']} "
            f"statement_coverage={verdict['coverage_percent']} "
            f"branch_coverage={verdict['branch_coverage_percent']}"
        )
        if not verdict["passed"]:
            print(f"     reason: {_failure_reason(verdict['stdout'])}")

    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)


if __name__ == "__main__":
    main()
