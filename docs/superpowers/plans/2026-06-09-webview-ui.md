# WebView Desktop UI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a polished pywebview desktop UI for configuring an OpenAI-compatible API and testing the existing OCSJS-compatible `/query` endpoint.

**Architecture:** Keep FastAPI as the backend and expose both API routes and a static UI. Add a local JSON config layer for API Key, Base URL, and model; start Uvicorn in a background thread from `desktop.py`, then open `pywebview` to the local UI.

**Tech Stack:** Python 3.12, FastAPI, Pydantic, OpenAI Python SDK, Uvicorn, pywebview, pytest, FastAPI TestClient, vanilla HTML/CSS/JavaScript.

---

## File Structure

- Create `.gitignore` — exclude virtualenvs, Python caches, local config, and IDE state.
- Create `requirements.txt` — runtime and test dependencies.
- Create `config.example.json` — safe example config without secrets.
- Modify `main.py` — add config load/save routes, static UI serving, safer client construction, and preserve `/query` GET/POST compatibility.
- Create `desktop.py` — start FastAPI on `127.0.0.1:5130` and open pywebview desktop window.
- Create `static/index.html` — desktop UI layout.
- Create `static/style.css` — polished dark gradient UI.
- Create `static/app.js` — load/save config, toggle secret visibility, run test query, copy OCSJS URL/config snippet.
- Create `tests/test_app.py` — automated coverage for config routes, validation, static UI, and OCSJS-compatible query routes using monkeypatched model calls.
- Modify `README.md` — installation, desktop startup, API usage, OCSJS integration, GitHub usage notes.

## Safety Rules

- Never commit `config.json`.
- Never commit real API keys found in existing files.
- Before first public GitHub push, remove hardcoded secret defaults from `main.py` and replace them with blank/example values.
- Public GitHub repository target: `question-ai-webview`.

---

### Task 1: Add repository safety files and dependencies

**Files:**
- Create: `.gitignore`
- Create: `requirements.txt`
- Create: `config.example.json`

- [ ] **Step 1: Create `.gitignore`**

Write this exact file to `C:\Users\choub\Desktop\python\16_regopenai\question\.gitignore`:

```gitignore
__pycache__/
*.py[cod]
*.pyo
*.pyd
.pytest_cache/
.coverage
htmlcov/

.venv/
venv/
env/

config.json
*.log

.idea/
.vscode/
.DS_Store
```

- [ ] **Step 2: Create `requirements.txt`**

Write this exact file to `C:\Users\choub\Desktop\python\16_regopenai\question\requirements.txt`:

```text
fastapi
uvicorn
openai
pywebview
pytest
httpx
```

- [ ] **Step 3: Create `config.example.json`**

Write this exact file to `C:\Users\choub\Desktop\python\16_regopenai\question\config.example.json`:

```json
{
  "api_key": "",
  "base_url": "https://openrouter.ai/api/v1",
  "model": "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free"
}
```

- [ ] **Step 4: Verify no generated files are accidentally tracked**

Run:

```bash
git status --short
```

Expected before Git init: if the repository is not initialized yet, this may print `fatal: not a git repository`. That is acceptable at this point.

---

### Task 2: Write backend tests for config and query behavior

**Files:**
- Create: `tests/test_app.py`
- Modify later: `main.py`

- [ ] **Step 1: Create `tests/test_app.py` with failing tests**

Write this exact file to `C:\Users\choub\Desktop\python\16_regopenai\question\tests\test_app.py`:

```python
import importlib

from fastapi.testclient import TestClient


def load_app_with_temp_config(monkeypatch, tmp_path):
    import main

    config_path = tmp_path / "config.json"
    monkeypatch.setattr(main, "CONFIG_PATH", config_path)
    return importlib.reload(main)


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
```

- [ ] **Step 2: Run tests to verify they fail before implementation**

Run:

```bash
pytest tests/test_app.py -v
```

Expected: failures because `/config` and `/` do not exist yet, and `CONFIG_PATH` is not defined yet.

---

### Task 3: Implement backend config, static UI serving, and safer model client construction

**Files:**
- Modify: `main.py`
- Test: `tests/test_app.py`

- [ ] **Step 1: Replace `main.py` with this implementation**

