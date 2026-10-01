import json

from src import config


def load_problems(limit: int | None = None, start: int = 0) -> list[dict]:
    """Loads MBPP problems from dataset/mbpp.jsonl, skipping the first `start`
    records (useful for resuming a batch after a crash/rate-limit).

    Each MBPP record has (at least) `task_id`, `text` (problem description),
    `code` (reference solution) and `test_list`. We only use `text` as input
    to the Code Generator Agent; `code`/`test_list` are reference-only, never
    shown to the LLM.
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
