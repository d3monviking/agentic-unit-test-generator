import os
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

# Pick any free model slug from https://openrouter.ai/models?max_price=0
MODEL = os.environ.get("OPENROUTER_MODEL", "cohere/north-mini-code:free")

CODE_GEN_TEMPERATURE = 0.2
TEST_GEN_TEMPERATURE = 0.4

MAX_REPAIR_ATTEMPTS = 3
SUBPROCESS_TIMEOUT_SECONDS = 15
LLM_TIMEOUT_SECONDS = 120
MAX_RESPONSE_TOKENS = 1200
RATE_LIMIT_BACKOFF_SECONDS = [15, 30, 60]

RESULTS_DIR = "results"
DATASET_PATH = "dataset/mbpp.jsonl"
