# Architecture

This document explains how Chat DSL is organized today.

It describes the current repository structure, the active runtime path, and the boundaries that should not be changed casually while the repository is still in its versioned-layout phase.

## System overview

Chat DSL is a local, versioned DSL experimentation repository centered on a Streamlit app and a small execution stack:

```text
DSL text -> parser -> program AST -> executor -> model adapter/client -> outputs and vars -> persisted chat state -> Streamlit UI
```

The active system is temporarily split during Phase 2:

- `apps/streamlit/` is now the active home of the Streamlit app
- `chatdsl_core/` is now the active home of shared runtime code
- `tests/` is now the active home of the current test suite
- `v0.4/` now contains temporary compatibility wrappers and version-specific docs until later migration issues land

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

### Historical compatibility shell

- `v0.4/`: historical compatibility wrappers, version docs, and persisted state retained at the repo root until final cleanup

Each version directory is largely self-contained. This makes history easy to inspect, but it also means the active architecture is still mixed with archival material.

### Transitional directories

- `docs/`: project-level docs such as roadmap, architecture, and operating model

## Phase 2 target layout

The agreed target layout for the active system is:

```text
README.md
AGENTS.md
docs/
apps/streamlit/
chatdsl_core/
tests/
archive/
```

Meaning:

- `apps/streamlit/` becomes the active home of the Streamlit UI
- `chatdsl_core/` is the active home of shared Python runtime code
- `tests/` is the active home of the unversioned test suite
- `archive/` is the home of historical version snapshots

## Phase 2 migration rules

- Phase 2 is a repository-structure migration, not a product-feature phase.
- Packaging work is out of scope for Phase 2.
- `chatdsl_core/` is already the active home of shared runtime code.
- `apps/streamlit/` is already the active home of the Streamlit app.
- `tests/` is already the active home of the current test suite.
- `archive/` already contains `v0.1/`, `v0.2/`, and `v0.3/`.
- `v0.4/` remains the compatibility layer and version-doc home until the migration issues move or remove those pieces.
- `v0.4/` should no longer be presented as an active implementation home.
- Major moves should stay separated by issue: layout scaffolding, core move, app move, test move, archive move, and final cleanup.
- Compatibility shims, if introduced at all, must be minimal and short-lived.
- Commands and docs should be updated as each migration step lands so the active path remains clear.
- Active validation should continue to run after each major move.

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
- persist chats and variables to JSON files under `v0.4/state/`
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

- The active system is temporarily split during Phase 2: app in `apps/streamlit/`, shared runtime code in `chatdsl_core/`, active tests in `tests/`, and compatibility wrappers still in `v0.4/`.
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
- The temporary compatibility wrappers under `v0.4/`, which should stay thin until later cleanup issues remove them

## Transitional note

The repository is intentionally not yet fully reduced to the final active layout. `apps/streamlit/`, `chatdsl_core/`, and `tests/` are already the active homes of the app, shared runtime, and test suite, while `archive/` now holds the older snapshots and `v0.4/` remains as the final historical compatibility shell still at the repo root.

That means contributors should optimize first for correctness, documentation, and clear issue-scoped changes within the current structure. Repository reorganization should happen only through explicit follow-up issues.
