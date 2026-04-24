# Repository Operating Model

This repository uses a lightweight operating model for keeping the project understandable, maintainable, and scalable for both humans and coding agents.

The goal is to keep important project knowledge outside any one person's head. Work should be visible, scoped, prioritized, testable, and recoverable.

This model is intentionally minimal. Each document has one clear purpose. Do not add new document types unless the existing ones fail to answer a distinct question.

---

## Core idea

The project is organized around six main artifacts:

```text
README.md
AGENTS.md
docs/roadmap.md
docs/architecture.md
GitHub Issues
Pull Requests
```

Each one answers a different question:

| Artifact               | Question it answers                                         |
| ---------------------- | ----------------------------------------------------------- |
| `README.md`            | What is this project and how do I use or run it?            |
| `AGENTS.md`            | How should contributors or coding agents work in this repo? |
| `docs/roadmap.md`      | What are we building, and in what order?                    |
| `docs/architecture.md` | How is the system structured?                               |
| GitHub Issues          | What specific work needs to be done?                        |
| Pull Requests          | What changed, why, and how was it validated?                |

The core workflow is:

```text
Roadmap says what matters.
Issue says exactly what to do.
Pull Request records what changed.
README says how to use and run the project.
Architecture docs explain how the system is built.
AGENTS.md explains how contributors and agents should behave.
```

---

# 1. README.md

## Purpose

`README.md` explains what the project is and how to run it.

It is the entry point for a new human contributor, user, or coding agent.

## Include

The README should include:

```text
- project name
- short project description
- installation/setup instructions
- basic usage
- common commands
- links to roadmap, architecture, issues, and agent instructions
```

## Do not include

Do not put these in the README:

```text
- detailed architecture explanations
- long-term task lists
- detailed agent behavior rules
- issue tracking
- implementation plans
- internal decision logs
```

Those belong elsewhere.

## Example structure

```md
# Project Name

Brief description of what this project does.

## Setup

```bash
...
```

## Usage

```bash
...
```

## Common commands

```bash
# Run tests
...

# Run linter
...

# Start development server
...
```

## Project docs

* Roadmap: `docs/roadmap.md`
* Architecture: `docs/architecture.md`
* Agent/contributor rules: `AGENTS.md`

```

---

# 2. AGENTS.md

## Purpose

`AGENTS.md` explains how coding agents and contributors should behave when working in this repository.

It is not a task list. It is not the roadmap. It is not a replacement for documentation.

It defines the work protocol.

## Core rules

The agent or contributor should:

```text
1. Read `README.md` first.
2. Read `AGENTS.md` before modifying files.
3. Use GitHub Issues as the source of durable work.
4. Keep changes tied to a specific issue whenever possible.
5. Do not expand scope silently.
6. Prefer small, reviewable changes.
7. Follow existing patterns before introducing new abstractions.
8. Run relevant validation before finishing.
9. Update docs when setup, behavior, architecture, or commands change.
10. Report what changed, what was tested, and what remains risky or incomplete.
```

## Example AGENTS.md

```md
# AGENTS.md

This file defines how coding agents and contributors should work in this repository.

## Before starting

1. Read `README.md`.
2. Read the relevant parts of `docs/architecture.md`.
3. Identify the GitHub Issue being worked on.
4. If no issue exists, propose or create one before doing substantial work.
5. Check the issue's goal, scope, acceptance criteria, and validation steps.

## Work tracking

Durable work belongs in GitHub Issues.

Do not create hidden private task systems. If new work is discovered, suggest a follow-up issue instead of silently expanding the current task.

## Scope control

Stay within the issue scope.

Do not:
- rewrite unrelated code
- introduce new dependencies without justification
- refactor unrelated areas
- change public behavior unless the issue requires it
- hide unfinished work in vague TODOs

If a useful improvement is outside the current scope, document it as a follow-up issue.

## Implementation rules

- Prefer small, focused changes.
- Match existing style in nearby files.
- Use clear names.
- Avoid premature abstractions.
- Add or update tests for behavior changes.
- Handle errors explicitly.
- Do not commit secrets, credentials, or private data.

## Validation

Before finishing, run the smallest relevant validation command.

Examples:
- unit tests for changed code
- integration tests for changed flows
- lint/typecheck if relevant
- manual test if automated tests do not exist

Report exactly what was run and whether it passed.

## Documentation updates

Update documentation when:
- setup instructions change
- commands change
- public behavior changes
- architecture changes
- important operational knowledge is discovered
- future contributors would otherwise need to rediscover the same information

Do not update docs for purely internal changes unless existing docs become misleading.

## Completion report

Every completed change should include:

- summary of changes
- related issue
- tests or validation run
- docs updated, if any
- risks or limitations
- suggested follow-up work, if any
```

