from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest


V03_DIR = Path(__file__).resolve().parents[1]
if str(V03_DIR) not in sys.path:
    sys.path.insert(0, str(V03_DIR))

from executor_v02 import execute_steps
from parser_v02 import ParseError, parse_dsl


def test_from_all_is_available_without_definition() -> None:
    steps = parse_dsl("Draft answer\n/FROM @ALL\n/OUT done")
    prompts: list[str] = []

    def fake_model(prompt: str, _: dict) -> str:
        prompts.append(prompt)
        return json.dumps({"error": 0, "out": "ok"})

    execute_steps(
        steps,
        context={"topic": "Safety"},
        call_model=fake_model,
        chat_history=["hello"],
    )

    prompt = prompts[0]
    assert "Inputs:\n- ALL: Chat history:" in prompt
    assert "hello" in prompt
    assert "- topic: Safety" in prompt
    assert "- ALL: Chat history:\nhello\n\nVariables:\n- ALL:" not in prompt


def test_from_omitted_supports_chat_embedding_only() -> None:
    steps = parse_dsl("Use this context: @CHAT\n/OUT done")
    prompts: list[str] = []

    def fake_model(prompt: str, _: dict) -> str:
        prompts.append(prompt)
        return json.dumps({"error": 0, "out": "ok"})

    execute_steps(
        steps,
        context={"topic": "Safety"},
        call_model=fake_model,
        chat_history=["hello"],
    )

    assert "Instruction:\nUse this context: hello" in prompts[0]


def test_from_omitted_rejects_all_embedding() -> None:
    with pytest.raises(ParseError, match="not allowed by /FROM"):
        parse_dsl("Use this context: @ALL\n/OUT done")
