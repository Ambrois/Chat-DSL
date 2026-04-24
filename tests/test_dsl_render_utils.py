from __future__ import annotations

from apps.streamlit.dsl_render_utils import dsl_to_highlighted_html, infer_message_sigil

def test_dsl_to_highlighted_html_marks_commands_and_custom_sigil_refs() -> None:
    html = dsl_to_highlighted_html("/IF #ok\n/THEN Use #notes\n/END", sigil="#")

    assert '<span class="dsl-kw">/IF</span>' in html
    assert '<span class="dsl-kw">/THEN</span>' in html
    assert '<span class="dsl-kw">/END</span>' in html
    assert '<span class="dsl-var">#ok</span>' in html
    assert '<span class="dsl-var">#notes</span>' in html

def test_dsl_to_highlighted_html_preserves_email_like_text() -> None:
    html = dsl_to_highlighted_html("Send note to a@b.com")

    assert "a@b.com" in html
    assert 'class="dsl-var"' not in html

def test_infer_message_sigil_reads_parsed_steps_metadata() -> None:
    sigil = infer_message_sigil({"meta": {"parsed_steps": [{"sigil": "#"}]}})

    assert sigil == "#"

def test_infer_message_sigil_falls_back_to_default() -> None:
    sigil = infer_message_sigil({"meta": {}}, default="$")

    assert sigil == "$"
