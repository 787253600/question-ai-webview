# Configurable Port and Answer Analysis Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a configurable local service port and return an `analysis` field alongside the final answer.

**Architecture:** Extend the existing JSON config with `port`, reuse that config in both FastAPI and the desktop launcher, and update the static UI to display dynamic endpoint/OCSJS snippets. Update model prompting to request JSON, parse `answer` and `analysis`, and preserve the OCSJS-compatible `answer` field.

**Tech Stack:** Python 3.12, FastAPI, Pydantic, OpenAI SDK, Uvicorn, pywebview, pytest, vanilla HTML/CSS/JavaScript.

---

## File Structure

- Modify `main.py` — add `port` to config schema/defaults, validate it, parse model JSON responses, and return `analysis`.
- Modify `desktop.py` — read `port` from config before starting Uvicorn and build runtime URL dynamically.
- Modify `static/index.html` — add service port input and answer analysis result area.
- Modify `static/app.js` — load/save port, update endpoint and OCSJS snippets dynamically, display analysis.
- Modify `config.example.json` — include default `port`.
- Modify `README.md` — document port changes, restart requirement, OCSJS config, and `analysis` response.
- Modify `tests/test_app.py` — cover config port validation, UI markers, model JSON parsing, and fallback behavior.
- Modify `tests/test_desktop.py` — cover dynamic port URL generation and readiness checks.

---

### Task 1: Add backend tests for port config and answer analysis

**Files:**
- Modify: `tests/test_app.py`

- [ ] **Step 1: Update default config test to include port**

Change expected JSON in `test_get_config_returns_defaults_without_secret` to:

```python
    assert response.json() == {
        "api_key": "",
        "base_url": "https://openrouter.ai/api/v1",
        "model": "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free",
        "port": 5130,
    }
```

- [ ] **Step 2: Update save config test to include port**

Change POST body and expected GET response in `test_save_config_persists_values` to include:

```python
"port": 5200,
```

- [ ] **Step 3: Add invalid port tests**

Append:

```python
def test_save_config_rejects_invalid_port(monkeypatch, tmp_path):
    app_module = load_app_with_temp_config(monkeypatch, tmp_path)
    client = TestClient(app_module.app)

    response = client.post(
        "/config",
        json={
            "api_key": "sk-test",
            "base_url": "https://example.test/v1",
            "model": "test-model",
            "port": 70000,
        },
    )

    assert response.status_code == 422
```

- [ ] **Step 4: Add model response parsing tests**

Append:

```python
def test_parse_model_content_extracts_answer_and_analysis(monkeypatch, tmp_path):
    app_module = load_app_with_temp_config(monkeypatch, tmp_path)

    parsed = app_module.parse_model_content(
        '{"answer":"The answer is B","analysis":"B 符合题意。"}',
        "single",
    )

    assert parsed == {"answer": "B", "analysis": "B 符合题意。"}


def test_parse_model_content_falls_back_for_plain_text(monkeypatch, tmp_path):
    app_module = load_app_with_temp_config(monkeypatch, tmp_path)

    parsed = app_module.parse_model_content("A and C", "multiple")

    assert parsed == {"answer": "A#C", "analysis": ""}
```

- [ ] **Step 5: Update UI test to expect port and analysis markers**

Add assertions in `test_home_page_serves_ui`:

```python
    assert "服务端口" in response.text
    assert "答案解析" in response.text
```

- [ ] **Step 6: Run tests and verify red**

Run:

```bash
pytest tests/test_app.py -v
```

Expected: failures for missing `port`, missing `parse_model_content`, and missing UI text.

---

### Task 2: Implement backend port config and answer analysis

**Files:**
- Modify: `main.py`
- Modify: `config.example.json`

- [ ] **Step 1: Add `port` to default config and schema**

Update `DEFAULT_CONFIG`:

```python
DEFAULT_CONFIG = {
    "api_key": "",
    "base_url": "https://openrouter.ai/api/v1",
    "model": "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free",
    "port": 5130,
}
```

Update imports:

```python
from pydantic import BaseModel, Field
```

Update `AppConfig`:

```python
class AppConfig(BaseModel):
    api_key: str = Field(min_length=1)
    base_url: str = Field(min_length=1)
    model: str = Field(min_length=1)
    port: int = Field(default=5130, ge=1, le=65535)
```

- [ ] **Step 2: Preserve env overrides only for AI fields**

Keep env overrides for `OPENAI_API_KEY`, `OPENAI_BASE_URL`, and `OPENAI_MODEL`; do not add a port environment variable.

- [ ] **Step 3: Add JSON model parser**

Add below `normalize_answer`:

```python
def parse_model_content(content: str, question_type: str) -> dict:
    try:
        payload = json.loads(content)
    except json.JSONDecodeError:
        return {"answer": normalize_answer(content, question_type), "analysis": ""}

    if not isinstance(payload, dict):
        return {"answer": normalize_answer(content, question_type), "analysis": ""}

    raw_answer = str(payload.get("answer", ""))
    analysis = str(payload.get("analysis", ""))
    return {"answer": normalize_answer(raw_answer, question_type), "analysis": analysis}
```

- [ ] **Step 4: Update prompt to request JSON**

Replace the return rules in `build_prompt` with text requiring:

```text
只返回 JSON，不要使用 Markdown 代码块，格式为：{"answer":"最终答案","analysis":"简短解析"}
```

Keep answer format rules for single/multiple/judgement/completion.

- [ ] **Step 5: Use parser in `ask_model`**

Replace direct `normalize_answer(...)` usage with:

```python
parsed = parse_model_content(response.choices[0].message.content.strip(), q.type)
return {
    "code": 1,
    "question": q.title,
    "answer": parsed["answer"],
    "analysis": parsed["analysis"],
}
```

- [ ] **Step 6: Update `config.example.json`**

Use:

```json
{
  "api_key": "",
  "base_url": "https://openrouter.ai/api/v1",
  "model": "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free",
  "port": 5130
}
```

- [ ] **Step 7: Run backend tests**

Run:

```bash
pytest tests/test_app.py -v
```

Expected: backend parser/config tests pass; UI marker test still fails until UI is updated.

---

### Task 3: Make desktop launcher use configured port

**Files:**
- Modify: `desktop.py`
- Modify: `tests/test_desktop.py`

- [ ] **Step 1: Update desktop tests for dynamic URL**

In `tests/test_desktop.py`, change expected URLs to use `desktop.build_url(5130)` and add:

```python
def test_build_url_uses_configured_port(monkeypatch):
    import desktop

    desktop = importlib.reload(desktop)
    monkeypatch.setattr(desktop, "read_config", lambda: {"port": 5200})

    assert desktop.get_port() == 5200
    assert desktop.build_url(5200) == "http://127.0.0.1:5200/"
```

- [ ] **Step 2: Run desktop tests and verify red**

Run:

```bash
pytest tests/test_desktop.py -v
```

Expected: failures because `build_url` and `get_port` do not exist yet.

- [ ] **Step 3: Implement dynamic port in `desktop.py`**

Update imports:

```python
from main import read_config
```

Replace fixed `PORT`/`URL` usage with:

```python
DEFAULT_PORT = 5130


def get_port() -> int:
    return int(read_config().get("port", DEFAULT_PORT))


def build_url(port: int) -> str:
    return f"http://{HOST}:{port}/"
```

Update functions:

```python
def run_server(port: int) -> None:
    uvicorn.run("main:app", host=HOST, port=port, log_level="info")


def wait_for_server(url: str, timeout_seconds: float = 10, interval_seconds: float = 0.2) -> bool:
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        try:
            urlopen(url, timeout=1)
            return True
        except OSError:
            time.sleep(interval_seconds)
    return False


def main() -> None:
    port = get_port()
    url = build_url(port)
    server_thread = threading.Thread(target=run_server, args=(port,), daemon=True)
    server_thread.start()
    wait_for_server(url)
    webview.create_window("AI 题库助手", url, width=1180, height=820, min_size=(960, 680))
    webview.start()
```

- [ ] **Step 4: Run desktop tests**

Run:

```bash
pytest tests/test_desktop.py -v
```

Expected: all desktop tests pass.

---

### Task 4: Update UI for port and analysis

**Files:**
- Modify: `static/index.html`
- Modify: `static/app.js`

