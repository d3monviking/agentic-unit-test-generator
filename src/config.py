import os
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

# Pick any free model slug from https://openrouter.ai/models?max_price=0.
# cohere/north-mini-code:free (tried first) produced real logic bugs that
# failed even MBPP's own reference tests (e.g. problem 11, remove_Occ) -
# nemotron-3-super is a much larger model and got these right.
MODEL = os.environ.get("OPENROUTER_MODEL", "nvidia/nemotron-3-super-120b-a12b:free")

CODE_GEN_TEMPERATURE = 0.2
TEST_GEN_TEMPERATURE = 0.4

MAX_REPAIR_ATTEMPTS = 3
SUBPROCESS_TIMEOUT_SECONDS = 15
LLM_TIMEOUT_SECONDS = 120
MAX_RESPONSE_TOKENS = 3000
RATE_LIMIT_BACKOFF_SECONDS = [15, 30, 60]

RESULTS_DIR = "results"
DATASET_PATH = "dataset/mbpp.jsonl"
