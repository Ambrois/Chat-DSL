from __future__ import annotations

import sys
from pathlib import Path

import pytest


V04_DIR = Path(__file__).resolve().parents[1]
if str(V04_DIR) not in sys.path:
    sys.path.insert(0, str(V04_DIR))

from parser_v02 import IfNode, ParseError, Step, parse_dsl, parse_program


def test_parse_program_builds_if_node_with_nested_steps() -> None:
    text = """Choose path
/DEF should_answer /TYPE bool
/IF @should_answer
/THEN Draft answer
/OUT concise answer
/THEN Draft follow-up
/OUT include one caveat
/END
"""
    program = parse_program(text)

    assert len(program.items) == 2
    assert isinstance(program.items[0], Step)
    assert isinstance(program.items[1], IfNode)
    if_node = program.items[1]
    assert if_node.condition_var == "should_answer"
    assert [item.text for item in if_node.items if isinstance(item, Step)] == [
        "Draft answer",
        "Draft follow-up",
    ]


def test_parse_program_supports_nested_if_blocks() -> None:
    text = """Seed
/DEF outer /TYPE bool
/DEF inner /TYPE bool
/IF @outer
/THEN Outer step
/OUT outer
/IF @inner
/THEN Inner step
/OUT inner
/END
/END
"""
    program = parse_program(text)

    outer_if = program.items[1]
    assert isinstance(outer_if, IfNode)
    assert isinstance(outer_if.items[1], IfNode)
    inner_if = outer_if.items[1]
    assert inner_if.condition_var == "inner"


def test_parse_program_accepts_predeclared_if_condition_variable() -> None:
    program = parse_program(
        "/IF @ok\n/THEN inside\n/OUT done\n/END",
        predeclared_vars={"ok"},
    )

    assert len(program.items) == 1
    assert isinstance(program.items[0], IfNode)
    assert program.items[0].condition_var == "ok"


@pytest.mark.parametrize(
    "dsl, err",
    [
        ("/END", "/END without matching /IF"),
        ("Seed\n/DEF ok /TYPE bool\n/IF @ok\n/THEN inside", "missing /END"),
        ("Seed\n/DEF ok /TYPE bool\n/IF @ok\n/END", "must contain at least one node"),
        ("/IF @missing\n/THEN inside\n/END", "undefined variable @missing"),
        ("Seed\n/DEF ok /TYPE bool\n/IF ok\n/THEN inside\n/END", "exactly one variable reference"),
    ],
)
def test_if_block_parse_errors(dsl: str, err: str) -> None:
    with pytest.raises(ParseError, match=err):
        parse_program(dsl)


def test_vars_defined_in_if_are_visible_only_inside_that_block() -> None:
    text = """Seed
/DEF ok /TYPE bool
/IF @ok
/THEN Make x
/DEF x
/THEN Use x
/FROM @x
/OUT done
/END
"""
    parse_program(text)


def test_vars_defined_in_if_are_not_visible_after_end() -> None:
    text = """Seed
/DEF ok /TYPE bool
/IF @ok
/THEN Make x
/DEF x
/END
/THEN Use x
/FROM @x
/OUT done
"""
    with pytest.raises(ParseError, match="undefined variable @x"):
        parse_program(text)


def test_parse_dsl_rejects_block_programs() -> None:
    text = """Seed
/DEF ok /TYPE bool
/IF @ok
/THEN Inside
/OUT done
/END
"""
    with pytest.raises(ParseError, match="flat step programs"):
        parse_dsl(text)
