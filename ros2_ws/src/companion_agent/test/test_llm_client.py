"""Tests for Ollama LLM client."""
from companion_agent.llm_client import generate_reply, is_available


def test_is_available_false_when_offline(monkeypatch):
    """Ollama probe returns False when the server is down."""
    def fake_urlopen(*_args, **_kwargs):
        raise OSError('offline')

    monkeypatch.setattr('companion_agent.llm_client.urllib.request.urlopen', fake_urlopen)
    assert is_available() is False


def test_generate_reply_parses_chat_response(monkeypatch):
    """Extract the model text from an Ollama chat payload."""
    class FakeResponse:
        def __init__(self, payload: bytes):
            self._payload = payload

        def read(self):
            return self._payload

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

    def fake_urlopen(_request, timeout=0):
        return FakeResponse(b'{"message": {"content": "Hey there!"}}')

    monkeypatch.setattr('companion_agent.llm_client.urllib.request.urlopen', fake_urlopen)
    assert generate_reply('hello') == 'Hey there!'
