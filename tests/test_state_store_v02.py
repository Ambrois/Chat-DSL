from __future__ import annotations

import json
from pathlib import Path

from chatdsl_core import state_store_v02


def _set_paths(tmp_path: Path) -> Path:
    new_dir = tmp_path / "apps" / "streamlit" / "state"

    state_store_v02._STATE_DIR = new_dir
    state_store_v02._VARS_PATH = new_dir / "vars.json"
    state_store_v02._HISTORY_PATH = new_dir / "chat_history.json"
    state_store_v02._CHATS_PATH = new_dir / "chats.json"

    return new_dir


def test_load_chats_reads_active_state_dir(tmp_path: Path) -> None:
    new_dir = _set_paths(tmp_path)
    new_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "active_chat_id": "chat-1",
        "chats": [{"id": "chat-1", "name": "Default", "history": [], "vars": {}}],
    }
    (new_dir / "chats.json").write_text(json.dumps(payload), encoding="utf-8")

    loaded = state_store_v02.load_chats()

    assert loaded == payload


def test_load_chats_bootstraps_from_active_vars_and_history(tmp_path: Path) -> None:
    new_dir = _set_paths(tmp_path)
    new_dir.mkdir(parents=True, exist_ok=True)
    (new_dir / "vars.json").write_text(json.dumps({"topic": "dsl"}), encoding="utf-8")
    history = [{"role": "user", "content": "hello"}]
    (new_dir / "chat_history.json").write_text(json.dumps(history), encoding="utf-8")

    loaded = state_store_v02.load_chats()

    assert loaded == {
        "active_chat_id": "chat-1",
        "chats": [
            {
                "id": "chat-1",
                "name": "Default",
                "history": history,
                "vars": {"topic": "dsl"},
            }
        ],
    }


def test_save_chats_writes_to_active_state_dir(tmp_path: Path) -> None:
    new_dir = _set_paths(tmp_path)
    state = {
        "active_chat_id": "chat-1",
        "chats": [{"id": "chat-1", "name": "Default", "history": [], "vars": {}}],
    }

    state_store_v02.save_chats(state)

    assert (new_dir / "chats.json").exists()
