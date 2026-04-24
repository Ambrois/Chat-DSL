from __future__ import annotations

from chatdsl_core.parser_v02 import Program, parse_dsl, parse_program, steps_to_dicts

def test_parse_program_returns_program_with_step_items() -> None:
    program = parse_program("First step\n/THEN Second step")

    assert isinstance(program, Program)
    assert program.sigil == "@"
    assert len(program.items) == 2
    assert [item.text for item in program.items] == ["First step", "Second step"]

def test_parse_program_preserves_flat_step_structure() -> None:
    text = """Seed topic
/DEF topic
/THEN Use #topic
/FROM #topic
/OUT done
"""
    program = parse_program(text, sigil="#")
    steps = parse_dsl(text, sigil="#")

    assert program.sigil == "#"
    assert all(item.sigil == "#" for item in program.items)
    assert steps_to_dicts(program.items) == steps_to_dicts(steps)
