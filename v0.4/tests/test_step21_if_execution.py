from __future__ import annotations

import json
import sys
from pathlib import Path


V04_DIR = Path(__file__).resolve().parents[1]
if str(V04_DIR) not in sys.path:
    sys.path.insert(0, str(V04_DIR))

from executor_v02 import execute_program
from parser_v02 import parse_program


def test_execute_program_runs_true_if_branch_without_leaking_branch_vars() -> None:
    program = parse_program(
        """Choose path
/DEF should_answer /TYPE bool
/IF @should_answer
/THEN Draft answer
/DEF answer /TYPE str
/OUT concise answer
/END
/THEN Finalize
/OUT done
"""
    )
    responses = iter(
        [
            json.dumps({"error": 0, "out": "decided", "vars": {"should_answer": True}}),
            json.dumps({"error": 0, "out": "answer ready", "vars": {"answer": "yes"}}),
            json.dumps({"error": 0, "out": "finished"}),
        ]
    )

    ctx, logs, outputs = execute_program(
        program,
        context={},
        call_model=lambda *_: next(responses),
    )

    assert outputs == ["decided", "answer ready", "finished"]
    assert ctx == {"should_answer": True}
    assert logs[1]["node_kind"] == "if"
    assert logs[1]["execution"] == "entered"
    assert logs[1]["node_path"] == [1]
    assert logs[2]["node_kind"] == "step"
    assert logs[2]["node_path"] == [1, 0]
    assert logs[2]["depth"] == 1
    assert logs[2]["output"] == "answer ready"


def test_execute_program_skips_false_if_branch_and_avoids_extra_model_calls() -> None:
    program = parse_program(
        """Choose path
/DEF should_answer /TYPE bool
/IF @should_answer
/THEN Draft answer
/OUT concise answer
/END
/THEN Finalize
/OUT done
"""
    )
    responses = iter(
        [
            json.dumps({"error": 0, "out": "decided", "vars": {"should_answer": False}}),
            json.dumps({"error": 0, "out": "finished"}),
        ]
    )
    calls = {"count": 0}

    def fake_model(*_: object) -> str:
        calls["count"] += 1
        return next(responses)

    ctx, logs, outputs = execute_program(program, context={}, call_model=fake_model)

    assert calls["count"] == 2
    assert outputs == ["decided", "finished"]
    assert ctx == {"should_answer": False}
    assert logs[1]["node_kind"] == "if"
    assert logs[1]["execution"] == "skipped"
    assert logs[1]["child_count"] == 1


def test_execute_program_keeps_outer_var_when_branch_redefines_it() -> None:
    program = parse_program(
        """Seed values
/DEF x /TYPE str
/DEF ok /TYPE bool
/IF @ok
/THEN Rewrite x
/DEF x /TYPE str
/OUT branch output
/END
"""
    )
    responses = iter(
        [
            json.dumps({"error": 0, "out": "seeded", "vars": {"x": "outer", "ok": True}}),
            json.dumps({"error": 0, "out": "branched", "vars": {"x": "inner"}}),
        ]
    )

    ctx, _, outputs = execute_program(program, context={}, call_model=lambda *_: next(responses))

    assert outputs == ["seeded", "branched"]
    assert ctx == {"x": "outer", "ok": True}
