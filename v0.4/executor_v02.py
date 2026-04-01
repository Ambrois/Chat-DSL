from __future__ import annotations

import json
import re
from functools import lru_cache
from typing import Any, Callable, Dict, List, Optional, Tuple, TypedDict

from parser_v02 import FromItem, IfNode, Program, ProgramNode, Step


class ResponseSchema(TypedDict):
    type: str
    properties: Dict[str, Any]
    required: List[str]


ModelCall = Callable[[str, ResponseSchema], str]
CheapModelCall = Callable[[str], str]
_BUILTIN_VAR_NAMES = {"ALL", "CHAT"}


@lru_cache(maxsize=None)
def _ref_pattern(sigil: str) -> re.Pattern[str]:
    return re.compile(rf"(?<![A-Za-z0-9_]){re.escape(sigil)}([A-Za-z_][A-Za-z0-9_]*)\b")


def _render_value(value: Any) -> str:
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False)


def _extract_refs(text: str, sigil: str) -> set[str]:
    return set(_ref_pattern(sigil).findall(text or ""))


def _interpolate(text: str, values: Dict[str, Any], sigil: str) -> str:
    pattern = _ref_pattern(sigil)

    def repl(match: re.Match[str]) -> str:
        name = match.group(1)
        if name in values:
            return _render_value(values[name])
        return match.group(0)

    return pattern.sub(repl, text or "")


def _resolve_accessible_inputs(step: Step, context: Dict[str, Any]) -> Dict[str, Any]:
    if step.from_items is None:
        return {"CHAT": context["CHAT"]} if "CHAT" in context else {}

    names = [item.value for item in step.from_items if item.kind == "var"]
    return {name: context[name] for name in names if name in context}


def _render_chat_history_text(chat_history: List[str]) -> str:
    lines = [line for line in chat_history if isinstance(line, str) and line.strip()]
    if not lines:
        return ""
    return "\n\n".join(lines)


def _build_builtin_values(context: Dict[str, Any], chat_history: List[str]) -> Dict[str, str]:
    chat_text = _render_chat_history_text(chat_history)

    vars_lines: List[str] = []
    for name, value in context.items():
        if name in _BUILTIN_VAR_NAMES:
            continue
        vars_lines.append(f"- {name}: {_render_value(value)}")

    all_parts: List[str] = []
    if chat_text:
        all_parts.append(f"Chat history:\n{chat_text}")
    if vars_lines:
        all_parts.append("Variables:\n" + "\n".join(vars_lines))

    return {
        "CHAT": chat_text,
        "ALL": "\n\n".join(all_parts).strip(),
    }


def build_step_prompt(
    step: Step,
    context: Dict[str, Any],
    nat_inputs: Optional[List[Tuple[str, str]]] = None,
) -> str:
    sigil = step.sigil
    accessible = _resolve_accessible_inputs(step, context)
    embedded: set[str] = set()
    embedded.update(_extract_refs(step.text, sigil))
    for spec in step.defs:
        embedded.update(_extract_refs(spec.as_text or "", sigil))

    instruction = _interpolate(step.text, accessible, sigil).strip()
    blocks: List[str] = [f"Instruction:\n{instruction}" if instruction else "Instruction:"]

    explicit_from = {item.value for item in (step.from_items or []) if item.kind == "var"}
    extra_inputs = [
        name
        for name in accessible
        if name not in embedded
        and (name not in _BUILTIN_VAR_NAMES or name in explicit_from)
    ]
    nat_inputs = list(nat_inputs or [])
    if extra_inputs:
        inputs_lines = "\n".join(
            f"- {name}: {_render_value(accessible[name])}" for name in extra_inputs
        )
        blocks.append(f"Inputs:\n{inputs_lines}")
    if nat_inputs:
        nat_lines = "\n".join(f"- {label}: {value}" for label, value in nat_inputs)
        if extra_inputs:
            blocks[-1] += "\n" + nat_lines
        else:
            blocks.append(f"Inputs:\n{nat_lines}")

    if step.defs:
        required_lines: List[str] = []
        for spec in step.defs:
            desc = _interpolate(spec.as_text or spec.var_name, accessible, sigil)
            required_lines.append(f"- {spec.var_name} ({spec.value_type}): {desc}")
        blocks.append("Required variables:\n" + "\n".join(required_lines))

    if step.out_text is not None:
        blocks.append(f"Output intent:\n{step.out_text}")

    blocks.append(
        "Output format requirements:\n"
        "- Respond with ONLY a JSON object.\n"
        "- Do not wrap JSON in markdown/code fences.\n"
        "- Keys required in every response: error, out.\n"
        "- error must be 0 or 1.\n"
        "- out must be a natural-language JSON string."
    )
    if step.defs:
        blocks.append(
            "Also include:\n"
            "- vars: JSON object containing every required variable by exact name."
        )
        sample_vars = ", ".join([f'"{spec.var_name}": <{spec.value_type}>' for spec in step.defs])
        blocks.append(
            "Example JSON shape:\n"
            f'{{"error": 0, "out": "done", "vars": {{{sample_vars}}}}}'
        )
    else:
        blocks.append('Example JSON shape:\n{"error": 0, "out": "done"}')

    return "\n\n".join(blocks).strip()