Write this exact content to `C:\Users\choub\Desktop\python\16_regopenai\question\main.py`:

```python
import json
import os
import re
import time
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from openai import OpenAI
from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = BASE_DIR / "config.json"
STATIC_DIR = BASE_DIR / "static"

DEFAULT_CONFIG = {
    "api_key": "",
    "base_url": "https://openrouter.ai/api/v1",
    "model": "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free",
}

app = FastAPI(title="AI 题库助手")

if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class Query(BaseModel):
    title: str
    options: str = ""
    type: str = ""


class AppConfig(BaseModel):
    api_key: str = Field(min_length=1)
    base_url: str = Field(min_length=1)
    model: str = Field(min_length=1)


def read_config() -> dict:
    config = DEFAULT_CONFIG.copy()
    config["api_key"] = os.getenv("OPENAI_API_KEY", config["api_key"])
    config["base_url"] = os.getenv("OPENAI_BASE_URL", config["base_url"])
    config["model"] = os.getenv("OPENAI_MODEL", config["model"])

    if CONFIG_PATH.exists():
        try:
            saved_config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
            for key in DEFAULT_CONFIG:
                if saved_config.get(key):
                    config[key] = saved_config[key]
        except json.JSONDecodeError:
            return config

    return config


def write_config(config: AppConfig) -> None:
    CONFIG_PATH.write_text(
        json.dumps(config.model_dump(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def build_prompt(q: Query) -> str:
    return f"""
你是一个考试题库助手，只返回最终答案，不要解释。

题目：{q.title}
题型：{q.type or "未提供"}
选项：{q.options or "未提供"}

返回规则：
- single：只返回一个选项字母，如 A
- multiple：只返回多个选项字母，并使用 # 分隔，如 A#C
- judgement：只返回 正确 或 错误
- completion：只返回填空答案内容
- 如果无法确定答案，只返回 不知道
""".strip()


def normalize_answer(answer: str, question_type: str) -> str:
    answer = answer.strip()
    qtype = (question_type or "").strip().lower()

    if qtype == "multiple":
        letters = re.findall(r"[A-Z]", answer.upper())
        if letters:
            unique_letters = []
            for letter in letters:
                if letter not in unique_letters:
                    unique_letters.append(letter)
            return "#".join(unique_letters)

        parts = [part.strip() for part in re.split(r"[#,，,、/\s]+", answer) if part.strip()]
        if parts:
            return "#".join(parts)

    if qtype == "single":
        match = re.search(r"[A-Z]", answer.upper())
        if match:
            return match.group(0)

    if qtype == "judgement":
        lowered = answer.lower()
        if any(token in lowered for token in ["正确", "对", "true", "yes", "√"]):
            return "正确"
        if any(token in lowered for token in ["错误", "错", "false", "no", "×"]):
            return "错误"

    return answer


def ask_model(q: Query) -> dict:
    config = read_config()
    if not config["api_key"] or not config["base_url"] or not config["model"]:
        return {"code": 0, "msg": "请先在桌面界面中填写并保存 API Key、Base URL 和模型名"}

    prompt = build_prompt(q)
    max_retries = 3
    client = OpenAI(api_key=config["api_key"], base_url=config["base_url"])

    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=config["model"],
                messages=[{"role": "user", "content": prompt}],
            )
            answer = normalize_answer(response.choices[0].message.content.strip(), q.type)
            return {"code": 1, "question": q.title, "answer": answer}
        except Exception as exc:
            print(f"请求失败，第 {attempt + 1} 次重试，错误：{exc}")
            time.sleep(1)

    return {"code": 0, "msg": "请求失败，请检查中转服务或模型是否可用"}


@app.get("/")
def index():
    index_path = STATIC_DIR / "index.html"
    if not index_path.exists():
        raise HTTPException(status_code=404, detail="UI 文件不存在")
    return FileResponse(index_path)


@app.get("/config")
def get_config():
    return read_config()


@app.post("/config")
def save_config(config: AppConfig):
    write_config(config)
    return {"ok": True}


@app.post("/query")
def query(q: Query):
    return ask_model(q)


@app.get("/query")
def query_get(title: str, options: str = "", type: str = ""):
    return ask_model(Query(title=title, options=options, type=type))
```

