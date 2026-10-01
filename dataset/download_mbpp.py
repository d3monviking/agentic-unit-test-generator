"""Downloads the MBPP dataset (mbpp.jsonl) into this directory.

Tries the official Google Research GitHub raw file first; falls back to
Hugging Face `datasets` if that fails (requires `pip install datasets`).
"""
import json
import os
import urllib.request

RAW_URL = "https://raw.githubusercontent.com/google-research/google-research/master/mbpp/mbpp.jsonl"
OUT_PATH = os.path.join(os.path.dirname(__file__), "mbpp.jsonl")


def download_from_github() -> bool:
    try:
        urllib.request.urlretrieve(RAW_URL, OUT_PATH)
        return os.path.exists(OUT_PATH) and os.path.getsize(OUT_PATH) > 0
    except Exception as e:
        print(f"GitHub download failed: {e}")
        return False


def download_from_huggingface() -> bool:
    try:
        from datasets import load_dataset
    except ImportError:
        print("`datasets` not installed. Run: pip install datasets")
        return False

    ds = load_dataset("mbpp", "full", split="test")
    with open(OUT_PATH, "w") as f:
        for row in ds:
            f.write(json.dumps(dict(row)) + "\n")
    return True


if __name__ == "__main__":
    if download_from_github():
        print(f"Saved MBPP dataset to {OUT_PATH}")
    elif download_from_huggingface():
        print(f"Saved MBPP dataset to {OUT_PATH} (via Hugging Face)")
    else:
        print("Could not download MBPP automatically. Download it manually from "
              "https://github.com/google-research/google-research/tree/master/mbpp "
              f"and place it at {OUT_PATH}")
