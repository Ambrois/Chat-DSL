from __future__ import annotations

from apps.streamlit.vars_panel_v02 import resolve_vars_panel_data


def test_resolve_vars_panel_data_prefers_history_view_vars() -> None:
    active_chat = {"vars": {"persisted": "disk"}}
    active_last_run = {"vars": {"session": "live"}}
    history_view_msg = {"id": "msg-1"}
    display_history = [
        {
            "role": "user",
            "mode": "dsl",
            "meta": {"vars_after": {"from_history": "shown"}},
        }
    ]

    vars_data = resolve_vars_panel_data(
        mode="Use DSL",
        active_chat=active_chat,
        active_last_run=active_last_run,
        history_view_msg=history_view_msg,
        display_history=display_history,
    )

    assert vars_data == {"from_history": "shown"}


def test_resolve_vars_panel_data_uses_session_last_run_when_present() -> None:
    vars_data = resolve_vars_panel_data(
        mode="Use DSL",
        active_chat={"vars": {"persisted": "disk"}},
        active_last_run={"vars": {"session": "live"}},
        history_view_msg=None,
        display_history=[],
    )

    assert vars_data == {"session": "live"}


def test_resolve_vars_panel_data_falls_back_to_persisted_chat_vars_after_reload() -> None:
    vars_data = resolve_vars_panel_data(
        mode="Use DSL",
        active_chat={"vars": {"persisted": "disk", "count": 3}},
        active_last_run=None,
        history_view_msg=None,
        display_history=[],
    )

    assert vars_data == {"persisted": "disk", "count": 3}


def test_resolve_vars_panel_data_returns_none_for_non_dsl_mode() -> None:
    vars_data = resolve_vars_panel_data(
        mode="Raw chat",
        active_chat={"vars": {"persisted": "disk"}},
        active_last_run=None,
        history_view_msg=None,
        display_history=[],
    )

    assert vars_data is None
