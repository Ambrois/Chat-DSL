# Chat DSL v0.4

This folder is the `v0.4` work area.

`v0.4` is the first block-structured control-flow release. The implementation is being
built in small, testable commits on top of the stable `v0.3` snapshot.

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

- code filenames still use the existing `*_v02.py` naming for continuity during the refactor
- later commits may rename modules once the new architecture is stable

Known issues:

- see `known_issues.md` for currently tracked `v0.4` UI/runtime issues

Run tests:

```bash
PYTHONPATH=/data/data/com.termux/files/home/projects/Chat-DSL/.vendor python -m pytest -q v0.4/tests
```
