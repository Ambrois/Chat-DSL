from __future__ import annotations

from typing import Any, Mapping, Sequence


def resolve_vars_panel_data(
    *,
    mode: str,
    active_chat: Mapping[str, Any],
    active_last_run: Mapping[str, Any] | None,
    history_view_msg: Mapping[str, Any] | None,
    display_history: Sequence[Mapping[str, Any]],
) -> dict[str, Any] | None:
    if mode != "Use DSL":
        return None

    if history_view_msg is not None:
        for msg in reversed(display_history):
            if msg.get("role") != "user" or msg.get("mode") != "dsl":
                continue
            meta = msg.get("meta", {})
            if isinstance(meta.get("vars_after"), dict):
                return dict(meta["vars_after"])
        return {}

    if active_last_run is not None:
        run_vars = active_last_run.get("vars")
        if isinstance(run_vars, dict):
            return dict(run_vars)
        return {}

    persisted_vars = active_chat.get("vars")
    if isinstance(persisted_vars, dict):
        return dict(persisted_vars)
    return {}