- [ ] **Step 2: Run backend tests**

Run:

```bash
pytest tests/test_app.py -v
```

Expected: `test_home_page_serves_ui` still fails until `static/index.html` exists; config and query tests pass.

---

### Task 4: Build the WebView UI assets

**Files:**
- Create: `static/index.html`
- Create: `static/style.css`
- Create: `static/app.js`
- Test: `tests/test_app.py`

- [ ] **Step 1: Create `static/index.html`**

Write this exact file to `C:\Users\choub\Desktop\python\16_regopenai\question\static\index.html`:

```html
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>AI 题库助手</title>
  <link rel="stylesheet" href="/static/style.css">
</head>
<body>
  <main class="shell">
    <section class="hero">
      <div>
        <p class="eyebrow">OCSJS Local Question API</p>
        <h1>AI 题库助手</h1>
        <p class="subtitle">填写 OpenAI 兼容接口配置，启动本地题库服务，并直接测试题目答案。</p>
      </div>
      <div class="endpoint-card">
        <span>本地题库接口</span>
        <code id="endpoint">http://127.0.0.1:5130/query</code>
        <button id="copyEndpoint" type="button">复制</button>
      </div>
    </section>

    <section class="grid">
      <form id="configForm" class="card">
        <div class="card-heading">
          <p class="eyebrow">Step 1</p>
          <h2>AI 接口配置</h2>
        </div>

        <label>
          API Key
          <div class="secret-row">
            <input id="apiKey" name="api_key" type="password" autocomplete="off" placeholder="sk-...">
            <button id="toggleSecret" type="button">显示</button>
          </div>
        </label>

        <label>
          AI Base URL
          <input id="baseUrl" name="base_url" type="url" placeholder="https://openrouter.ai/api/v1">
        </label>

        <label>
          模型名
          <input id="model" name="model" type="text" placeholder="nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free">
        </label>

        <button class="primary" type="submit">保存配置</button>
        <p id="configStatus" class="status">正在读取配置...</p>
      </form>

      <form id="queryForm" class="card accent-card">
        <div class="card-heading">
          <p class="eyebrow">Step 2</p>
          <h2>测试题目</h2>
        </div>

        <label>
          题目
          <textarea id="title" rows="5" placeholder="请输入题目内容"></textarea>
        </label>

        <label>
          选项
          <textarea id="options" rows="5" placeholder="A. 选项一&#10;B. 选项二"></textarea>
        </label>

        <label>
          题型
          <select id="questionType">
            <option value="single">single 单选</option>
            <option value="multiple">multiple 多选</option>
            <option value="judgement">judgement 判断</option>
            <option value="completion">completion 填空</option>
          </select>
        </label>

        <button class="primary" type="submit">测试回答</button>

        <div class="result">
          <span>答案结果</span>
          <strong id="answer">等待测试</strong>
          <p id="queryStatus" class="status"></p>
        </div>
      </form>
    </section>

    <section class="card footer-card">
      <div>
        <p class="eyebrow">OCSJS 配置提示</p>
        <h2>把题库 URL 指向本地服务</h2>
        <p>启动本软件并保存配置后，在 OCSJS 的题库配置中使用下面的地址。</p>
      </div>
      <pre id="ocsSnippet">{
  "name": "GPT题库",
  "type": "GM_xmlhttpRequest",
  "method": "post",
  "url": "http://127.0.0.1:5130/query",
  "headers": { "Content-Type": "application/json" },
  "data": {
    "title": "${title}",
    "options": "${options}",
    "type": "${type}"
  },
  "handler": "return (res)=> res.code === 1 ? [res.question, res.answer, { ai: true }] : [res.msg, undefined]"
}</pre>
      <button id="copySnippet" type="button">复制配置片段</button>
    </section>
  </main>

  <script src="/static/app.js"></script>
</body>
</html>
```

- [ ] **Step 2: Create `static/style.css`**

Write this exact file to `C:\Users\choub\Desktop\python\16_regopenai\question\static\style.css`:

