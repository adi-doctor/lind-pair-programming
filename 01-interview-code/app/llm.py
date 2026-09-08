"""Client for the hosted clinical-extraction LLM.

This offline stub stands in for the real hosted model so the repo runs with
no API keys, no network access, and no cost. It simulates real request
latency and the occasional upstream overload failure. Treat it like the
external service it replaces.
"""

import asyncio
import json
import re
from collections import defaultdict
from pathlib import Path

RESPONSES_PATH = Path(__file__).resolve().parents[1] / "data" / "llm_responses.json"

# Visits whose upstream requests intermittently fail with an overload error.
_FLAKY_VISITS = {"VN-110"}

REQUEST_LATENCY_SECONDS = 1.5


class LLMOverloadedError(RuntimeError):
    """Raised when the upstream model returns HTTP 529 (overloaded)."""

    status_code = 529


class LLMClient:
    def __init__(self, latency: float = REQUEST_LATENCY_SECONDS):
        self.latency = latency
        with open(RESPONSES_PATH) as f:
            self._responses: dict[str, str] = json.load(f)
        self._attempts: dict[str, int] = defaultdict(int)

    async def complete(self, prompt: str) -> str:
        await asyncio.sleep(self.latency)

        match = re.search(r"VN-\d+", prompt)
        if match is None:
            raise ValueError("prompt does not reference a known visit")
        visit_id = match.group()

        self._attempts[visit_id] += 1
        if visit_id in _FLAKY_VISITS and self._attempts[visit_id] % 3 != 0:
            raise LLMOverloadedError(
                f"upstream model overloaded (status 529) handling {visit_id}"
            )

        if visit_id not in self._responses:
            raise KeyError(f"no completion available for {visit_id}")
        return self._responses[visit_id]
