import io
import json
import urllib.error

import pytest

from app.services import ai


def test_mock_is_used_without_api_key(monkeypatch):
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    content, source = ai.generate_plan("Physics", 9, "Density", None)
    assert source == "mock"
    assert "Short-term plan: Density" in content
    assert "Understand and apply the key ideas of the topic Density." in content


def test_openrouter_request_and_response(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    monkeypatch.setenv("OPENROUTER_MODEL", "test/model")
    captured = {}

    def fake_urlopen(request, timeout):
        captured["url"] = request.full_url
        captured["headers"] = dict(request.header_items())
        captured["body"] = json.loads(request.data)
        reply = {"choices": [{"message": {"content": "# Generated plan"}}]}
        return io.BytesIO(json.dumps(reply).encode())

    monkeypatch.setattr(ai.urllib.request, "urlopen", fake_urlopen)
    content, source = ai.generate_plan("Physics", 9, "Density", "Measure density")

    assert (content, source) == ("# Generated plan", "openrouter")
    assert captured["url"] == ai.OPENROUTER_URL
    assert captured["headers"]["Authorization"] == "Bearer test-key"
    assert captured["body"]["model"] == "test/model"
    user_message = captured["body"]["messages"][1]["content"]
    assert "Topic: Density" in user_message
    assert "Measure density" in user_message


@pytest.mark.parametrize(
    "failure",
    [urllib.error.URLError("no network"), TimeoutError()],
)
def test_openrouter_network_errors(monkeypatch, failure):
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")

    def fake_urlopen(request, timeout):
        raise failure

    monkeypatch.setattr(ai.urllib.request, "urlopen", fake_urlopen)
    with pytest.raises(ai.AIServiceError):
        ai.generate_plan("Physics", 9, "Density", None)


def test_openrouter_unexpected_response(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    monkeypatch.setattr(
        ai.urllib.request, "urlopen", lambda request, timeout: io.BytesIO(b"{}")
    )
    with pytest.raises(ai.AIServiceError):
        ai.generate_plan("Physics", 9, "Density", None)
