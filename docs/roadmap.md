# Roadmap

This document describes the current direction and priorities for Chat DSL.

Detailed work belongs in GitHub Issues. This roadmap stays strategic.

## Now

- Adopt the repository operating model so work is tracked through GitHub Issues, documented clearly, and validated consistently.
- Treat `v0.4/` as the active implementation line and improve its documentation, usability, and runtime reliability.
- Prepare for a structured Phase 2 repository cleanup that separates active code from historical version snapshots without disrupting current development.

## Next

- Reorganize the repository around a clearer active-code layout for the app and shared runtime components.
- Define the long-term place of historical version folders so snapshots remain useful without obscuring the active system.
- Continue hardening `v0.4` behavior around execution flow, versioned chat state, and user-facing reliability.

## Later

- Expand the language and runtime after the `v0.4` foundations and repo structure are stable.
- Improve packaging and interface boundaries so the core DSL runtime can support more than one frontend cleanly.
- Strengthen automated validation and release discipline as the project grows.

## Not planned

- Treat every historical `v0.x/` snapshot as an equally active product line.
- Large unscoped rewrites that bypass issues, validation, or architecture review.
- Major platform expansion before the active `v0.4` line and repository structure are stable.