```css
:root {
  color-scheme: dark;
  font-family: Inter, "Microsoft YaHei", "PingFang SC", system-ui, sans-serif;
  background: #08111f;
  color: #edf4ff;
}

* {
  box-sizing: border-box;
}

body {
  margin: 0;
  min-height: 100vh;
  background:
    radial-gradient(circle at top left, rgba(94, 234, 212, 0.18), transparent 32rem),
    radial-gradient(circle at top right, rgba(129, 140, 248, 0.24), transparent 28rem),
    linear-gradient(135deg, #07111f 0%, #111827 52%, #0f172a 100%);
}

button,
input,
textarea,
select {
  font: inherit;
}

button {
  border: 0;
  cursor: pointer;
}

.shell {
  width: min(1180px, calc(100% - 40px));
  margin: 0 auto;
  padding: 40px 0;
}

.hero,
.grid,
.footer-card {
  display: grid;
  gap: 22px;
}

.hero {
  grid-template-columns: minmax(0, 1fr) 360px;
  align-items: end;
  margin-bottom: 24px;
}

.eyebrow {
  margin: 0 0 8px;
  color: #67e8f9;
  font-size: 12px;
  font-weight: 800;
  letter-spacing: 0.18em;
  text-transform: uppercase;
}

h1,
h2,
p {
  margin-top: 0;
}

h1 {
  margin-bottom: 12px;
  font-size: clamp(36px, 6vw, 72px);
  line-height: 0.95;
}

h2 {
  margin-bottom: 0;
  font-size: 24px;
}

.subtitle {
  max-width: 680px;
  margin-bottom: 0;
  color: #b7c5d8;
  font-size: 18px;
}

.card,
.endpoint-card {
  border: 1px solid rgba(148, 163, 184, 0.22);
  border-radius: 28px;
  background: rgba(15, 23, 42, 0.72);
  box-shadow: 0 24px 80px rgba(0, 0, 0, 0.34);
  backdrop-filter: blur(18px);
}

.endpoint-card {
  padding: 20px;
}

.endpoint-card span,
.result span {
  display: block;
  margin-bottom: 8px;
  color: #94a3b8;
  font-size: 13px;
}

.endpoint-card code {
  display: block;
  margin-bottom: 14px;
  overflow-wrap: anywhere;
  color: #a7f3d0;
}

.grid {
  grid-template-columns: 0.92fr 1.08fr;
}

.card {
  padding: 26px;
}

.accent-card {
  background: linear-gradient(145deg, rgba(30, 41, 59, 0.86), rgba(15, 23, 42, 0.74));
}

.card-heading {
  margin-bottom: 22px;
}

label {
  display: grid;
  gap: 8px;
  margin-bottom: 18px;
  color: #dbeafe;
  font-weight: 700;
}

input,
textarea,
select {
  width: 100%;
  border: 1px solid rgba(148, 163, 184, 0.22);
  border-radius: 16px;
  outline: none;
  background: rgba(2, 6, 23, 0.56);
  color: #f8fafc;
  padding: 14px 15px;
}

textarea {
  resize: vertical;
}

input:focus,
textarea:focus,
select:focus {
  border-color: rgba(103, 232, 249, 0.72);
  box-shadow: 0 0 0 4px rgba(103, 232, 249, 0.12);
}

.secret-row {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 86px;
  gap: 10px;
}

.primary,
.endpoint-card button,
.footer-card button,
.secret-row button {
  border-radius: 999px;
  background: linear-gradient(135deg, #22d3ee, #818cf8);
  color: #03111f;
  padding: 12px 18px;
  font-weight: 900;
}

.primary {
  width: 100%;
  margin-top: 4px;
}

.secret-row button {
  padding-inline: 12px;
}

.status {
  min-height: 22px;
  margin: 14px 0 0;
  color: #a7f3d0;
}

.status.error {
  color: #fecaca;
}

.result {
  margin-top: 20px;
  border: 1px solid rgba(103, 232, 249, 0.18);
  border-radius: 22px;
  background: rgba(8, 47, 73, 0.36);
  padding: 20px;
}

.result strong {
  display: block;
  min-height: 36px;
  color: #fef3c7;
  font-size: 32px;
  overflow-wrap: anywhere;
}

.footer-card {
  grid-template-columns: minmax(0, 0.9fr) minmax(0, 1.1fr) auto;
  align-items: center;
  margin-top: 24px;
}

pre {
  margin: 0;
  max-height: 260px;
  overflow: auto;
  border-radius: 18px;
  background: rgba(2, 6, 23, 0.68);
  color: #bfdbfe;
  padding: 18px;
  white-space: pre-wrap;
}

@media (max-width: 900px) {
  .hero,
  .grid,
  .footer-card {
    grid-template-columns: 1fr;
  }
}
```