---

# 3. docs/roadmap.md

## Purpose

`docs/roadmap.md` explains what the project is trying to build over time.

It is strategic, not tactical.

It should describe direction and priority, not individual task details.

## Structure

Use four sections:

```text
Now
Next
Later
Not planned
```

## Meaning of each section

| Section     | Meaning                       |
| ----------- | ----------------------------- |
| Now         | Current priorities            |
| Next        | Likely upcoming work          |
| Later       | Possible future work          |
| Not planned | Things intentionally excluded |

The `Not planned` section is important because it prevents scope creep.

## Do not include

Do not put detailed issue checklists in the roadmap.

Bad:

```md
- Add button to page
- Rename function
- Fix typo
- Change parser error message
```

Good:

```md
- Build CSV import flow
- Add transaction categorization
- Improve search and filtering
```

## Example roadmap

```md
# Roadmap

This file describes the project's current direction and priorities.

## Now

- Build the minimum useful version of the core product.
- Stabilize local development setup.
- Add tests for the most important flows.

## Next

- Improve user experience around the main workflow.
- Add persistence for important user data.
- Add better error handling and validation.

## Later

- Add advanced configuration.
- Add plugin or extension support.
- Add deployment automation.

## Not planned

- Mobile app.
- Multi-user support.
- Large infrastructure rewrite.
```

---

# 4. docs/architecture.md

## Purpose

`docs/architecture.md` explains how the system is organized.

It should help a contributor or agent answer:

```text
Where does this feature live?
What are the major components?
How does data move through the system?
What should not be changed casually?
```

## Include

The architecture document should include:

```text
- high-level system overview
- major modules
- important data flow
- important invariants
- external dependencies
- boundaries between components
- things not to change casually
```

## Do not include

Do not put every implementation detail in the architecture document.

Avoid:

```text
- line-by-line explanations
- duplicated source code comments
- temporary task notes
- issue checklists
- stale implementation plans
```

## Example architecture document

```md
# Architecture

This document explains the structure of the project.

## System overview

Briefly describe what the system does and how the major pieces fit together.

## Major components

### Component A

Purpose:

Key files:

Responsibilities:

### Component B

Purpose:

Key files:

Responsibilities:

## Data flow

Describe the main flow of data through the system.

Example:

```text
Input → Parser → Validator → Storage → API → UI
```

## Important invariants

These are assumptions that should remain true unless there is a deliberate architecture change.

* ...
* ...
* ...

## External dependencies

List important external systems, libraries, APIs, or services.

## Things not to change casually

* ...
* ...
* ...

```

---

# 5. GitHub Issues

## Purpose

GitHub Issues are the durable work queue.

Every real task, bug, feature, or refactor should be represented as an issue.

Issues are where work becomes specific.

## Why issues matter

Issues prevent work from remaining vague.

A good issue defines:

```text
- what should be true when the work is done
- what is in scope
- what is out of scope
- how to check that the work worked
```

## Good issue size

An issue should usually be small enough to complete in one focused work session or one small pull request.

Bad issue:

```text
Build the whole dashboard.
```

Better issues:

```text
Create transaction database schema.
Implement CSV parser.
Add transaction table UI.
Add tests for malformed CSV rows.
```

## Required issue structure

Each issue should include:

```md
# Goal

What should be true when this issue is done?

# Scope

What is included in this issue?

# Out of scope

What should not be changed as part of this issue?

# Acceptance criteria

- [ ] Specific observable requirement
- [ ] Specific observable requirement
- [ ] Specific observable requirement

# Validation

How should this be tested or checked?
```

