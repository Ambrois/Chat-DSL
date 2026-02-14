from __future__ import annotations

import sys
from pathlib import Path


V02_DIR = Path(__file__).resolve().parents[1]
if str(V02_DIR) not in sys.path:
    sys.path.insert(0, str(V02_DIR))

from versioning_v02 import (
    backfill_history_metadata,
    get_assistant_messages_for_run,
    get_thread_versions,
    next_version_for_thread,
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
