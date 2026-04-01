from __future__ import annotations

import json
import sys
from pathlib import Path


V02_DIR = Path(__file__).resolve().parents[1]
if str(V02_DIR) not in sys.path:
    sys.path.insert(0, str(V02_DIR))

from runtime_v02 import run_dsl_text


def test_run_dsl_text_success() -> None:
    res = run_dsl_text(
        "Create x\n/DEF x /TYPE int",
        context={},
        call_model=lambda *_: json.dumps({"error": 0, "out": "ok", "vars": {"x": 3}}),
    )
    assert res.ok is True
    assert res.outputs == ["ok"]
    assert res.vars_after == {"x": 3}
    assert res.error is None
    assert len(res.parsed_steps) == 1


def test_run_dsl_text_parse_error() -> None:
    res = run_dsl_text("/OUT only output", context={})
    assert res.ok is False
    assert res.error is not None
    assert "Parse error:" in res.error
    assert res.outputs == []


def test_run_dsl_text_execution_error() -> None:
    res = run_dsl_text(
        "Create x\n/DEF x /TYPE int",
        context={},
        call_model=lambda *_: "not-json",
    )
    assert res.ok is False
    assert res.error is not None
    assert "Execution error:" in res.error
    assert len(res.parsed_steps) == 1


def test_run_dsl_text_preserves_prior_step_vars_after_later_failure() -> None:
    responses = iter(
        [
            json.dumps({"error": 0, "out": "ok1", "vars": {"a": 1}}),
            "not-json",
        ]
    )

    res = run_dsl_text(
        "One\n/DEF a /TYPE int\n/THEN Two\n/OUT done",
        context={},
        call_model=lambda *_: next(responses),
    )

    assert res.ok is False
    assert res.vars_after == {"a": 1}
    assert "Execution error:" in res.error


def test_run_dsl_text_supports_custom_sigil() -> None:
    responses = iter(
        [
            json.dumps({"error": 0, "out": "ok1", "vars": {"topic": "AI safety"}}),
            json.dumps({"error": 0, "out": "ok2"}),
        ]
    )

    res = run_dsl_text(
        "Pick topic\n/DEF topic\n/THEN Summarize #topic\n/FROM #topic\n/OUT done",
        context={},
        call_model=lambda *_: next(responses),
        sigil="#",
    )

    assert res.ok is True
    assert res.outputs == ["ok1", "ok2"]
    assert res.vars_after == {"topic": "AI safety"}
    assert res.parsed_steps[1]["sigil"] == "#"
