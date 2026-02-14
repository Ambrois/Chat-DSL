from __future__ import annotations

import json
import re
from typing import Any, Callable, Dict, List, Optional, Tuple

from parser_v02 import Step


ModelCall = Callable[[str], str]
_REF_PATTERN = re.compile(r"@([A-Za-z_][A-Za-z0-9_]*)")


def _render_value(value: Any) -> str:
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False)


def _extract_refs(text: str) -> set[str]:
    return set(_REF_PATTERN.findall(text or ""))


def _interpolate(text: str, values: Dict[str, Any]) -> str:
    def repl(match: re.Match[str]) -> str:
        name = match.group(1)
        if name in values:
            return _render_value(values[name])
        return match.group(0)

    return _REF_PATTERN.sub(repl, text or "")


def _resolve_accessible_inputs(step: Step, context: Dict[str, Any]) -> Dict[str, Any]:
    if step.from_vars is None:
        return dict(context)
    return {name: context[name] for name in step.from_vars if name in context}


def build_step_prompt(step: Step, context: Dict[str, Any]) -> str:
    accessible = _resolve_accessible_inputs(step, context)
    embedded: set[str] = set()
    embedded.update(_extract_refs(step.text))
    for spec in step.defs:
        embedded.update(_extract_refs(spec.as_text or ""))

    instruction = _interpolate(step.text, accessible).strip()
    blocks: List[str] = [f"Instruction:\n{instruction}" if instruction else "Instruction:"]

    extra_inputs = [name for name in accessible if name not in embedded]
    if extra_inputs:
        inputs_lines = "\n".join(
            f"- {name}: {_render_value(accessible[name])}" for name in extra_inputs
        )
        blocks.append(f"Inputs:\n{inputs_lines}")

    if step.defs:
        required_lines: List[str] = []
        for spec in step.defs:
            desc = _interpolate(spec.as_text or spec.var_name, accessible)
            required_lines.append(f"- {spec.var_name} ({spec.value_type}): {desc}")
        blocks.append("Required variables:\n" + "\n".join(required_lines))

    if step.out_text is not None:
        blocks.append(f"Output intent:\n{step.out_text}")

    blocks.append("Return JSON with keys:\n- error: 0 or 1\n- out: natural-language string")
    if step.defs:
        blocks.append("Also include:\n- vars: object with all required variables")

    return "\n\n".join(blocks).strip()


def execute_steps(
    steps: List[Step],
    context: Dict[str, Any],
    call_model: Optional[ModelCall] = None,
) -> Tuple[Dict[str, Any], List[Dict[str, Any]], List[str]]:
    """Execute steps with prompt construction and model-call injection support."""
    logs: List[Dict[str, Any]] = []
    visible_outputs: List[str] = []

    for st in steps:
        prompt = build_step_prompt(st, context)
        if call_model is None:
            response = f"stub output for step {st.index}"
        else:
            response = call_model(prompt)

        visible_outputs.append(response)
        logs.append(
            {
                "step_index": st.index,
                "start_line_no": st.start_line_no,
                "text": st.text,
                "prompt": prompt,
                "raw_response": response,
            }
        )

    return context, logs, visible_outputs
