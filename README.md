# Chat DSL

Chat DSL is a versioned experimental repository for a chat-oriented domain-specific language, its parser and executor, and a local Streamlit app for running DSL programs.

The active application lives in `apps/streamlit/`, shared runtime code lives in `chatdsl_core/`, and the active test suite lives in `tests/`.

Historical snapshots live under `archive/`. `v0.4/` remains in the repository as historical version-specific reference material and a legacy state fallback location.

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
python -m pytest -q archive/v0.3/tests
```

## Repository layout

- `apps/streamlit/`: active Streamlit app
- `chatdsl_core/`: active shared runtime code
- `tests/`: active test suite
- `v0.4/`: historical version-specific docs and legacy state fallback during the transition
- `docs/`: project-level documentation
- `archive/`: archived `v0.1/`, `v0.2/`, and `v0.3/` snapshots

## Project docs

- Roadmap: `docs/roadmap.md`
- Architecture: `docs/architecture.md`
- Agent and contributor workflow: `AGENTS.md`
- GitHub Issues: `https://github.com/Ambrois/Chat-DSL/issues`

Use GitHub Issues for substantial work. Repo-local notes are not the durable work queue.