def _schema_type_for_def(type_name: str) -> str:
    t = type_name.lower()
    if t in {"nat", "str"}:
        return "string"
    if t == "int":
        return "integer"
    if t == "float":
        return "number"
    if t == "bool":
        return "boolean"
    return "string"


def build_response_schema(step: Step) -> ResponseSchema:
    props: Dict[str, Any] = {
        "error": {
            "type": "integer",
        },
        "out": {
            "type": "string",
        },
    }
    required = ["error", "out"]

    if step.defs:
        vars_props: Dict[str, Any] = {}
        vars_required: List[str] = []
        for spec in step.defs:
            vars_props[spec.var_name] = {"type": _schema_type_for_def(spec.value_type)}
            vars_required.append(spec.var_name)

        props["vars"] = {
            "type": "object",
            "properties": vars_props,
            "required": vars_required,
        }
        required.append("vars")

    return {
        "type": "object",
        "properties": props,
        "required": required,
    }


def _default_stub_response(step: Step) -> str:
    payload: Dict[str, Any] = {
        "error": 0,
        "out": f"stub output for step {step.index}",
    }
    if step.defs:
        payload["vars"] = {spec.var_name: f"stub value for {spec.var_name}" for spec in step.defs}
    return json.dumps(payload)


def _build_prefilter_prompt(description: str, scope_var: str, scope_text: str, sigil: str) -> str:
    return (
        "Task: extract matching content with minimal rewriting.\n\n"
        f"Description:\n{description}\n\n"
        f"Scope ({sigil}{scope_var}):\n{scope_text}\n\n"
        "Rules:\n"
        "- Return only text matching the description.\n"
        "- Keep original wording/order when possible.\n"
        "- Return plain text only.\n"
        "- If nothing matches, return an empty string."
    )


def _run_prefilter(
    item: FromItem,
    runtime_context: Dict[str, Any],
    cheap_model_call: Optional[CheapModelCall],
    sigil: str,
) -> Tuple[str, str]:
    scope_var = item.scope_var or "ALL"
    scope_text = _render_value(runtime_context.get(scope_var, ""))
    prompt = _build_prefilter_prompt(item.value, scope_var, scope_text, sigil)
    if cheap_model_call is None:
        filtered_text = scope_text
    else:
        filtered_text = cheap_model_call(prompt)
    if not isinstance(filtered_text, str):
        raise ValueError("cheap prefilter call must return a string")
    label = f"{item.value} (from {sigil}{scope_var})"
    return label, filtered_text


