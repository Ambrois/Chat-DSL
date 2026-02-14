from __future__ import annotations

import uuid
from typing import Any, Dict, List, Optional


def new_message_id(prefix: str = "msg") -> str:
    return f"{prefix}-{uuid.uuid4().hex[:12]}"


def _meta(msg: Dict[str, Any]) -> Dict[str, Any]:
    meta = msg.get("meta")
    if not isinstance(meta, dict):
        meta = {}
        msg["meta"] = meta
    return meta


def backfill_history_metadata(history: List[Dict[str, Any]]) -> bool:
    """
    Make legacy history records compatible with versioned runs.
    Mutates history in place and returns whether anything changed.
    """
    changed = False
    current_run_id: Optional[str] = None
    current_user_id: Optional[str] = None

    for msg in history:
        if not isinstance(msg, dict):
            continue
        if not msg.get("id"):
            msg["id"] = new_message_id("msg")
            changed = True

        role = msg.get("role")
        mode = msg.get("mode")

        if role == "user" and mode == "dsl":
            meta = _meta(msg)
            if not meta.get("thread_id"):
                meta["thread_id"] = msg["id"]
                changed = True
            if not isinstance(meta.get("version"), int) or meta["version"] < 1:
                meta["version"] = 1
                changed = True
            if not meta.get("run_id"):
                meta["run_id"] = f"run-{msg['id']}"
                changed = True

            current_run_id = meta["run_id"]
            current_user_id = msg["id"]
            continue

        if role == "assistant":
            if current_run_id is not None:
                meta = _meta(msg)
                if not meta.get("run_id"):
                    meta["run_id"] = current_run_id
                    changed = True
                if current_user_id and not meta.get("source_user_message_id"):
                    meta["source_user_message_id"] = current_user_id
                    changed = True
            continue

        if role == "user":
            current_run_id = None
            current_user_id = None

    return changed


def next_version_for_thread(history: List[Dict[str, Any]], thread_id: str) -> int:
    max_version = 0
    for msg in history:
        if msg.get("role") != "user" or msg.get("mode") != "dsl":
            continue
        meta = msg.get("meta", {})
        if meta.get("thread_id") != thread_id:
            continue
        v = meta.get("version")
        if isinstance(v, int) and v > max_version:
            max_version = v
    return max_version + 1


def get_thread_versions(history: List[Dict[str, Any]], thread_id: str) -> List[Dict[str, Any]]:
    versions: List[Dict[str, Any]] = []
    for idx, msg in enumerate(history):
        if msg.get("role") != "user" or msg.get("mode") != "dsl":
            continue
        meta = msg.get("meta", {})
        if meta.get("thread_id") == thread_id:
            versions.append({"msg": msg, "index": idx})
    versions.sort(
        key=lambda it: (
            it["msg"].get("meta", {}).get("version", 0),
            it["index"],
        )
    )
    return [it["msg"] for it in versions]


def get_assistant_messages_for_run(
    history: List[Dict[str, Any]], run_id: str
) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for msg in history:
        if msg.get("role") != "assistant":
            continue
        meta = msg.get("meta", {})
        if meta.get("run_id") == run_id:
            out.append(msg)
    return out
