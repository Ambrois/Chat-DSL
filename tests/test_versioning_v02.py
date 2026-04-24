from __future__ import annotations

from chatdsl_core.versioning_v02 import (
    backfill_history_metadata,
    build_edit_run_context,
    cutoff_index_for_version_view,
    find_message_index,
    get_assistant_messages_for_run,
    get_thread_versions,
    next_version_for_thread,
    project_visible_history,
)

def test_backfill_adds_ids_and_run_links() -> None:
    history = [
        {"role": "user", "mode": "dsl", "content": "A"},
        {"role": "assistant", "mode": "dsl", "content": "A1"},
        {"role": "assistant", "mode": "dsl", "content": "A2"},
        {"role": "user", "mode": "raw", "content": "x"},
        {"role": "assistant", "mode": "raw", "content": "y"},
    ]
    changed = backfill_history_metadata(history)
    assert changed is True
    assert history[0]["id"]
    assert history[0]["meta"]["thread_id"] == history[0]["id"]
    assert history[0]["meta"]["version"] == 1
    run_id = history[0]["meta"]["run_id"]
    assert history[1]["meta"]["run_id"] == run_id
    assert history[1]["meta"]["source_user_message_id"] == history[0]["id"]
    assert history[2]["meta"]["run_id"] == run_id

def test_next_version_for_thread_and_sorted_versions() -> None:
    history = [
        {
            "role": "user",
            "mode": "dsl",
            "id": "m1",
            "meta": {"thread_id": "t1", "version": 2, "run_id": "r2"},
            "content": "v2",
        },
        {
            "role": "user",
            "mode": "dsl",
            "id": "m0",
            "meta": {"thread_id": "t1", "version": 1, "run_id": "r1"},
            "content": "v1",
        },
    ]
    assert next_version_for_thread(history, "t1") == 3
    versions = get_thread_versions(history, "t1")
    assert [m["content"] for m in versions] == ["v1", "v2"]

def test_get_assistant_messages_for_run() -> None:
    history = [
        {"role": "assistant", "meta": {"run_id": "r1"}, "content": "a"},
        {"role": "assistant", "meta": {"run_id": "r2"}, "content": "b"},
        {"role": "assistant", "meta": {"run_id": "r1"}, "content": "c"},
    ]
    msgs = get_assistant_messages_for_run(history, "r1")
    assert [m["content"] for m in msgs] == ["a", "c"]

def _sample_branching_history() -> list[dict]:
    return [
        {
            "id": "u1",
            "role": "user",
            "mode": "dsl",
            "content": "u1",
            "meta": {"thread_id": "t1", "version": 1, "run_id": "r1"},
        },
        {"id": "a1", "role": "assistant", "mode": "dsl", "content": "a1", "meta": {"run_id": "r1"}},
        {
            "id": "u2v1",
            "role": "user",
            "mode": "dsl",
            "content": "u2-v1",
            "meta": {"thread_id": "t2", "version": 1, "run_id": "r2"},
        },
        {"id": "a2", "role": "assistant", "mode": "dsl", "content": "a2", "meta": {"run_id": "r2"}},
        {
            "id": "u3v1",
            "role": "user",
            "mode": "dsl",
            "content": "u3-v1",
            "meta": {"thread_id": "t3", "version": 1, "run_id": "r3"},
        },
        {"id": "a3", "role": "assistant", "mode": "dsl", "content": "a3", "meta": {"run_id": "r3"}},
        {
            "id": "u2v2",
            "role": "user",
            "mode": "dsl",
            "content": "u2-v2",
            "meta": {
                "thread_id": "t2",
                "version": 2,
                "run_id": "r4",
                "edited_from_message_id": "u2v1",
            },
        },
        {"id": "a2b", "role": "assistant", "mode": "dsl", "content": "a2b", "meta": {"run_id": "r4"}},
    ]

def test_project_visible_history_replaces_suffix_after_edit() -> None:
    history = _sample_branching_history()
    projected = project_visible_history(history)
    assert [m["id"] for m in projected] == ["u1", "a1", "u2v2", "a2b"]

def test_cutoff_index_for_version_view_replays_old_timeline() -> None:
    history = _sample_branching_history()
    cutoff = cutoff_index_for_version_view(history, "u2v1")
    assert cutoff == find_message_index(history, "u2v2") - 1
    projected = project_visible_history(history, cutoff_index=cutoff)
    assert [m["id"] for m in projected] == ["u1", "a1", "u2v1", "a2", "u3v1", "a3"]

