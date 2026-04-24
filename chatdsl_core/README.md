# chatdsl_core

Active shared runtime code for Chat DSL.

This directory now contains the active:

- parser
- executor
- runtime wrapper
- model adapters and Gemini client
- persistence and versioning helpers

Phase 2 status:

- moved here under issue `#8`
- the active Streamlit app now lives in `apps/streamlit/`
- the active tests now live in `tests/`
- active state now writes to `apps/streamlit/state/` with legacy fallback from `v0.4/state/`