## Example issue

```md
# Parse Chase CSV transactions

## Goal

Convert Chase CSV export rows into normalized transaction objects.

## Scope

- Support Chase checking-account CSV exports.
- Parse date, description, amount, and balance.
- Return structured transaction objects.
- Add parser tests.

## Out of scope

- Support for other banks.
- Duplicate detection.
- Database insertion.
- UI upload flow.

## Acceptance criteria

- [ ] Valid Chase CSV rows parse correctly.
- [ ] Missing required columns produce clear errors.
- [ ] Malformed rows are rejected.
- [ ] Parser tests cover normal and invalid input.
- [ ] Parser does not depend on the UI.

## Validation

Run:

```bash
pytest tests/test_chase_csv_parser.py
```

```

## Issue states

Use a simple workflow:

```text
Backlog
Ready
In Progress
Review / Testing
Done
```

Meanings:

| State            | Meaning                           |
| ---------------- | --------------------------------- |
| Backlog          | Captured idea, not yet clarified  |
| Ready            | Clear enough to work on           |
| In Progress      | Currently being worked on         |
| Review / Testing | Implemented but not fully checked |
| Done             | Completed and validated           |

For solo or agent-assisted work, keep at most one or two issues in progress at a time.

---

# 6. Pull Requests

## Purpose

Pull Requests record actual changes.

A PR should connect an issue to the code change that resolves it.

The ideal flow is:

```text
Issue describes desired work.
Branch implements it.
Pull Request explains what changed.
Tests prove it works.
Issue gets closed.
```

## PR should include

Every PR should answer:

```text
- What changed?
- What issue does this close?
- How was it validated?
- What risks remain?
- Were docs updated?
```

## Example PR template

```md
# Summary

Briefly describe what changed.

# Related issue

Closes #

# Changes

- ...
- ...
- ...

# Validation

Commands run:

```bash
...
```

Results:

```text
...
```

# Documentation

* [ ] Docs updated
* [ ] Docs not needed

# Risks / limitations

Describe anything that might still be fragile, incomplete, or risky.

# Follow-up work

List any work intentionally left for later.

```

---

# 7. Standard workflow

Use this workflow for all nontrivial work:

```text
Capture → Clarify → Prioritize → Decompose → Execute → Validate → Document
```

## 1. Capture

Write down the idea, bug, feature, or improvement.

At this stage, it can be rough.

Example:

```text
Maybe add duplicate transaction detection.
```

## 2. Clarify

Turn the rough idea into a real issue.

Example:

```text
Detect duplicate imported transactions using date, amount, and description.
```

## 3. Prioritize

Decide whether this belongs in:

```text
Now
Next
Later
Not planned
```

Only `Now` items should actively drive work.

## 4. Decompose

Break large work into smaller issues.

Bad:

```text
Build import system.
```

Better:

```text
- Define transaction schema.
- Parse Chase CSV files.
- Store imported transactions.
- Show import preview.
- Add duplicate detection.
```

## 5. Execute

Work on one issue at a time.

Stay within scope.

## 6. Validate

Run the validation steps from the issue.

If validation is missing, add a reasonable one.

## 7. Document

Update docs only when durable knowledge changes.

Examples:

```text
- README if setup or usage changes.
- architecture.md if system structure changes.
- roadmap.md if priorities change.
- AGENTS.md if contributor/agent workflow changes.
```

---

# 8. Scope discipline

Scope discipline is the main difference between small-project habits and scalable-project habits.

## Rule

Do not silently expand the task.

If new work appears, classify it:

```text
Required for current issue → do it.
Useful but separate → create follow-up issue.
Unclear → note it as an open question.
Not needed → ignore it.
```

## Example

Current issue:

```text
Parse Chase CSV transactions.
```

During work, you notice duplicate detection would be useful.

Do not implement duplicate detection inside the parser issue unless it is required by the acceptance criteria.

Instead, create a follow-up issue:

```text
Detect duplicate transactions during CSV import.
```

This keeps each change understandable.

---

# 9. Acceptance criteria

Acceptance criteria define what “done” means.

