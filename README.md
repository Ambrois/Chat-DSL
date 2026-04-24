# Chat DSL

Chat DSL is a versioned experimental repository for a chat-oriented domain-specific language, its parser and executor, and a local Streamlit app for running DSL programs.

The active implementation line is `v0.4/`. Earlier `v0.x/` directories remain in the repository as historical snapshots.

Phase 2 migration target:

- active app code will move to `apps/streamlit/`
- active core code will move to `chatdsl_core/`
- active tests will move to `tests/`
- historical snapshots will move to `archive/`

Until that migration is complete, the active runtime still lives under `v0.4/`.

## Setup

This repository is not packaged yet. The active app and tests run directly from the versioned source tree.

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

- `v0.4/`: active app, runtime, parser, executor, versioning, persistence, and tests until Phase 2 finishes
- `v0.1/`, `v0.2/`, `v0.3/`: historical version snapshots
- `docs/`: project-level documentation
- `apps/`, `chatdsl_core/`, `tests/`, `archive/`: agreed Phase 2 destination layout for the active app, active core, active tests, and historical snapshots

## Project docs

- Roadmap: `docs/roadmap.md`
- Architecture: `docs/architecture.md`
- Agent and contributor workflow: `AGENTS.md`
- GitHub Issues: `https://github.com/Ambrois/Chat-DSL/issues`

Use GitHub Issues for substantial work. Repo-local notes are not the durable work queue.
