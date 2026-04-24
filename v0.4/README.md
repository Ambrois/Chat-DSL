# Chat DSL v0.4

This folder is the `v0.4` app and test work area during Phase 2.

`v0.4` is the first block-structured control-flow release. During Phase 2, the active shared runtime modules have moved to `chatdsl_core/`, while `v0.4/` still contains:

- the active Streamlit app entrypoint
- app-specific helpers such as `dsl_render_utils.py`
- the active `v0.4` test suite
- temporary compatibility wrapper modules that preserve the old import paths until later cleanup issues land

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

- active shared runtime code now lives in `chatdsl_core/`
- local `*_v02.py` compatibility modules in `v0.4/` are temporary Phase 2 shims
- later commits will move the active app and tests out of `v0.4/` as well

Open issues:

- tracked in GitHub Issues: `https://github.com/Ambrois/Chat-DSL/issues`

Run tests:

```bash
python -m pytest -q v0.4/tests
```
