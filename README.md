# Chat DSL

Chat DSL is a versioned experimental repository for a chat-oriented domain-specific language, its parser and executor, and a local Streamlit app for running DSL programs.

The active implementation line is in transition during Phase 2. Shared runtime code now lives in `chatdsl_core/`, the active Streamlit app now lives in `apps/streamlit/`, and the active tests now live in `tests/`.

Earlier `v0.x/` directories remain in the repository as historical snapshots.

Phase 2 migration status:

- active shared runtime code has moved to `chatdsl_core/`
- the active app has moved to `apps/streamlit/`
- the active tests have moved to `tests/`
- historical snapshots will move to `archive/` under issue `#11`

Until those follow-up issues land, `v0.4/` retains temporary compatibility wrappers and historical version-specific docs.

## Setup

This repository is not packaged yet. The active app runs from `apps/streamlit/`, the active tests run from `tests/`, and shared runtime code lives in `chatdsl_core/`.

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
streamlit run apps/streamlit/app.py
```

The `v0.4` app supports:

- DSL execution through the `v0.4` parser and executor
- local chat persistence
- versioned edits for DSL messages
- stub execution and Gemini-backed execution modes

## Common commands

Run the active test suite:

```bash
python -m pytest -q tests
```

Run the previous stable line's tests when comparing behavior:

```bash
python -m pytest -q v0.3/tests
```

## Repository layout

- `apps/streamlit/`: active Streamlit app
- `chatdsl_core/`: active shared runtime code
- `tests/`: active test suite
- `v0.4/`: version-specific docs and temporary compatibility wrappers during Phase 2
- `v0.1/`, `v0.2/`, `v0.3/`: historical version snapshots
- `docs/`: project-level documentation
- `archive/`: scaffolded destination for historical snapshots

## Project docs

- Roadmap: `docs/roadmap.md`
- Architecture: `docs/architecture.md`
- Agent and contributor workflow: `AGENTS.md`
- GitHub Issues: `https://github.com/Ambrois/Chat-DSL/issues`

Use GitHub Issues for substantial work. Repo-local notes are not the durable work queue.
