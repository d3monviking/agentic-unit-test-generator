import time

import requests
from src import config


def call_llm(
    system_prompt: str,
    user_prompt: str,
    temperature: float,
    model: str = None,
    max_tokens: int = None,
) -> dict:
    """Calls the OpenRouter chat completions API.

    Returns a dict with the raw response text plus the exact request payload,
    so the caller can log everything the report requires (prompts + settings).
    """
    model = model or config.MODEL
    payload = {
        "model": model,
        "temperature": temperature,
        "max_tokens": max_tokens or config.MAX_RESPONSE_TOKENS,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        # The project spec forbids chain-of-thought: explicitly disable any
        # reasoning tokens the model would otherwise generate before its answer.
        "reasoning": {"enabled": False},
    }
    headers = {
        "Authorization": f"Bearer {config.OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    response = _post_with_retry(payload, headers)
    data = response.json()
    choice = data["choices"][0]
    text = choice["message"]["content"]
    finish_reason = choice.get("finish_reason")
    if not text:
        raise ValueError(
            f"Model '{model}' returned empty content (finish_reason="
            f"{finish_reason!r}). Raw message: {choice['message']!r}"
        )
    if finish_reason == "length":
        raise ValueError(
            f"Model '{model}' hit the max_tokens limit ({payload['max_tokens']}) "
            f"and was cut off mid-response (likely a runaway/repetitive generation). "
            f"Partial content:\n{text[:500]}..."
        )

    return {
        "request": payload,
        "response_text": text,
        "raw_response": data,
    }


def _post_with_retry(payload: dict, headers: dict) -> requests.Response:
    """POSTs to OpenRouter, retrying on 429 (shared free-tier rate limit)
    with a growing backoff, since these limits are typically transient."""
    last_error = None
    for attempt, wait_seconds in enumerate([0, *config.RATE_LIMIT_BACKOFF_SECONDS]):
        if wait_seconds:
            time.sleep(wait_seconds)
        response = requests.post(
            config.OPENROUTER_BASE_URL, json=payload, headers=headers, timeout=config.LLM_TIMEOUT_SECONDS
        )
        if response.status_code != 429:
            response.raise_for_status()
            return response
        last_error = response
    last_error.raise_for_status()