def _parse_runtime_response(raw_response: str, step: Step) -> Dict[str, Any]:
    try:
        parsed = json.loads(raw_response)
    except json.JSONDecodeError as exc:
        snippet = raw_response.strip().replace("\n", "\\n")
        if len(snippet) > 220:
            snippet = snippet[:220] + "..."
        raise ValueError(
            f"Step {step.index} (line {step.start_line_no}): model response is not valid JSON. Raw response starts with: {snippet!r}"
        ) from exc

    if not isinstance(parsed, dict):
        raise ValueError(
            f"Step {step.index} (line {step.start_line_no}): model response must be a JSON object"
        )

    if "error" not in parsed or "out" not in parsed:
        raise ValueError(
            f"Step {step.index} (line {step.start_line_no}): response missing required keys 'error' and/or 'out'"
        )

    error_val = parsed["error"]
    if error_val not in (0, 1):
        raise ValueError(
            f"Step {step.index} (line {step.start_line_no}): 'error' must be 0 or 1"
        )

    out_val = parsed["out"]
    if not isinstance(out_val, str):
        raise ValueError(
            f"Step {step.index} (line {step.start_line_no}): 'out' must be a JSON string"
        )

    if step.defs:
        vars_val = parsed.get("vars")
        if not isinstance(vars_val, dict):
            raise ValueError(
                f"Step {step.index} (line {step.start_line_no}): response must include object key 'vars'"
            )
        missing = [spec.var_name for spec in step.defs if spec.var_name not in vars_val]
        if missing:
            raise ValueError(
                f"Step {step.index} (line {step.start_line_no}): missing /DEF values in vars: {missing}"
            )

    if error_val == 1:
        raise RuntimeError(
            f"Step {step.index} (line {step.start_line_no}): model returned error=1"
        )

    return parsed


def _validate_def_value(step: Step, var_name: str, type_name: str, value: Any) -> None:
    if value is None:
        raise ValueError(
            f"Step {step.index} (line {step.start_line_no}): /DEF value for '{var_name}' cannot be null"
        )

    t = type_name.lower()
    if t in {"nat", "str"}:
        if not isinstance(value, str):
            raise ValueError(
                f"Step {step.index} (line {step.start_line_no}): '{var_name}' expected {t} (string)"
            )
        return

    if t == "int":
        if type(value) is not int:
            raise ValueError(
                f"Step {step.index} (line {step.start_line_no}): '{var_name}' expected int"
            )
        return

    if t == "float":
        if type(value) not in {int, float}:
            raise ValueError(
                f"Step {step.index} (line {step.start_line_no}): '{var_name}' expected float"
            )
        return

    if t == "bool":
        if type(value) is not bool:
            raise ValueError(
                f"Step {step.index} (line {step.start_line_no}): '{var_name}' expected bool"
            )
        return

    raise ValueError(
        f"Step {step.index} (line {step.start_line_no}): unsupported /TYPE '{type_name}'"
    )


def _execute_step_node(
    step: Step,
    context: Dict[str, Any],
    logs: List[Dict[str, Any]],
    visible_outputs: List[str],
    chat_lines: List[str],
    call_model: Optional[ModelCall],
    cheap_model_call: Optional[CheapModelCall],
    node_path: List[int],
) -> None:
    sigil = step.sigil
    runtime_context = dict(context)
    runtime_context.update(_build_builtin_values(context, chat_lines + visible_outputs))
    nat_inputs: List[Tuple[str, str]] = []
    prefilter_logs: List[Dict[str, str]] = []
    for item in step.from_items or []:
        if item.kind != "nat":
            continue
        label, filtered = _run_prefilter(item, runtime_context, cheap_model_call, sigil)
        nat_inputs.append((label, filtered))
        prefilter_logs.append(
            {
                "description": item.value,
                "scope_var": item.scope_var or "ALL",
                "filtered_text": filtered,
            }
        )

    prompt = build_step_prompt(step, runtime_context, nat_inputs=nat_inputs)
    response_schema = build_response_schema(step)
    if call_model is None:
        response = _default_stub_response(step)
    else:
        response = call_model(prompt, response_schema)

    parsed = _parse_runtime_response(response, step)

    staged_updates: Dict[str, Any] = {}
    if step.defs:
        vars_payload = parsed["vars"]
        for spec in step.defs:
            value = vars_payload[spec.var_name]
            _validate_def_value(step, spec.var_name, spec.value_type, value)
            staged_updates[spec.var_name] = value

    context.update(staged_updates)
    visible_outputs.append(parsed["out"])
    logs.append(
        {
            "node_kind": "step",
            "node_path": list(node_path),
            "depth": len(node_path) - 1,
            "execution": "executed",
            "step_index": step.index,
            "start_line_no": step.start_line_no,
            "text": step.text,
            "output": parsed["out"],
            "prompt": prompt,
            "response_schema": response_schema,
            "raw_response": response,
            "parsed_json": parsed,
            "staged_updates": staged_updates,
            "prefilter_logs": prefilter_logs,
        }
    )


