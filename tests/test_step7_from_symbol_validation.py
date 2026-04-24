from __future__ import annotations

import pytest

from chatdsl_core.parser_v02 import ParseError, parse_dsl

def test_from_accepts_previously_defined_variable() -> None:
    text = """Create seed
/DEF seed
/THEN use seed
/FROM @seed
/OUT done
"""
    steps = parse_dsl(text)
    assert len(steps) == 2
    assert [it.value for it in (steps[1].from_items or []) if it.kind == "var"] == ["seed"]

def test_from_accepts_predeclared_context_variable() -> None:
    steps = parse_dsl("Use existing var\n/FROM @seed\n/OUT done", predeclared_vars={"seed"})
    assert len(steps) == 1
    assert [it.value for it in (steps[0].from_items or []) if it.kind == "var"] == ["seed"]

@pytest.mark.parametrize(
    "dsl",
    [
        "Use missing\n/FROM @missing",
        "Use future\n/FROM @future\n/THEN define future\n/DEF future",
        "Use and define in same step\n/FROM @x\n/DEF x",
    ],
)
def test_from_rejects_undefined_or_forward_references(dsl: str) -> None:
    with pytest.raises(ParseError, match="/FROM references undefined variable"):
        parse_dsl(dsl)

def test_from_allows_redefined_variable_in_later_steps() -> None:
    text = """Create x
/DEF x
/THEN overwrite x
/DEF x
/THEN use x
/FROM @x
/OUT done
"""
    steps = parse_dsl(text)
    assert len(steps) == 3
    assert [it.value for it in (steps[2].from_items or []) if it.kind == "var"] == ["x"]