They should be observable.

Bad acceptance criteria:

```text
- Make import better.
- Clean up parser.
- Improve UI.
```

Good acceptance criteria:

```text
- Valid CSV rows produce transaction objects.
- Missing required columns produce a clear error.
- Parser tests cover valid and invalid files.
- UI displays an error message when upload fails.
```

Use this pattern when helpful:

```text
Given some situation,
when some action happens,
then some result should occur.
```

Example:

```text
Given a valid Chase CSV file,
when the parser runs,
then it returns one transaction object per row.
```

---

# 10. Documentation update rules

Update documentation when the change affects future understanding.

## Update README.md when

```text
- setup changes
- install commands change
- usage changes
- common commands change
- project purpose changes
```

## Update docs/architecture.md when

```text
- major modules change
- data flow changes
- storage model changes
- public interfaces change
- important dependencies change
- important invariants change
```

## Update docs/roadmap.md when

```text
- priorities change
- major planned work changes
- something moves from Later to Next or Next to Now
- something is explicitly rejected as Not planned
```

## Update AGENTS.md when

```text
- contributor workflow changes
- agent workflow changes
- repeated agent mistakes reveal a missing rule
- validation expectations change
- documentation expectations change
```

## Do not update docs when

```text
- the change is purely internal and obvious from the code
- the note is temporary
- the information belongs in an issue or PR instead
- the update would duplicate another document
```

---

# 11. When to add more structure

Start with the minimal model.

Do not add extra docs or process until there is real pain.

## Add `docs/testing.md` only if

```text
- test commands become complicated
- different parts of the project need different test procedures
- agents repeatedly run the wrong tests
```

## Add `docs/style.md` only if

```text
- style decisions are repeatedly inconsistent
- formatting/linting is not enough
- contributors need project-specific conventions
```

## Add `docs/features/` only if

```text
- a feature spans many issues
- the feature design is too large to fit in one issue
- multiple contributors need shared context
```

## Add `docs/decisions/` only if

```text
- architecture decisions need historical explanation
- people keep relitigating the same choices
- future contributors need to know why a choice was made
```

## Add milestones or epics only if

```text
- there are too many issues to understand flatly
- multiple issues together produce one meaningful release or capability
```

## Add labels only if

```text
- issue count becomes hard to scan
- filtering by area, priority, or status becomes useful
```

---

# 12. Anti-patterns

Avoid these.

## Giant README

The README becomes unusable if it tries to contain everything.

Keep it focused on project purpose, setup, and usage.

## Giant AGENTS.md

`AGENTS.md` should explain how to work, not contain all project knowledge.

If it gets too long, move durable knowledge into README, roadmap, architecture docs, or issues.

## Vague issues

Bad:

```text
Improve backend.
```

Better:

```text
Add validation for missing transaction dates in CSV parser.
```

## Hidden TODOs

Do not hide durable work inside code comments.

Bad:

```python
# TODO: add real auth later
```

Better:

```text
Create an issue: Add authentication middleware.
```

Small local TODOs are acceptable only when they are directly tied to the current change.

## Scope creep

Do not turn one issue into a large unplanned refactor.

## Duplicate sources of truth

Do not track the same thing in multiple places.

Examples:

```text
Bad:
- roadmap has detailed task checklist
- issues have the same checklist
- AGENTS.md has another copy

Good:
- roadmap has priority
- issue has task detail
- PR records implementation
```

---

# 13. Summary

This repository operating model separates project knowledge into distinct layers:

```text
README.md
Explains what the project is and how to run it.

AGENTS.md
Explains how contributors and agents should work.

docs/roadmap.md
Explains what is being built and in what order.

docs/architecture.md
Explains how the system is organized.

GitHub Issues
Define specific units of work.

Pull Requests
Record completed changes and validation.
```

The main rule is:

```text
Do not create a new document type unless it answers a different question than the existing documents.
```

The main workflow is:

```text
Capture → Clarify → Prioritize → Decompose → Execute → Validate → Document
```

The main discipline is:

```text
One issue at a time.
Clear scope.
Observable acceptance criteria.
Validation before completion.
Documentation only when durable knowledge changes.
```


