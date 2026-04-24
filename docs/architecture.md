# Architecture

This document explains how Chat DSL is organized today.

It describes the current repository structure, the active runtime path, and the boundaries that should not be changed casually.

## System overview

Chat DSL is a local, versioned DSL experimentation repository centered on a Streamlit app and a small execution stack:

```text
DSL text -> parser -> program AST -> executor -> model adapter/client -> outputs and vars -> persisted chat state -> Streamlit UI
```

The active system is organized around:

- `apps/streamlit/` as the active home of the Streamlit app
- `chatdsl_core/` as the active home of shared runtime code
- `tests/` as the active home of the current test suite
- `archive/` as the home of historical version snapshots
- `v0.4/` as historical version-specific docs and a legacy state fallback location

Earlier version folders remain useful for reference and regression comparison, but they are no longer the default target for new product work.

## Repository layout

### Active implementation

- `apps/streamlit/`: active Streamlit app and app-specific helpers
- `chatdsl_core/`: active parser, executor, runtime wrapper, model integration, persistence, and versioning code
- `tests/`: active test suite

### Historical snapshots

- `archive/v0.1/`: frozen early baseline
- `archive/v0.2/`: intermediate version snapshot
- `archive/v0.3/`: stable predecessor to `v0.4`

### Historical reference material

- `v0.4/`: historical version docs and legacy state retained at the repo root

Each archived version directory is largely self-contained. This makes history easy to inspect without treating archived code as part of the active implementation.

### Project docs

- `docs/`: project-level docs such as roadmap, architecture, and operating model

## Major components

### Streamlit app

Key file:
- `apps/streamlit/app.py`

Responsibilities:
- render the interactive UI
- manage user input and mode selection
- load and save chat state
- trigger DSL execution or raw model calls
- display version history, variables, outputs, and execution traces

Key helper:
- `apps/streamlit/dsl_render_utils.py`

### Parser

Key file:
- `chatdsl_core/parser_v02.py`

Responsibilities:
- parse DSL text into a `Program` AST
- validate command structure and variable references
- support `v0.4` block-structured control flow such as nested `/IF ... /END`
- preserve parse metadata such as line numbers and sigils for downstream reporting

Primary data structures:
- `Program`
- `Step`
- `IfNode`
- `FromItem`
- `DefSpec`

### Executor

Key file:
- `chatdsl_core/executor_v02.py`

Responsibilities:
- traverse the parsed program
- build model prompts
- interpolate variable references
- run cheap-model prefiltering for natural-language `/FROM` items
- enforce response schema and type rules
- commit variable updates and collect outputs/logs

### Runtime wrapper

Key file:
- `chatdsl_core/runtime_v02.py`

Responsibilities:
- provide an app-facing parse-and-execute entrypoint
- convert parser and executor exceptions into structured results for the UI
- keep the UI layer out of the lower-level execution code

### Model adapters and Gemini client

Key files:
- `chatdsl_core/model_adapters_v02.py`
- `chatdsl_core/gemini_client_v02.py`

Responsibilities:
- adapt runtime calls into the callable shape expected by the executor
- talk to the Gemini HTTP API
- keep API-specific behavior out of parser and executor code

### Persistence and versioning

Key files:
- `chatdsl_core/state_store_v02.py`
- `chatdsl_core/versioning_v02.py`

Responsibilities:
- persist chats and variables to JSON files under `apps/streamlit/state/`
- read legacy state from `v0.4/state/` when the new location is empty
- backfill metadata for older history records
- maintain append-only message/version history
- project visible history for edited DSL runs
- support version inspection and re-execution flows

### Tests

Key directory:
- `tests/`

Responsibilities:
- cover parser behavior
- cover executor validation and runtime semantics
- cover Gemini client and adapter behavior
- cover versioning and app-facing flows

## Data flow

The main DSL execution path is:

```text
User input in Streamlit
-> app chooses DSL mode
-> parser builds a Program AST
-> runtime wrapper catches parse/runtime errors
-> executor walks the program
-> model adapter calls Gemini or a stub path
-> executor returns outputs, vars, and logs
-> app persists chat/version state
-> UI renders messages, variables, and traces
```

The versioned edit path adds another layer:

```text
stored chat history
-> versioning helpers compute visible history and prior context
-> app builds an edit run context
-> parser/executor rerun the edited DSL message
-> app records a new immutable version instead of mutating the old one
```

## Important invariants

- The active system lives in `apps/streamlit/`, `chatdsl_core/`, and `tests/`, while historical version material lives in `archive/` and `v0.4/`.
- Historical version folders are snapshots, not peer active systems.
- The parser is responsible for producing a valid program structure before execution begins.
- `CHAT` and `ALL` are read-only built-in context variables and should not become ordinary mutable user vars.
- DSL edits are append-only history events. Older messages should remain inspectable even when later edits change the projected visible timeline.
- Message metadata such as `id`, `thread_id`, `version`, `run_id`, and edit ancestry must remain coherent across persistence and UI flows.
- Parser and executor contracts should stay cleanly separated from Streamlit-specific UI code.

## External dependencies

- Streamlit for the interactive app
- Gemini HTTP API for live model execution
- standard-library JSON and file persistence for local state
- `pytest` for automated validation

## Things not to change casually

- The append-only versioning model and projected-history logic in `chatdsl_core/versioning_v02.py`
- The persisted JSON shape used by `chatdsl_core/state_store_v02.py`
- The parser-to-executor contract, especially the `Program` and node structures used by `chatdsl_core`
- The persisted JSON shape and fallback behavior used by `chatdsl_core/state_store_v02.py`

## Contribution note

Contributors should optimize first for correctness, documentation, and clear issue-scoped changes within the current structure. Repository reorganization should happen only through explicit follow-up issues.