def _execute_program_nodes(
    items: List[ProgramNode],
    context: Dict[str, Any],
    logs: List[Dict[str, Any]],
    visible_outputs: List[str],
    chat_lines: List[str],
    call_model: Optional[ModelCall],
    cheap_model_call: Optional[CheapModelCall],
    path_prefix: List[int],
) -> None:
    for child_index, item in enumerate(items):
        node_path = [*path_prefix, child_index]
        if isinstance(item, Step):
            _execute_step_node(
                item,
                context,
                logs,
                visible_outputs,
                chat_lines,
                call_model,
                cheap_model_call,
                node_path,
            )
            continue

        if item.condition_var not in context:
            raise ValueError(
                f"Line {item.start_line_no}: missing /IF variable '{item.condition_var}' at runtime"
            )

        guard_value = context[item.condition_var]
        if type(guard_value) is not bool:
            raise ValueError(
                f"Line {item.start_line_no}: /IF variable '{item.condition_var}' must be bool at runtime"
            )

        logs.append(
            {
                "node_kind": "if",
                "node_path": node_path,
                "depth": len(node_path) - 1,
                "start_line_no": item.start_line_no,
                "condition_var": item.condition_var,
                "condition_value": guard_value,
                "execution": "entered" if guard_value else "skipped",
                "child_count": len(item.items),
            }
        )

        if not guard_value:
            continue

        branch_context = dict(context)
        _execute_program_nodes(
            item.items,
            branch_context,
            logs,
            visible_outputs,
            chat_lines,
            call_model,
            cheap_model_call,
            node_path,
        )


def execute_steps(
    steps: List[Step],
    context: Dict[str, Any],
    call_model: Optional[ModelCall] = None,
    chat_history: Optional[List[str]] = None,
    cheap_model_call: Optional[CheapModelCall] = None,
) -> Tuple[Dict[str, Any], List[Dict[str, Any]], List[str]]:
    """Execute steps with prompt construction and model-call injection support."""
    logs: List[Dict[str, Any]] = []
    visible_outputs: List[str] = []
    chat_lines = list(chat_history or [])

    for st in steps:
        _execute_step_node(
            st,
            context,
            logs,
            visible_outputs,
            chat_lines,
            call_model,
            cheap_model_call,
            [st.index],
        )

    return context, logs, visible_outputs


def execute_program(
    program: Program,
    context: Dict[str, Any],
    call_model: Optional[ModelCall] = None,
    chat_history: Optional[List[str]] = None,
    cheap_model_call: Optional[CheapModelCall] = None,
) -> Tuple[Dict[str, Any], List[Dict[str, Any]], List[str]]:
    """Execute a v0.4 Program AST with nested /IF blocks."""
    logs: List[Dict[str, Any]] = []
    visible_outputs: List[str] = []
    chat_lines = list(chat_history or [])

    _execute_program_nodes(
        program.items,
        context,
        logs,
        visible_outputs,
        chat_lines,
        call_model,
        cheap_model_call,
        [],
    )

    return context, logs, visible_outputs
