# Class 01 - Multi-provider LLM core

## What I built

- Implemented `GroqProvider` in `core/providers.py`: set `name = "groq"` and
  `base_url = "https://api.groq.com/openai/v1"` (Groq's OpenAI-compatible endpoint). The base
  adapter (`OpenAICompatibleProvider`) already handles request, errors and usage; the provider
  only fixes the endpoint.
- Completed `scripts/report.py`: reads `logs/llm_calls.jsonl` and prints total cost (USD),
  p50/p95 latency (successful calls only, `statistics.quantiles`), % of calls with fallback and
  calls per provider. Handles missing file and empty file with a message.
- Verified end to end: `uv run main.py --provider groq "..."` responds and logs a successful
  call; tests pass (`uv run pytest -q`, 17 passed); `ruff check` clean.

## Key concepts

- Adapter pattern: one provider class per API, all speaking the same OpenAI-compatible
  `/chat/completions` shape through a shared base class.
- Transient vs permanent errors: 429/5xx/timeouts are retried with exponential backoff
  (1s -> 2s -> 4s + jitter); 4xx are not retried, they move straight to the next provider.
- Fallback chain: primary + ordered fallbacks; the client walks them until one answers.
- Cost per call: computed from tokens in/out and a price table (`core/pricing.py`).
- Structured logging: one JSON line per attempt, and never the prompt text or keys.

## Useful commands

    uv run main.py --demo
    uv run main.py --provider groq "hola"
    uv run pytest -q
    uv run ruff check .
    uv run scripts/report.py

## Open questions / pending

- Bonus: add `--temperature` (0-2) to `main.py` and pass it through to the provider.