- [ ] **Step 3: Create `static/app.js`**

Write this exact file to `C:\Users\choub\Desktop\python\16_regopenai\question\static\app.js`:

```javascript
const apiKeyInput = document.querySelector("#apiKey");
const baseUrlInput = document.querySelector("#baseUrl");
const modelInput = document.querySelector("#model");
const configForm = document.querySelector("#configForm");
const queryForm = document.querySelector("#queryForm");
const configStatus = document.querySelector("#configStatus");
const queryStatus = document.querySelector("#queryStatus");
const answer = document.querySelector("#answer");
const toggleSecret = document.querySelector("#toggleSecret");
const endpoint = document.querySelector("#endpoint");
const snippet = document.querySelector("#ocsSnippet");

function setStatus(element, message, isError = false) {
  element.textContent = message;
  element.classList.toggle("error", isError);
}

function getConfigPayload() {
  return {
    api_key: apiKeyInput.value.trim(),
    base_url: baseUrlInput.value.trim(),
    model: modelInput.value.trim(),
  };
}

function validateConfig() {
  const config = getConfigPayload();
  if (!config.api_key || !config.base_url || !config.model) {
    setStatus(configStatus, "请填写 API Key、AI Base URL 和模型名。", true);
    return null;
  }
  return config;
}

async function loadConfig() {
  try {
    const response = await fetch("/config");
    if (!response.ok) throw new Error("读取配置失败");
    const config = await response.json();
    apiKeyInput.value = config.api_key || "";
    baseUrlInput.value = config.base_url || "";
    modelInput.value = config.model || "";
    setStatus(configStatus, config.api_key ? "配置已加载。" : "请填写并保存配置。");
  } catch (error) {
    setStatus(configStatus, "服务未启动或配置读取失败。", true);
  }
}

async function saveConfig(event) {
  event.preventDefault();
  const config = validateConfig();
  if (!config) return;

  try {
    const response = await fetch("/config", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(config),
    });
    if (!response.ok) throw new Error("保存失败");
    setStatus(configStatus, "配置已保存，重启后仍会自动加载。");
  } catch (error) {
    setStatus(configStatus, "配置保存失败，请检查输入内容。", true);
  }
}

async function runQuery(event) {
  event.preventDefault();
  if (!validateConfig()) return;

  const title = document.querySelector("#title").value.trim();
  const options = document.querySelector("#options").value.trim();
  const type = document.querySelector("#questionType").value;

  if (!title) {
    setStatus(queryStatus, "请先输入题目。", true);
    return;
  }

  answer.textContent = "请求中...";
  setStatus(queryStatus, "正在请求模型，请稍候。");

  try {
    const response = await fetch("/query", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title, options, type }),
    });
    if (!response.ok) throw new Error("请求失败");
    const result = await response.json();
    if (result.code === 1) {
      answer.textContent = result.answer || "无答案";
      setStatus(queryStatus, "测试成功。");
    } else {
      answer.textContent = "失败";
      setStatus(queryStatus, result.msg || "模型请求失败。", true);
    }
  } catch (error) {
    answer.textContent = "失败";
    setStatus(queryStatus, "服务未启动或网络请求失败。", true);
  }
}

async function copyText(text, statusElement, message) {
  try {
    await navigator.clipboard.writeText(text);
    setStatus(statusElement, message);
  } catch (error) {
    setStatus(statusElement, "复制失败，请手动复制。", true);
  }
}

configForm.addEventListener("submit", saveConfig);
queryForm.addEventListener("submit", runQuery);

toggleSecret.addEventListener("click", () => {
  const isHidden = apiKeyInput.type === "password";
  apiKeyInput.type = isHidden ? "text" : "password";
  toggleSecret.textContent = isHidden ? "隐藏" : "显示";
});

document.querySelector("#copyEndpoint").addEventListener("click", () => {
  copyText(endpoint.textContent, configStatus, "本地接口地址已复制。");
});

document.querySelector("#copySnippet").addEventListener("click", () => {
  copyText(snippet.textContent, configStatus, "OCSJS 配置片段已复制。");
});

loadConfig();
```

