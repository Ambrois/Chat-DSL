# Chat DSL v0.4 Interface Specification

## 1. Purpose

This document specifies the current UI behavior of the `v0.4` Streamlit app
at `v0.4/app.py`.

It covers:
- visual layout and controls
- interaction flows
- timeline/version semantics
- persistence and message metadata used by the interface

It does not redefine DSL syntax/runtime rules. See:
- `v0.4/spec_changes_from_last.md`
- `v0.4/dsl_v0.4_specs.md`

---

## 2. Runtime Context

- Framework: Streamlit
- Entry point: `streamlit run v0.4/app.py`
- Primary persisted state file: `v0.4/state/chats.json`
- Optional environment variables:
  - `GEMINI_API_KEY`
  - `GEMINI_MODEL`
  - `GEMINI_CHEAP_MODEL`
  - `GEMINI_TIMEOUT`
  - `GEMINI_API_BASE`

---

## 3. Information Architecture

The app has two main regions:

1. Sidebar
- chat list and chat management
- settings
- staging editor

2. Main panel
- chat composer (`st.chat_input`)
- variables panel (DSL mode)
- timeline status banner (when viewing historical version)
- chat transcript

---

## 4. Sidebar Specification

### 4.1 Chats Section

Controls:
- `New chat`
- paginated chat list (page size = 20)
- per-chat menu (`⋮`) with:
  - rename
  - `Move up`
  - `Move down`
  - `Delete`
- pagination:
  - previous `‹`
  - page indicator `current/total`
  - next `›`

Behavior:
- active chat label is prefixed with `•`
- selecting a chat updates `active_chat_id` and reruns
- delete removes only selected chat; app ensures one chat remains active

### 4.2 Settings Section

Controls:
- Theme select:
  - `Gruvbox Dark`
  - `Paper White (WIP)`
  - `Default`
- Mode radio:
  - `Use DSL`
  - `Raw LLM`
- DSL-only toggle:
  - `Run executor (turn off for debugging)`
- DSL-only sigil input:
  - label: `Sigil`
  - exactly one character
- Model select:
  - `Gemini 2.5 Flash`
  - `Gemini 3 Flash`
  - `Gemini 3 Pro`
- Cheap Model select:
  - same options as `Model`
- Timeout number input:
  - label: `Request timeout (seconds, 0 = no timeout)`
  - range: `0..600`

Behavior:
- invalid sigil length triggers a warning and the app uses `@` until corrected

### 4.3 Edit Status

When edit mode is active for the current chat:
- caption: `Editing version vN. Sending will create a new version.`
- `Cancel Edit` clears the edit target

### 4.4 Staging Editor

Form-based draft editor:
- text area (`sidebar_draft`)
- actions:
  - `↩` send
  - `×` clear
  - `⤢` open fullscreen dialog

Rules:
- if sent text contains `/NEXT`, show warning: `You used /NEXT. Use /THEN to start a new step.`
- sending in DSL mode executes `_run_dsl`
- sending in Raw mode executes `_run_raw`

---

## 5. Main Composer Specification

Control:
- `st.chat_input` (`chat_composer`)

Placeholder:
- DSL mode: `Enter DSL (use /THEN to chain steps)`
- Raw mode: `Send a message`

Rules:
- empty input is ignored
- `/NEXT` warning shown in DSL mode
- on send, historical-version view state is cleared

---

## 6. Dialogs

Dialogs are used when `st.dialog` is available.

### 6.1 Draft Editor Dialog

Title: `Draft editor`

Contents:
- large text area (`draft_dialog`)
- `Send`
- `Clear`
- `Close`

Behavior:
- send mirrors staging send behavior
- close syncs dialog text back to sidebar draft

### 6.2 Message Versions Dialog

Title: `Message Versions`

Sections:
- DSL source
- model responses for selected run
- `Vars Before`
- `Vars After`

Actions:
- `View This Version`
- `View Latest`
- `Edit This Version`

### 6.3 Copy Message Dialog

Title: `Copy Message`

Contents:
- caption instructing to use the code-block copy icon
- message body rendered in `st.code`

---

## 7. Transcript Rendering

### 7.1 Display Source

The persisted chat history is append-only, but the UI renders a projected timeline:

- `display_history = project_visible_history(chat_history, cutoff_index=...)`

### 7.2 Message Rendering

For each displayed message:
- assistant: content plus `⋮` details menu
- user DSL: content plus `⋮` actions menu
- user Raw: content only

### 7.3 Assistant Menu (`⋮`)

Displays metadata based on available keys:

- `step_log`:
  - Parsed Output
  - Execution Log
- execution bundle:
  - Parsed Program
  - Execution Trace
  - Execution Logs
  - Vars After
- raw meta JSON
- or `No details available.`

Execution trace rows summarize:
- node path
- node kind
- execution status
- source line
- short summary text

### 7.4 User DSL Menu (`⋮`)

Buttons:
- `Edit`
- `Versions`
- `Copy`

---

## 8. Variables Panel

Shown only in `Use DSL` mode.

Displays a table with:
- variable name
- approximate token count
- short preview

Built-ins such as `ALL` and `CHAT` are hidden from this table.

Open UI issues are tracked in `v0.4/known_issues.md`.

---

## 9. Stored Metadata

For DSL runs, user messages store:
- `thread_id`
- `version`
- `run_id`
- `parsed_steps`
- `execution_logs`
- `vars_before`
- `vars_after`

Assistant messages for DSL runs store:
- `run_id`
- `source_user_message_id`
- optional `step_log` for step-output messages

---

## 10. v0.4-Specific Notes

- the DSL parser/runtime now operates on a nested program AST
- nested `/IF ... /END` blocks are supported
- execution traces include both `if` nodes and step nodes
- branch-local variables do not leak beyond `/END`
