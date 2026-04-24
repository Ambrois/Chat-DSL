# Chat DSL v0.4

This folder is the `v0.4` historical reference work area.

`v0.4` is the first block-structured control-flow release. The active app and shared runtime modules now live in `apps/streamlit/` and `chatdsl_core/`, while `v0.4/` contains:

- version-specific documentation and reference material
- legacy local state under `v0.4/state/` that can still be read as fallback

Historical focus:

- introduced a real AST instead of a flat `List[Step]`
- added `/IF <sigil>bool_var ... /END`
- allowed nested `/IF` blocks
- executed the program recursively rather than as a flat loop
- recorded execution traces for entered, skipped, and executed nodes

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

Open issues:

- tracked in GitHub Issues: `https://github.com/Ambrois/Chat-DSL/issues`

Run tests:

```bash
python -m pytest -q tests
```
