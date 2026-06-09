import importlib


def test_wait_for_server_retries_until_ready(monkeypatch):
    import desktop

    desktop = importlib.reload(desktop)
    attempts = []

    def fake_urlopen(url, timeout):
        attempts.append((url, timeout))
        if len(attempts) < 3:
            raise OSError("not ready")
        return object()

    monkeypatch.setattr(desktop, "urlopen", fake_urlopen)
    monkeypatch.setattr(desktop.time, "sleep", lambda seconds: None)

    assert desktop.wait_for_server(timeout_seconds=1, interval_seconds=0.1) is True
    assert attempts == [
        ("http://127.0.0.1:5130/", 1),
        ("http://127.0.0.1:5130/", 1),
        ("http://127.0.0.1:5130/", 1),
    ]


def test_wait_for_server_returns_false_after_timeout(monkeypatch):
    import desktop

    desktop = importlib.reload(desktop)
    attempts = []
    now = iter([0, 0.1, 0.2, 0.7])

    def fake_urlopen(url, timeout):
        attempts.append((url, timeout))
        raise OSError("not ready")

    monkeypatch.setattr(desktop, "urlopen", fake_urlopen)
    monkeypatch.setattr(desktop.time, "monotonic", lambda: next(now))
    monkeypatch.setattr(desktop.time, "sleep", lambda seconds: None)

    assert desktop.wait_for_server(timeout_seconds=0.5, interval_seconds=0.1) is False
    assert attempts == [
        ("http://127.0.0.1:5130/", 1),
        ("http://127.0.0.1:5130/", 1),
    ]
