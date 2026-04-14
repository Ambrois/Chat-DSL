# v0.4 Known Issues

Manual review notes captured on 2026-04-01 while hardening `feature/v0.4-integration`.

## Open Bugs

### 1. Historical edits use the wrong chat timeline

Severity: high

Files:
- `v0.4/app.py`
- `v0.4/versioning_v02.py`

Relevant code:
- `v0.4/app.py:756`
- `v0.4/app.py:777`
- `v0.4/app.py:790`
- `v0.4/versioning_v02.py:125`

Problem:
- Editing an older DSL message restores `vars_before` from the selected version when available.
- But execution still builds `chat_lines` from the full current `chat_history`.
- As a result, `@CHAT`, `@ALL`, and `/FROM ... /IN @CHAT` can see messages from newer branches or later edits that were not visible at the version being edited.

Expected:
- Re-executing a historical version should use the projected timeline for that version, not the latest chat timeline.

Suggested fix:
- In the edit path, derive the cutoff with `cutoff_index_for_version_view(...)`.
- Build `chat_lines` from `project_visible_history(..., cutoff_index=...)` before calling `execute_program(...)`.


### 2. Backfilled legacy histories edit against current vars

Severity: medium

Files:
- `v0.4/app.py`
- `v0.4/versioning_v02.py`

Relevant code:
- `v0.4/app.py:754`
- `v0.4/app.py:766`
- `v0.4/versioning_v02.py:19`

Problem:
- Legacy chats are backfilled with IDs, thread IDs, versions, and run links.
- They are not backfilled with `vars_before` snapshots.
- When editing one of those older messages, the app falls back to the latest `active_chat["vars"]`.
- That means "Edit This Version" can branch from today's variables instead of the variables that existed before the original run.

Expected:
- Editing an old version should use the original pre-run variable state, or the UI should explicitly block/mark the edit as non-reproducible.

Suggested fix:
- Either backfill enough metadata to reconstruct historical `vars_before`, or compute it from the projected history before editing.
- If reconstruction is not possible, show a warning and disable version-faithful editing for those records.


### 3. Variables panel ignores persisted vars after reload

Severity: medium

Files:
- `v0.4/app.py`

Relevant code:
- `v0.4/app.py:913`
- `v0.4/app.py:1378`
- `v0.4/app.py:1390`

Problem:
- Chat vars are loaded from disk into `active_chat["vars"]`.
- The Variables panel only displays `history_view_msg` vars or session-local `active_last_run`.
- After restarting Streamlit or loading an existing chat, the UI can show "No variables yet" even when the chat has persisted vars on disk.

Expected:
- When not viewing a historical version, the Variables panel should fall back to persisted chat state from `active_chat["vars"]`.

Suggested fix:
- Use `active_chat["vars"]` as the non-history fallback when `active_last_run` is missing.

