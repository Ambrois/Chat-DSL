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
- `v0.4/` still exposes thin compatibility wrappers until later cleanup issues remove them
- the active Streamlit app remains in `v0.4/` until issue `#9`
- the active tests remain in `v0.4/tests/` until issue `#10`
