from __future__ import annotations

import sys
from pathlib import Path


V02_DIR = Path(__file__).resolve().parents[1]
if str(V02_DIR) not in sys.path:
    sys.path.insert(0, str(V02_DIR))

from parser_v02 import parse_dsl


def _normalized(steps: list) -> list:
    out = []
    for st in steps:
        out.append(
            {
                "index": st.index,
                "text": st.text,
                "from_vars": st.from_vars,
                "defs": [(d.var_name, d.value_type, d.as_text) for d in st.defs],
                "out_text": st.out_text,
                "commands": [(c.name, c.payload) for c in st.commands],
            }
        )
    return out


def test_indented_and_non_indented_commands_parse_equally() -> None:
    plain = """Plan the response.
/FROM @topic, @audience
/DEF score /TYPE float /AS confidence score
/OUT concise summary
/THEN second step
/OUT include one caveat
"""
    indented = """Plan the response.
    /FROM @topic, @audience
  /DEF score /TYPE float /AS confidence score
     /OUT concise summary
    /THEN second step
      /OUT include one caveat
"""
    assert _normalized(parse_dsl(plain)) == _normalized(parse_dsl(indented))


def test_then_is_command_token_not_prefix() -> None:
    steps = parse_dsl("single step\n/THENX not-a-split")
    assert len(steps) == 1
    assert steps[0].commands[0].name == "THENX"
