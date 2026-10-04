import json

from src import config


def load_problems(limit: int | None = None, start: int = 0) -> list[dict]:
    """Loads MBPP problems from dataset/mbpp.jsonl, skipping the first `start`
    records (useful for resuming a batch after a crash/rate-limit).

    Each MBPP record has (at least) `task_id` and `text` (problem
    description); only `text` is used, as the user prompt for the Code
    Generator Agent. The dataset's own reference `code`/`test_list` fields
    are never read anywhere in the pipeline.
    """
    problems = []
    with open(config.DATASET_PATH) as f:
        for i, line in enumerate(f):
            if i < start:
                continue
            line = line.strip()
            if not line:
                continue
            problems.append(json.loads(line))
            if limit and len(problems) >= limit:
                break
    return problems


def get_problem(task_id: int) -> dict | None:
    """Looks up a single MBPP problem by its task_id."""
    with open(config.DATASET_PATH) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            record = json.loads(line)
            if record.get("task_id") == task_id:
                return record
    return None
