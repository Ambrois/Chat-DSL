# Chat DSL

Chat DSL is a versioned experimental repository for a chat-oriented domain-specific language, its parser and executor, and a local Streamlit app for running DSL programs.

The active implementation line is in transition during Phase 2. Shared runtime code now lives in `chatdsl_core/`, while the active Streamlit app and active tests still run from `v0.4/`.

Earlier `v0.x/` directories remain in the repository as historical snapshots.

Phase 2 migration status:

- active shared runtime code has moved to `chatdsl_core/`
- the active app will move to `apps/streamlit/` under issue `#9`
- the active tests will move to `tests/` under issue `#10`
- historical snapshots will move to `archive/` under issue `#11`

Until those follow-up issues land, the active app and test entrypoints still live under `v0.4/`.

## Setup

This repository is not packaged yet. The active app and tests still run directly from the `v0.4/` tree, while shared runtime code lives in `chatdsl_core/`.

Recommended local setup:

```bash
python -m venv .venv
source .venv/bin/activate
pip install streamlit pytest
```

Optional environment variables for Gemini-backed execution:

```bash
export GEMINI_API_KEY=...
export GEMINI_MODEL=gemini-2.5-flash
export GEMINI_CHEAP_MODEL=gemini-3-flash-preview
export GEMINI_TIMEOUT=120
```

`GEMINI_API_KEY` is only required when running live Gemini calls. The app can still be used in stub mode without it.

## Usage

Run the active app:

```bash
streamlit run v0.4/app.py
```

The `v0.4` app supports:

- DSL execution through the `v0.4` parser and executor
- local chat persistence
- versioned edits for DSL messages
- stub execution and Gemini-backed execution modes

## Common commands

Run the active test suite:

```bash
python -m pytest -q v0.4/tests
```

Run the previous stable line's tests when comparing behavior:

```bash
python -m pytest -q v0.3/tests
```

## Repository layout

- `chatdsl_core/`: active shared runtime code
- `v0.4/`: active Streamlit app, app-specific helpers, active tests, version-specific docs, and temporary compatibility wrappers during Phase 2
- `v0.1/`, `v0.2/`, `v0.3/`: historical version snapshots
- `docs/`: project-level documentation
- `apps/streamlit/`: scaffolded destination for the active app
- `tests/`: scaffolded destination for the active test suite
- `archive/`: scaffolded destination for historical snapshots

## Project docs

- Roadmap: `docs/roadmap.md`
- Architecture: `docs/architecture.md`
- Agent and contributor workflow: `AGENTS.md`
- GitHub Issues: `https://github.com/Ambrois/Chat-DSL/issues`

Use GitHub Issues for substantial work. Repo-local notes are not the durable work queue.
