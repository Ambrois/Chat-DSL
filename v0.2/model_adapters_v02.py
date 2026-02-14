from __future__ import annotations

from typing import Optional

from executor_v02 import ModelCall
from gemini_client_v02 import call_gemini


def make_gemini_caller(model: Optional[str], timeout_s: float) -> ModelCall:
    def _caller(prompt: str) -> str:
        return call_gemini(prompt, model=model, timeout_s=timeout_s)

    return _caller
