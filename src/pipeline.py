import argparse
import json
import os

import requests

from src import config, oracle
from src.agents import code_generator, test_generator, test_executor
from src.dataset_loader import load_problems


def has_gaps(v: dict) -> bool:
    return bool(v.get("missing_lines")) or bool(v.get("missing_branches"))


def classify_against_oracle(verdict_passed: bool, oracle_result: dict) -> str | None:
    """Classifies the generated test suite's verdict against ground truth
    (MBPP's own reference solution + test_list), independent of and never
    fed back into the pipeline. This measures what the project is actually
    about - how good the agent is at writing tests that catch real bugs -
    rather than how good the pipeline is at self-correcting with help it
    wouldn't have in the real world.

    - true_positive:  code is actually buggy, generated tests caught it
    - false_negative: code is actually buggy, generated tests missed it (passed anyway)
    - false_positive: code is actually correct, generated tests wrongly failed it
    - true_negative:  code is actually correct, generated tests correctly passed it
    """
    if oracle_result.get("oracle_passed") is None:
        return None
    code_actually_correct = oracle_result["oracle_passed"]
    if code_actually_correct:
        return "true_negative" if verdict_passed else "false_positive"
    else:
        return "true_positive" if not verdict_passed else "false_negative"


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

    # Coverage-gap retry only: if the generated tests pass but coverage.py
    # reports lines/branches never executed, ask for more tests to close the
    # gap. This uses only information a real test-generation tool would have
    # (its own coverage report) - no reference solution involved.
    attempt = 0
    while attempt < config.MAX_REPAIR_ATTEMPTS and verdict["passed"] and has_gaps(verdict):
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

    # Post-hoc oracle classification (evaluation only - not fed back into the
    # pipeline): did the agent-written tests actually catch a real bug?
    reference_code = problem.get("code", "")
    reference_test_list = problem.get("test_list", [])
    oracle_result = oracle.check(problem_id, func_name, reference_code, reference_test_list)
    log["steps"].append({"agent": "oracle_check", "result": oracle_result})
    classification = classify_against_oracle(verdict["passed"], oracle_result)

    log["final_code"] = code
    log["final_tests"] = tests
    log["final_verdict"] = verdict
    log["oracle_classification"] = classification

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
                "oracle_classification": log["oracle_classification"],
            }
        )
        print(
            f"  -> passed={verdict['passed']} "
            f"statement_coverage={verdict['coverage_percent']} "
            f"branch_coverage={verdict['branch_coverage_percent']} "
            f"oracle={log['oracle_classification']}"
        )
        if not verdict["passed"]:
            print(f"     reason: {_failure_reason(verdict['stdout'])}")

    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)

    _print_oracle_stats(summary)


def _print_oracle_stats(summary: list[dict]) -> None:
    """Prints bug-catching effectiveness stats for the test generator agent:
    of the problems where ground truth is known, how often did its tests
    actually catch a real bug vs. miss one vs. false-flag correct code."""
    counts = {"true_positive": 0, "false_negative": 0, "false_positive": 0, "true_negative": 0}
    for entry in summary:
        label = entry.get("oracle_classification")
        if label in counts:
            counts[label] += 1
    total_classified = sum(counts.values())
    if not total_classified:
        return

    buggy = counts["true_positive"] + counts["false_negative"]
    correct = counts["false_positive"] + counts["true_negative"]
    print("\nOracle-based test generator effectiveness:")
    print(f"  classified: {total_classified} (buggy code: {buggy}, correct code: {correct})")
    print(f"  true_positive  (caught a real bug):        {counts['true_positive']}")
    print(f"  false_negative (missed a real bug):        {counts['false_negative']}")
    print(f"  false_positive (false-flagged correct code): {counts['false_positive']}")
    print(f"  true_negative  (correctly passed correct code): {counts['true_negative']}")
    if buggy:
        print(f"  bug-catch rate: {counts['true_positive'] / buggy:.2%}")
    if correct:
        print(f"  false-alarm rate: {counts['false_positive'] / correct:.2%}")


if __name__ == "__main__":
    main()
