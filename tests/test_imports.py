import sys
import types

def test_import_main_and_agent():
    import importlib
    m_main = importlib.import_module('main')
    m_agent = importlib.import_module('agent')
    assert hasattr(m_main, 'AutonomousNetworkApp')
    assert hasattr(m_agent, 'call_ollama')

def test_call_ollama_mock(monkeypatch):
    import agent
    class DummyResp:
        def __init__(self, ok=True, text='ok', json_data=None, status_code=200):
            self._json = json_data
            self.text = text
            self.status_code = status_code
            self.ok = ok
        def json(self):
            if self._json is None:
                raise ValueError('no json')
            return self._json

    def fake_post(url, json=None, timeout=None):
        return DummyResp(ok=True, json_data={"response": "```python\nprint(\"hello\")\n```"})

    monkeypatch.setattr('requests.post', fake_post)
    res = agent.call_ollama('hi')
    assert 'print' in res or 'hello' in res
