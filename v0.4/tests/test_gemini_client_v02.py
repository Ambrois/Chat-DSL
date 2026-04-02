from __future__ import annotations

import io
import json
import sys
import urllib.error
from pathlib import Path

import pytest


V02_DIR = Path(__file__).resolve().parents[1]
if str(V02_DIR) not in sys.path:
    sys.path.insert(0, str(V02_DIR))

import gemini_client_v02


class FakeResp(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


def _json_response(payload: dict) -> FakeResp:
    return FakeResp(json.dumps(payload).encode("utf-8"))


def test_call_gemini_requests_json_mime_type(monkeypatch) -> None:
    captured: dict = {}

    def fake_urlopen(req, timeout=None):
        captured["url"] = req.full_url
        captured["timeout"] = timeout
        captured["payload"] = json.loads(req.data.decode("utf-8"))
        response_data = {
            "candidates": [
                {"content": {"parts": [{"text": '{"error":0,"out":"ok"}'}]}}
            ]
        }
        return FakeResp(json.dumps(response_data).encode("utf-8"))

    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setattr(gemini_client_v02.urllib.request, "urlopen", fake_urlopen)

    schema = {
        "type": "object",
        "properties": {"error": {"type": "integer"}, "out": {"type": "string"}},
        "required": ["error", "out"],
    }
    out = gemini_client_v02.call_gemini(
        "hello", model="gemini-2.5-flash", timeout_s=7, response_schema=schema
    )
    assert out == '{"error":0,"out":"ok"}'
    assert captured["payload"]["generationConfig"]["responseMimeType"] == "application/json"
    assert captured["payload"]["generationConfig"]["responseSchema"] == schema


def test_call_gemini_uses_default_timeout_from_env(monkeypatch) -> None:
    captured: dict = {}

    def fake_urlopen(req, timeout=None):
        captured["timeout"] = timeout
        return _json_response({"candidates": [{"content": {"parts": [{"text": "ok"}]}}]})

    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setenv("GEMINI_TIMEOUT", "15.5")
    monkeypatch.setattr(gemini_client_v02.urllib.request, "urlopen", fake_urlopen)

    out = gemini_client_v02.call_gemini("hello", model="gemini-2.5-flash")

    assert out == "ok"
    assert captured["timeout"] == 15.5


def test_call_gemini_uses_no_timeout_for_nonpositive_value(monkeypatch) -> None:
    captured: dict = {}

    def fake_urlopen(req, timeout=None):
        captured["timeout"] = timeout
        return _json_response({"candidates": [{"content": {"parts": [{"text": "ok"}]}}]})

    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setattr(gemini_client_v02.urllib.request, "urlopen", fake_urlopen)

    out = gemini_client_v02.call_gemini("hello", timeout_s=0)

    assert out == "ok"
    assert captured["timeout"] is None


def test_call_gemini_retries_503_then_succeeds(monkeypatch) -> None:
    attempts: list[int] = []
    sleeps: list[float] = []

    def fake_urlopen(req, timeout=None):
        attempts.append(1)
        if len(attempts) < 3:
            raise urllib.error.HTTPError(
                req.full_url,
                503,
                "busy",
                hdrs=None,
                fp=io.BytesIO(b"retry later"),
            )
        return _json_response({"candidates": [{"content": {"parts": [{"text": "ok"}]}}]})

    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setattr(gemini_client_v02.urllib.request, "urlopen", fake_urlopen)
    monkeypatch.setattr(gemini_client_v02.random, "random", lambda: 0.0)
    monkeypatch.setattr(gemini_client_v02.time, "sleep", sleeps.append)

    out = gemini_client_v02.call_gemini("hello")

    assert out == "ok"
    assert len(attempts) == 3
    assert sleeps == [1.0, 2.0]


def test_call_gemini_raises_http_error_for_non_retryable_status(monkeypatch) -> None:
    def fake_urlopen(req, timeout=None):
        raise urllib.error.HTTPError(
            req.full_url,
            400,
            "bad request",
            hdrs=None,
            fp=io.BytesIO(b'{"error":"bad input"}'),
        )

    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setattr(gemini_client_v02.urllib.request, "urlopen", fake_urlopen)

    with pytest.raises(RuntimeError, match='Gemini HTTP error 400: \\{"error":"bad input"\\}'):
        gemini_client_v02.call_gemini("hello")


def test_call_gemini_raises_connection_error(monkeypatch) -> None:
    def fake_urlopen(req, timeout=None):
        raise urllib.error.URLError("timed out")

    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setattr(gemini_client_v02.urllib.request, "urlopen", fake_urlopen)

    with pytest.raises(RuntimeError, match="Gemini connection error:"):
        gemini_client_v02.call_gemini("hello")


def test_call_gemini_raises_api_error_from_response_payload(monkeypatch) -> None:
    def fake_urlopen(req, timeout=None):
        return _json_response({"error": {"message": "bad request"}})

    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setattr(gemini_client_v02.urllib.request, "urlopen", fake_urlopen)

    with pytest.raises(RuntimeError, match="Gemini API error:"):
        gemini_client_v02.call_gemini("hello")


def test_call_gemini_raises_when_no_candidates_returned(monkeypatch) -> None:
    def fake_urlopen(req, timeout=None):
        return _json_response({"candidates": []})

    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setattr(gemini_client_v02.urllib.request, "urlopen", fake_urlopen)

    with pytest.raises(RuntimeError, match="Gemini returned no candidates"):
        gemini_client_v02.call_gemini("hello")


def test_call_gemini_raises_when_text_is_empty(monkeypatch) -> None:
    def fake_urlopen(req, timeout=None):
        return _json_response({"candidates": [{"content": {"parts": [{"text": "   "}]}}]})

    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setattr(gemini_client_v02.urllib.request, "urlopen", fake_urlopen)

    with pytest.raises(RuntimeError, match="Gemini returned empty text"):
        gemini_client_v02.call_gemini("hello")


def test_call_gemini_requires_non_empty_prompt(monkeypatch) -> None:
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")

    with pytest.raises(ValueError, match="prompt must be a non-empty string"):
        gemini_client_v02.call_gemini("   ")


def test_call_gemini_requires_api_key(monkeypatch) -> None:
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    with pytest.raises(EnvironmentError, match="GEMINI_API_KEY is not set"):
        gemini_client_v02.call_gemini("hello")