- [ ] **Step 4: Run tests after UI creation**

Run:

```bash
pytest tests/test_app.py -v
```

Expected: all tests pass.

---

### Task 5: Add desktop launcher

**Files:**
- Create: `desktop.py`

- [ ] **Step 1: Create `desktop.py`**

Write this exact file to `C:\Users\choub\Desktop\python\16_regopenai\question\desktop.py`:

```python
import threading
import time

import uvicorn
import webview

HOST = "127.0.0.1"
PORT = 5130
URL = f"http://{HOST}:{PORT}/"


def run_server() -> None:
    uvicorn.run("main:app", host=HOST, port=PORT, log_level="info")


def main() -> None:
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    time.sleep(1)
    webview.create_window("AI 题库助手", URL, width=1180, height=820, min_size=(960, 680))
    webview.start()


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run import smoke test**

Run:

```bash
python -m py_compile main.py desktop.py
```

Expected: command exits with code 0.

- [ ] **Step 3: Run automated tests again**

Run:

```bash
pytest tests/test_app.py -v
```

Expected: all tests pass.

---

### Task 6: Update README with install, desktop UI, API, and OCSJS instructions

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Replace `README.md` with complete usage docs**

Write this exact content to `C:\Users\choub\Desktop\python\16_regopenai\question\README.md`:

````markdown
# AI 题库助手 WebView 桌面版

这是一个本地 AI 题库接口工具，适合搭配 [OCSJS](https://docs.ocsjs.com/) 使用。它提供一个 OpenAI 兼容接口配置界面，并保留 `/query` 接口给脚本调用。

## 功能

- 桌面 WebView 界面填写 API Key、AI Base URL、模型名
- 本地保存配置到 `config.json`
- 内置题目测试区，支持单选、多选、判断、填空
- 提供 OCSJS 兼容的 `/query` GET/POST 接口
- 返回格式兼容 OCSJS 题库 handler

## 安装

建议使用 Python 3.12。

```bash
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
```

## 启动桌面界面

```bash
python desktop.py
```

启动后会打开“AI 题库助手”桌面窗口。先填写并保存：

- API Key
- AI Base URL，例如 `https://openrouter.ai/api/v1`
- 模型名，例如 `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free`

配置会保存到本地 `config.json`，该文件不会提交到 Git。

## 只启动接口服务

如果不需要桌面窗口，也可以只启动 FastAPI 服务：

```bash
uvicorn main:app --host 0.0.0.0 --port 5130
```

本地题库接口地址：

```text
http://127.0.0.1:5130/query
```

## API 用法

### POST `/query`

```bash
curl -X POST http://127.0.0.1:5130/query \
  -H "Content-Type: application/json" \
  -d '{"title":"1+1=?","options":"A.2\nB.3","type":"single"}'
```

成功返回示例：

```json
{
  "code": 1,
  "question": "1+1=?",
  "answer": "A"
}
```

失败返回示例：

```json
{
  "code": 0,
  "msg": "请求失败，请检查中转服务或模型是否可用"
}
```

### GET `/query`

```text
http://127.0.0.1:5130/query?title=1%2B1%3D%3F&options=A.2%0AB.3&type=single
```

## OCSJS 配置示例

启动 `python desktop.py` 并保存 AI 配置后，把下面片段加入 OCSJS 的题库配置中：

```json
{
  "name": "GPT题库",
  "type": "GM_xmlhttpRequest",
  "method": "post",
  "url": "http://127.0.0.1:5130/query",
  "headers": {
    "Content-Type": "application/json"
  },
  "data": {
    "title": "${title}",
    "options": "${options}",
    "type": "${type}"
  },
  "handler": "return (res)=> res.code === 1 ? [res.question, res.answer, { ai: true }] : [res.msg, undefined]"
}
```

题型返回规则：

