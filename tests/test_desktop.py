import importlib


def test_build_url_uses_configured_port(monkeypatch):
    import desktop

    desktop = importlib.reload(desktop)
    monkeypatch.setattr(desktop, "read_config", lambda: {"port": 5200})

    assert desktop.get_port() == 5200
    assert desktop.build_url(5200) == "http://127.0.0.1:5200/"


def test_wait_for_server_retries_until_ready(monkeypatch):
    import desktop

    desktop = importlib.reload(desktop)
    attempts = []
    url = desktop.build_url(5130)

    def fake_urlopen(request_url, timeout):
        attempts.append((request_url, timeout))
        if len(attempts) < 3:
            raise OSError("not ready")
        return object()

    monkeypatch.setattr(desktop, "urlopen", fake_urlopen)
    monkeypatch.setattr(desktop.time, "sleep", lambda seconds: None)

    assert desktop.wait_for_server(url, timeout_seconds=1, interval_seconds=0.1) is True
    assert attempts == [(url, 1), (url, 1), (url, 1)]


def test_wait_for_server_returns_false_after_timeout(monkeypatch):
    import desktop

    desktop = importlib.reload(desktop)
    attempts = []
    now = iter([0, 0.1, 0.2, 0.7])
    url = desktop.build_url(5200)

    def fake_urlopen(request_url, timeout):
        attempts.append((request_url, timeout))
        raise OSError("not ready")

    monkeypatch.setattr(desktop, "urlopen", fake_urlopen)
    monkeypatch.setattr(desktop.time, "monotonic", lambda: next(now))
    monkeypatch.setattr(desktop.time, "sleep", lambda seconds: None)

    assert desktop.wait_for_server(url, timeout_seconds=0.5, interval_seconds=0.1) is False
    assert attempts == [(url, 1), (url, 1)]
