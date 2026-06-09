import importlib

from fastapi.testclient import TestClient


def load_app_with_temp_config(monkeypatch, tmp_path):
    import main

    app_module = importlib.reload(main)
    monkeypatch.setattr(app_module, "CONFIG_PATH", tmp_path / "config.json")
    return app_module


def test_get_config_returns_defaults_without_secret(monkeypatch, tmp_path):
    app_module = load_app_with_temp_config(monkeypatch, tmp_path)
    client = TestClient(app_module.app)

    response = client.get("/config")

    assert response.status_code == 200
    assert response.json() == {
        "api_key": "",
        "base_url": "https://openrouter.ai/api/v1",
        "model": "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free",
    }


def test_save_config_persists_values(monkeypatch, tmp_path):
    app_module = load_app_with_temp_config(monkeypatch, tmp_path)
    client = TestClient(app_module.app)

    response = client.post(
        "/config",
        json={
            "api_key": "sk-test",
            "base_url": "https://example.test/v1",
            "model": "test-model",
        },
    )

    assert response.status_code == 200
    assert response.json() == {"ok": True}
    assert client.get("/config").json() == {
        "api_key": "sk-test",
        "base_url": "https://example.test/v1",
        "model": "test-model",
    }


def test_save_config_rejects_missing_required_values(monkeypatch, tmp_path):
    app_module = load_app_with_temp_config(monkeypatch, tmp_path)
    client = TestClient(app_module.app)

    response = client.post(
        "/config",
        json={"api_key": "", "base_url": "https://example.test/v1", "model": "test-model"},
    )

    assert response.status_code == 422


def test_query_post_uses_ocsjs_compatible_shape(monkeypatch, tmp_path):
    app_module = load_app_with_temp_config(monkeypatch, tmp_path)
    client = TestClient(app_module.app)

    def fake_ask_model(q):
        return {"code": 1, "question": q.title, "answer": "A"}

    monkeypatch.setattr(app_module, "ask_model", fake_ask_model)

    response = client.post(
        "/query",
        json={"title": "1+1=?", "options": "A.2\nB.3", "type": "single"},
    )

    assert response.status_code == 200
    assert response.json() == {"code": 1, "question": "1+1=?", "answer": "A"}


def test_query_get_uses_ocsjs_compatible_shape(monkeypatch, tmp_path):
    app_module = load_app_with_temp_config(monkeypatch, tmp_path)
    client = TestClient(app_module.app)

    def fake_ask_model(q):
        return {"code": 1, "question": q.title, "answer": "正确"}

    monkeypatch.setattr(app_module, "ask_model", fake_ask_model)

    response = client.get("/query", params={"title": "天空是蓝色", "type": "judgement"})

    assert response.status_code == 200
    assert response.json() == {"code": 1, "question": "天空是蓝色", "answer": "正确"}


def test_home_page_serves_ui(monkeypatch, tmp_path):
    app_module = load_app_with_temp_config(monkeypatch, tmp_path)
    client = TestClient(app_module.app)

    response = client.get("/")

    assert response.status_code == 200
    assert "AI 题库助手" in response.text


def test_single_choice_normalizes_prose_answer(monkeypatch, tmp_path):
    app_module = load_app_with_temp_config(monkeypatch, tmp_path)

    assert app_module.normalize_answer("The answer is B", "single") == "B"


def test_multiple_choice_normalizes_prose_answer(monkeypatch, tmp_path):
    app_module = load_app_with_temp_config(monkeypatch, tmp_path)

    assert app_module.normalize_answer("A and C", "multiple") == "A#C"


def test_judgement_normalizes_negative_phrase(monkeypatch, tmp_path):
    app_module = load_app_with_temp_config(monkeypatch, tmp_path)

    assert app_module.normalize_answer("不正确", "judgement") == "错误"
