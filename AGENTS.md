# AGENTS.md

This file defines how contributors and coding agents should work in this repository.

## Before starting

1. Read `README.md`.
2. Read the relevant parts of `docs/architecture.md`.
3. Identify the GitHub Issue for the work.
4. If no GitHub Issue exists and the work is substantial, create or request one before changing code or durable docs.
5. Confirm the issue's goal, scope, acceptance criteria, and validation steps before implementation.

## Work tracking

GitHub Issues are the durable work queue for this repository.

Do not use ad hoc in-repo task lists, private notes, or branch names as the primary record of planned work. If new work is discovered during implementation, capture it as a follow-up issue instead of silently expanding scope.

Substantial work must always map to a GitHub Issue.

## Repo guidance

- `apps/streamlit/` is the active home for the Streamlit app.
- `chatdsl_core/` is the active home for shared parser, executor, runtime, model-integration, persistence, and versioning code.
- `tests/` is the active home for the current test suite.
- `v0.4/` now holds historical version-specific docs and legacy state fallback only. Do not target it for active product work unless an issue explicitly requires it.
- `archive/v0.1/`, `archive/v0.2/`, and `archive/v0.3/` are historical version snapshots unless a GitHub Issue explicitly says otherwise.
- Treat version-specific spec and README files as supporting documentation, not as replacements for the top-level `README.md`, roadmap, architecture docs, or GitHub Issues.
- Follow existing patterns in the active path you are changing before introducing new abstractions or reorganizing code.

## Scope control

Stay within the scope of the current issue.

Do not:
- rewrite unrelated code
- refactor unrelated areas
- introduce new dependencies without justification
- change public behavior unless the issue requires it
- leave behind vague TODOs as a substitute for tracking follow-up work

If useful follow-up work is discovered, capture it in GitHub Issues.

## Implementation rules

- Prefer small, reviewable changes.
- Match the style and structure of nearby code unless the issue calls for a deliberate pattern change.
- Keep durable project knowledge in the designated docs, not in commit messages or ephemeral notes.
- Add or update tests for behavior changes.
- Handle errors explicitly.
- Do not commit secrets, credentials, or private data.

## Validation

Before finishing, run the smallest relevant validation for the files you changed.

Examples:
- targeted unit tests
- integration tests for affected flows
- lint or type checks when relevant
- manual validation when automated coverage does not exist

Report exactly what you ran and whether it passed.

## Documentation updates

Update documentation when:
- setup or run instructions change
- commands change
- public behavior changes
- architecture changes
- roadmap priorities change
- important operational knowledge is discovered

Do not create new standing document types unless the existing operating model artifacts are insufficient.

## Completion report

Every completed change should report:

- summary of changes
- related GitHub Issue
- validation run
- docs updated, if any
- remaining risks or limitations
- suggested follow-up work, if any