- [ ] **Step 1: Add port input in HTML**

In the config form after model field, add:

```html
<label>
  服务端口
  <input id="port" name="port" type="number" min="1" max="65535" step="1" placeholder="5130">
</label>
```

- [ ] **Step 2: Add analysis area in HTML**

Inside `.result`, after `queryStatus`, add:

```html
<div class="analysis-box">
  <span>答案解析</span>
  <p id="analysis">暂无解析</p>
</div>
```

- [ ] **Step 3: Update OCSJS snippet in HTML**

Add `contentType` and analysis metadata:

```json
"contentType": "json",
"handler": "return (res)=> res.code === 1 ? [res.question, res.answer, { ai: true, analysis: res.analysis }] : [res.msg, undefined]"
```

- [ ] **Step 4: Update JS config payload**

Add selectors:

```javascript
const portInput = document.querySelector("#port");
const analysis = document.querySelector("#analysis");
```

Update `getConfigPayload()`:

```javascript
const port = Number(portInput.value || 5130);
return {
  api_key: apiKeyInput.value.trim(),
  base_url: baseUrlInput.value.trim(),
  model: modelInput.value.trim(),
  port,
};
```

- [ ] **Step 5: Add JS port validation and dynamic endpoint update**

In `validateConfig()`, reject ports outside `1-65535`.

Add:

```javascript
function getCurrentPort() {
  return window.location.port || "5130";
}

function buildEndpoint(port = getCurrentPort()) {
  return `${window.location.protocol}//${window.location.hostname}:${port}/query`;
}

function refreshEndpointText() {
  const endpointUrl = buildEndpoint();
  endpoint.textContent = endpointUrl;
  snippet.textContent = snippet.textContent.replace(/http:\/\/127\.0\.0\.1:\d+\/query/g, endpointUrl);
}
```

Call `refreshEndpointText()` on load.

- [ ] **Step 6: Load and save port in JS**

Set `portInput.value = config.port || 5130` in `loadConfig()`.

After save, if `String(config.port) !== getCurrentPort()`, show:

```text
配置已保存。端口修改需要重启软件后生效。
```

- [ ] **Step 7: Display analysis from query result**

On success:

```javascript
analysis.textContent = result.analysis || "暂无解析";
```

On failure/catch:

```javascript
analysis.textContent = "暂无解析";
```

- [ ] **Step 8: Run UI-serving tests**

Run:

```bash
pytest tests/test_app.py::test_home_page_serves_ui -v
```

Expected: pass.

---

### Task 5: Update README and verify everything

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Update README**

Add documentation that:

- Service port is configurable in the desktop UI.
- Port changes require restarting `python desktop.py`.
- OCSJS `url` must use the current port.
- `@connect 127.0.0.1` is needed when using `GM_xmlhttpRequest`.
- Successful `/query` now returns `analysis`.
- Handler can include `{ ai: true, analysis: res.analysis }`.

- [ ] **Step 2: Run all tests**

Run:

```bash
pytest -v
```

Expected: all tests pass.

- [ ] **Step 3: Compile Python files**

Run:

```bash
python -m py_compile main.py desktop.py
```

Expected: exit code 0.

- [ ] **Step 4: Run local server UI content check**

Run:

```bash
python -m uvicorn main:app --host 127.0.0.1 --port 5130
```

In another check, request `/` and `/config` and verify UI contains `服务端口` and `答案解析`, and `/config` contains `port`.

- [ ] **Step 5: Commit and push**

Run:

```bash
git add main.py desktop.py config.example.json static/index.html static/app.js README.md tests/test_app.py tests/test_desktop.py docs/superpowers/plans/2026-06-09-port-analysis.md
git commit -m "$(cat <<'EOF'
Add configurable port and answer analysis.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
git push
```

Expected: commit is pushed to GitHub.

---

## Self-Review

- Spec coverage: port config, restart behavior, dynamic desktop URL, answer analysis response, UI display, OCSJS handler docs, and tests are covered.
- Placeholder scan: no placeholders or vague implementation-only instructions remain.
- Type consistency: config uses `port`, model parser returns `answer` and `analysis`, and desktop helpers use `get_port()`/`build_url()` consistently.