- `single`：返回一个选项字母，例如 `A`
- `multiple`：返回多个选项字母，并用 `#` 分隔，例如 `A#C`
- `judgement`：返回 `正确` 或 `错误`
- `completion`：返回填空答案内容

## 配置文件

`config.example.json` 是示例配置，不包含真实密钥。

实际配置保存在：

```text
config.json
```

不要把 `config.json` 上传到 GitHub。

## 测试

```bash
pytest tests/test_app.py -v
```

## GitHub

本项目计划推送到公开仓库：

```text
question-ai-webview
```
````

- [ ] **Step 2: Check README does not contain a real API key**

Run:

```bash
python - <<'PY'
from pathlib import Path
text = Path('README.md').read_text(encoding='utf-8')
assert 'sk-' not in text
print('README secret check passed')
PY
```

Expected: prints `README secret check passed`.

---

### Task 7: Run verification and manually launch the desktop UI

**Files:**
- Verify: all project files

- [ ] **Step 1: Run automated tests**

Run:

```bash
pytest tests/test_app.py -v
```

Expected: all tests pass.

- [ ] **Step 2: Run compile smoke test**

Run:

```bash
python -m py_compile main.py desktop.py
```

Expected: command exits with code 0.

- [ ] **Step 3: Start desktop UI for manual verification**

Run:

```bash
python desktop.py
```

Expected: a desktop window titled `AI 题库助手` opens and loads the UI.

- [ ] **Step 4: Manual UI checks**

In the desktop window:

1. Confirm the top endpoint card shows `http://127.0.0.1:5130/query`.
2. Save API Key, AI Base URL, and model.
3. Confirm `config.json` is created locally.
4. Close and restart `python desktop.py`.
5. Confirm the saved configuration reloads.
6. Enter a single-choice test question and run test.
7. Confirm the answer result area changes from `等待测试` to a model answer or a clear failure message.

---

### Task 8: Initialize local Git repository and create first commit

**Files:**
- Track all source, test, docs, and config example files.
- Exclude `.idea/`, `__pycache__/`, and `config.json`.

- [ ] **Step 1: Initialize Git if needed**

Run:

```bash
git init
```

Expected: repository initialized or already initialized.

- [ ] **Step 2: Review status**

Run:

```bash
git status --short
```

Expected: project source files appear; `.idea/`, `__pycache__/`, and `config.json` do not appear.

- [ ] **Step 3: Stage safe files only**

Run:

```bash
git add .gitignore README.md main.py desktop.py requirements.txt config.example.json static/index.html static/style.css static/app.js tests/test_app.py docs/superpowers/specs/2026-06-09-webview-ui-design.md docs/superpowers/plans/2026-06-09-webview-ui.md
```

Expected: files are staged.

- [ ] **Step 4: Commit**

Run:

```bash
git commit -m "$(cat <<'EOF'
Add WebView desktop UI for local question API.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

Expected: a new commit is created.

---

### Task 9: Create GitHub repository and push

**Files:**
- Remote repository: public `question-ai-webview`

- [ ] **Step 1: Confirm GitHub authentication**

Run:

```bash
gh auth status
```

Expected: GitHub CLI reports an authenticated account. If not authenticated, ask the user to run:

```bash
! gh auth login
```

- [ ] **Step 2: Create public GitHub repository**

Run:

```bash
gh repo create question-ai-webview --public --source=. --remote=origin
```

Expected: GitHub repository is created and `origin` is added.

- [ ] **Step 3: Push the main branch**

Run:

```bash
git branch -M main && git push -u origin main
```

Expected: local commit is pushed to GitHub.

- [ ] **Step 4: Show remote URL**

Run:

```bash
gh repo view --web
```

Expected: the repository page opens in browser, or GitHub CLI prints the repository URL.

---

## Self-Review

- Spec coverage: config UI, local config persistence, `/query` compatibility, OCSJS README instructions, tests, Git initialization, GitHub public repo creation, and push are all covered.
- Placeholder scan: no `TBD`, `TODO`, or vague implementation-only instructions remain.
- Type consistency: `AppConfig`, `Query`, `read_config`, `write_config`, `ask_model`, `/config`, `/query`, and static asset paths are consistent across tasks.