def test_cutoff_index_for_version_view_handles_ancestor_replacement() -> None:
    history = [
        {
            "id": "u1v1",
            "role": "user",
            "mode": "dsl",
            "content": "u1-v1",
            "meta": {"thread_id": "t1", "version": 1, "run_id": "r1"},
        },
        {"id": "a1", "role": "assistant", "mode": "dsl", "content": "a1", "meta": {"run_id": "r1"}},
        {
            "id": "u2v1",
            "role": "user",
            "mode": "dsl",
            "content": "u2-v1",
            "meta": {"thread_id": "t2", "version": 1, "run_id": "r2"},
        },
        {"id": "a2", "role": "assistant", "mode": "dsl", "content": "a2", "meta": {"run_id": "r2"}},
        {
            "id": "u1v2",
            "role": "user",
            "mode": "dsl",
            "content": "u1-v2",
            "meta": {
                "thread_id": "t1",
                "version": 2,
                "run_id": "r3",
                "edited_from_message_id": "u1v1",
            },
        },
        {"id": "a1b", "role": "assistant", "mode": "dsl", "content": "a1b", "meta": {"run_id": "r3"}},
    ]
    cutoff = cutoff_index_for_version_view(history, "u2v1")
    projected = project_visible_history(history, cutoff_index=cutoff)
    assert [m["id"] for m in projected] == ["u1v1", "a1", "u2v1", "a2"]

def test_project_visible_history_uses_source_cutoff_for_hidden_edit_source() -> None:
    history = [
        {
            "id": "u1v1",
            "role": "user",
            "mode": "dsl",
            "content": "u1-v1",
            "meta": {"thread_id": "t1", "version": 1, "run_id": "r1"},
        },
        {"id": "a1", "role": "assistant", "mode": "dsl", "content": "a1", "meta": {"run_id": "r1"}},
        {
            "id": "u2v1",
            "role": "user",
            "mode": "dsl",
            "content": "u2-v1",
            "meta": {"thread_id": "t2", "version": 1, "run_id": "r2"},
        },
        {"id": "a2", "role": "assistant", "mode": "dsl", "content": "a2", "meta": {"run_id": "r2"}},
        {
            "id": "u1v2",
            "role": "user",
            "mode": "dsl",
            "content": "u1-v2",
            "meta": {
                "thread_id": "t1",
                "version": 2,
                "run_id": "r3",
                "edited_from_message_id": "u1v1",
            },
        },
        {"id": "a1b", "role": "assistant", "mode": "dsl", "content": "a1b", "meta": {"run_id": "r3"}},
        {
            "id": "u2v2",
            "role": "user",
            "mode": "dsl",
            "content": "u2-v2",
            "meta": {
                "thread_id": "t2",
                "version": 2,
                "run_id": "r4",
                "edited_from_message_id": "u2v1",
                "source_cutoff_index": 3,
            },
        },
        {"id": "a2b", "role": "assistant", "mode": "dsl", "content": "a2b", "meta": {"run_id": "r4"}},
    ]
    projected = project_visible_history(history)
    assert [m["id"] for m in projected] == ["u1v1", "a1", "u2v2", "a2b"]

def test_build_edit_run_context_uses_visible_prefix_before_source_version() -> None:
    history = _sample_branching_history()

    context = build_edit_run_context(history, "u2v1")

    assert context.source_cutoff_index == find_message_index(history, "u2v2") - 1
    assert [msg["id"] for msg in context.visible_history_before] == ["u1", "a1"]
    assert context.vars_before == {}

def test_build_edit_run_context_prefers_recorded_vars_before() -> None:
    history = [
        {
            "id": "u1",
            "role": "user",
            "mode": "dsl",
            "content": "seed",
            "meta": {
                "thread_id": "t1",
                "version": 1,
                "run_id": "r1",
                "vars_after": {"seed": "alpha"},
            },
        },
        {"id": "a1", "role": "assistant", "mode": "dsl", "content": "done", "meta": {"run_id": "r1"}},
        {
            "id": "u2",
            "role": "user",
            "mode": "dsl",
            "content": "use seed",
            "meta": {
                "thread_id": "t2",
                "version": 1,
                "run_id": "r2",
                "vars_before": {"seed": "recorded"},
            },
        },
    ]

    context = build_edit_run_context(history, "u2")

    assert [msg["id"] for msg in context.visible_history_before] == ["u1", "a1"]
    assert context.vars_before == {"seed": "recorded"}

def test_build_edit_run_context_reconstructs_vars_from_prior_visible_timeline() -> None:
    history = [
        {
            "id": "u1v1",
            "role": "user",
            "mode": "dsl",
            "content": "set root",
            "meta": {
                "thread_id": "t1",
                "version": 1,
                "run_id": "r1",
                "vars_after": {"root": "old"},
            },
        },
        {"id": "a1", "role": "assistant", "mode": "dsl", "content": "done", "meta": {"run_id": "r1"}},
        {
            "id": "u2v1",
            "role": "user",
            "mode": "dsl",
            "content": "branch child",
            "meta": {"thread_id": "t2", "version": 1, "run_id": "r2"},
        },
        {"id": "a2", "role": "assistant", "mode": "dsl", "content": "child done", "meta": {"run_id": "r2"}},
        {
            "id": "u1v2",
            "role": "user",
            "mode": "dsl",
            "content": "replace root",
            "meta": {
                "thread_id": "t1",
                "version": 2,
                "run_id": "r3",
                "edited_from_message_id": "u1v1",
            },
        },
        {"id": "a1b", "role": "assistant", "mode": "dsl", "content": "replaced", "meta": {"run_id": "r3"}},
    ]

    context = build_edit_run_context(history, "u2v1")

    assert [msg["id"] for msg in context.visible_history_before] == ["u1v1", "a1"]
    assert context.vars_before == {"root": "old"}
