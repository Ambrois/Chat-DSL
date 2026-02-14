"""Run with: streamlit run v0.2/app.py"""

from __future__ import annotations

import os
from datetime import datetime
from typing import Any, Dict, List

import streamlit as st

from model_adapters_v02 import make_gemini_caller
from runtime_v02 import RunResult, run_dsl_text


def _init_state() -> None:
    st.session_state.setdefault("v02_vars", {})
    st.session_state.setdefault("v02_runs", [])


def _append_run(input_text: str, mode: str, result: RunResult) -> None:
    st.session_state["v02_runs"].append(
        {
            "ts": datetime.utcnow().isoformat(timespec="seconds"),
            "input": input_text,
            "mode": mode,
            "ok": result.ok,
            "outputs": result.outputs,
            "error": result.error,
            "parsed_steps": result.parsed_steps,
            "logs": result.logs,
            "vars_after": result.vars_after,
        }
    )


def _render_result(result: RunResult) -> None:
    if result.ok:
        st.success("Run completed")
    else:
        st.error(result.error or "Unknown error")

    st.subheader("Outputs")
    if result.outputs:
        for idx, out in enumerate(result.outputs, start=1):
            st.markdown(f"**Step output {idx}:**")
            st.write(out)
    else:
        st.caption("No visible outputs.")

    st.subheader("Variables")
    if result.vars_after:
        st.json(result.vars_after)
    else:
        st.caption("No variables.")

    with st.expander("Parsed Steps", expanded=False):
        st.json(result.parsed_steps)
    with st.expander("Execution Logs", expanded=False):
        st.json(result.logs)


def _render_history(runs: List[Dict[str, Any]]) -> None:
    st.subheader("Run History")
    if not runs:
        st.caption("No runs yet.")
        return
    for i, run in enumerate(reversed(runs), start=1):
        label = f"{i}. {run['ts']} ({run['mode']}) {'OK' if run['ok'] else 'ERROR'}"
        with st.expander(label, expanded=False):
            st.markdown("**Input**")
            st.code(run["input"])
            if run["ok"]:
                st.markdown("**Outputs**")
                st.json(run["outputs"])
            else:
                st.markdown("**Error**")
                st.write(run["error"])
            st.markdown("**Vars After**")
            st.json(run["vars_after"])


def main() -> None:
    st.set_page_config(page_title="Chat DSL v0.2", layout="wide")
    _init_state()

    st.title("Chat DSL v0.2")
    st.caption("Parser + executor playground for the v0.2 command spec.")

    with st.sidebar:
        st.header("Executor")
        mode = st.radio("Mode", ["Stub", "Gemini"], index=0)

        model = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
        timeout_s = 120.0
        if mode == "Gemini":
            model = st.text_input("Model", value=model)
            timeout_s = float(
                st.number_input(
                    "Timeout (seconds)",
                    min_value=0,
                    max_value=600,
                    value=120,
                    step=10,
                )
            )
            st.info(
                "Gemini responses must follow the v0.2 JSON contract: "
                '{"error":0|1,"out":"...","vars":{...}}.'
            )

        st.divider()
        if st.button("Clear Variables", use_container_width=True):
            st.session_state["v02_vars"] = {}
        if st.button("Clear History", use_container_width=True):
            st.session_state["v02_runs"] = []

    default_text = (
        "Choose a topic\n"
        "/DEF topic /TYPE str\n"
        "/THEN Draft a concise summary for @topic\n"
        "/FROM @topic\n"
        "/DEF summary /TYPE str /AS concise summary of @topic\n"
        "/OUT readable output"
    )
    dsl_text = st.text_area(
        "DSL Input",
        value=default_text,
        height=260,
        help="Use /THEN for additional steps. Indented commands are allowed.",
    )

    run_clicked = st.button("Run DSL", type="primary")
    if run_clicked:
        call_model = None
        run_mode = "stub"
        if mode == "Gemini":
            call_model = make_gemini_caller(model=model, timeout_s=timeout_s)
            run_mode = "gemini"

        result = run_dsl_text(
            dsl_text,
            context=st.session_state["v02_vars"],
            call_model=call_model,
        )
        _append_run(dsl_text, run_mode, result)
        if result.ok:
            st.session_state["v02_vars"] = result.vars_after
        _render_result(result)
    elif st.session_state["v02_runs"]:
        last = st.session_state["v02_runs"][-1]
        _render_result(
            RunResult(
                ok=last["ok"],
                outputs=last["outputs"],
                logs=last["logs"],
                vars_after=last["vars_after"],
                parsed_steps=last["parsed_steps"],
                error=last["error"],
            )
        )

    st.divider()
    _render_history(st.session_state["v02_runs"])


if __name__ == "__main__":
    main()
