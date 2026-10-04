# Agentic Unit Test Generation

A pipeline of three LLM agents that, given an MBPP problem description, writes a
Python solution, writes pytest unit tests for it, and iteratively improves the
tests until `coverage.py` reports full statement + branch coverage (or the
repair budget runs out).

## Pipeline

```
problem description
      │
      ▼
Code Generator Agent  ──►  solution.py
      │
      ▼
Test Generator Agent  ──►  test_solution.py
      │
      ▼
Test Executor Agent   ──►  pytest + coverage.py  ──►  verdict.json
      │
      ▼
 missing lines/branches? ──yes──► Test Generator Agent (retry) ──► re-run
      │no
      ▼
    done
```

- **Code Generator** (`src/agents/code_generator.py`) — turns the MBPP problem
  text into a single Python function.
- **Test Generator** (`src/agents/test_generator.py`) — writes pytest tests
  aimed at full statement/branch/loop-path coverage, deriving expected values
  from the problem description (not by tracing the generated code, so it can
  actually catch bugs). On a coverage gap it's re-prompted with the exact
  missing lines/branches from the previous run.
- **Test Executor** (`src/agents/test_executor.py`) — runs the generated code
  and tests as a real subprocess under `coverage run --branch`, parses
  `coverage.json`, and produces a pass/fail + coverage verdict.

The MBPP dataset's own reference `code`/`test_list` are never read — only the
problem's `text` is given to the agents. Coverage is measured, not judged
against a reference solution.

## Project layout

```
src/
  config.py           settings: model, temperature, retry limits, paths
  llm_client.py        OpenRouter chat-completions call + 429 retry/backoff
  codeutil.py          fenced-code-block extraction from LLM output
  dataset_loader.py     loads MBPP problems from dataset/mbpp.jsonl
  pipeline.py           orchestrates the 3 agents + coverage-repair loop
  agents/
    code_generator.py
    test_generator.py
    test_executor.py
dataset/
  mbpp.jsonl            MBPP dataset (text, code, test_list per problem)
  download_mbpp.py      fetches the dataset
docs/
  report_draft.md        project report
results/
  <problem_id>/          solution.py, test_solution.py, coverage.json, verdict.json, log.json
  summary.json            per-problem pass/fail + coverage, across all runs
```

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in OPENROUTER_API_KEY
```

## Running

```bash
# Run N problems starting from the top of the dataset
python -m src.pipeline --limit 5

# Resume a batch, skipping the first K records
python -m src.pipeline --limit 5 --start 5

# Run a single MBPP problem by task_id
python -m src.pipeline --problem-id 69
```

Each run writes `results/<problem_id>/{solution.py,test_solution.py,coverage.json,verdict.json,log.json}`
and upserts an entry into `results/summary.json`. At the end it prints an
aggregate coverage summary (how many problems hit 100%/100%, average
statement/branch coverage, pass rate).

## Config

All tunables live in `src/config.py` (model slug, temperatures, max repair
attempts, subprocess/LLM timeouts, rate-limit backoff). Model is overridable
via the `OPENROUTER_MODEL` env var.
