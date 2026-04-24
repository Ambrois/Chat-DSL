# Chat DSL v0.4

This folder is the `v0.4` historical reference work area during Phase 2.

`v0.4` is the first block-structured control-flow release. During Phase 2, the active app and shared runtime modules have moved out to `apps/streamlit/` and `chatdsl_core/`, while `v0.4/` still contains:

- version-specific documentation and reference material
- legacy local state under `v0.4/state/` that can still be read during the transition

Current goals:

- introduce a real AST instead of a flat `List[Step]`
- support `/IF <sigil>bool_var ... /END`
- allow nested `/IF` blocks
- execute the program recursively rather than as a flat loop
- record execution traces for entered, skipped, and executed nodes

Important semantic choice for `v0.4`:

- variables defined inside an `/IF` block are branch-local
- they are not visible after `/END`
- `/ELSE` is intentionally deferred to a later version

Primary docs:

- `spec_changes_from_last.md`: v0.4 deltas from v0.3
- `dsl_v0.4_specs.md`: v0.4 draft spec sheet
- `interface_spec_v0.4.md`: current Streamlit UI behavior for the v0.4 app

Implementation note:

- the active app now lives in `apps/streamlit/`
- active shared runtime code now lives in `chatdsl_core/`
- the active tests now live in `tests/`
- temporary compatibility modules have been removed
- later commits may remove the legacy `v0.4/state/` fallback once migration concerns are settled

Open issues:

- tracked in GitHub Issues: `https://github.com/Ambrois/Chat-DSL/issues`

Run tests:

```bash
python -m pytest -q tests
```
