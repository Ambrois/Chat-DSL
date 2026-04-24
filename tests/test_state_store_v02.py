from __future__ import annotations

import json
from pathlib import Path

from chatdsl_core import state_store_v02


def _set_paths(tmp_path: Path) -> tuple[Path, Path]:
    new_dir = tmp_path / "apps" / "streamlit" / "state"
    legacy_dir = tmp_path / "v0.4" / "state"

    state_store_v02._STATE_DIR = new_dir
    state_store_v02._LEGACY_STATE_DIR = legacy_dir
    state_store_v02._VARS_PATH = new_dir / "vars.json"
    state_store_v02._HISTORY_PATH = new_dir / "chat_history.json"
    state_store_v02._CHATS_PATH = new_dir / "chats.json"
    state_store_v02._LEGACY_VARS_PATH = legacy_dir / "vars.json"
    state_store_v02._LEGACY_HISTORY_PATH = legacy_dir / "chat_history.json"
    state_store_v02._LEGACY_CHATS_PATH = legacy_dir / "chats.json"

    return new_dir, legacy_dir


def test_load_chats_falls_back_to_legacy_state_dir(tmp_path: Path) -> None:
    _, legacy_dir = _set_paths(tmp_path)
    legacy_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "active_chat_id": "chat-1",
        "chats": [{"id": "chat-1", "name": "Default", "history": [], "vars": {}}],
    }
    (legacy_dir / "chats.json").write_text(json.dumps(payload), encoding="utf-8")

    loaded = state_store_v02.load_chats()

    assert loaded == payload


def test_save_chats_writes_to_active_state_dir(tmp_path: Path) -> None:
    new_dir, legacy_dir = _set_paths(tmp_path)
    state = {
        "active_chat_id": "chat-1",
        "chats": [{"id": "chat-1", "name": "Default", "history": [], "vars": {}}],
    }

    state_store_v02.save_chats(state)

    assert (new_dir / "chats.json").exists()
    assert not (legacy_dir / "chats.json").exists()
