# AI 题库助手：Python 新手从建立到发布学习文档

这份文档写给 Python 新手，目标是带你理解这个项目是怎么从一个想法，逐步变成本地接口、桌面软件、测试项目，最后打包成 Windows 安装包的。

项目名称：**AI 题库助手 WebView 桌面版**  
项目用途：在本机启动一个 OpenAI 兼容的 AI 题库接口，供 OCSJS 或其他脚本调用，同时提供桌面界面填写配置、测试题目和复制接口地址。

阅读建议：

1. 先从“项目目标”读到“目录结构”，建立整体印象。
2. 再跟着“从 0 建立项目”理解每个文件为什么存在。
3. 最后看“测试、打包、发布”，理解一个 Python 项目怎样变成可交付的软件。

## 目录

- [1. 项目最终效果](#1-项目最终效果)
- [2. 项目目录结构](#2-项目目录结构)
- [3. 从 0 建立项目](#3-从-0-建立项目)
- [4. 配置文件设计](#4-配置文件设计)
- [5. 后端核心：main.py](#5-后端核心mainpy)
- [6. AI 请求与答案整理](#6-ai-请求与答案整理)
- [7. 后端接口路由](#7-后端接口路由)
- [8. 桌面入口：desktop.py](#8-桌面入口desktoppy)
- [9. 前端页面结构：static/index.html](#9-前端页面结构staticindexhtml)
- [10. 前端交互：static/app.js](#10-前端交互staticappjs)
- [11. 页面样式：static/style.css](#11-页面样式staticstylecss)
- [12. 自动化测试](#12-自动化测试)
- [13. OCSJS 题库配置](#13-ocsjs-题库配置)
- [14. 开发时如何运行项目](#14-开发时如何运行项目)
- [15. Windows 打包发布流程](#15-windows-打包发布流程)
- [16. 发布前检查清单](#16-发布前检查清单)
- [17. 常见问题排查](#17-常见问题排查)
- [18. 新手学习路线总结](#18-新手学习路线总结)
- [19. 后续维护这份文档](#19-后续维护这份文档)

---

## 1. 项目最终效果

这个项目最终提供两种使用方式。

第一种是桌面软件：

```bash
python desktop.py
```

这段命令的意思是：用 Python 运行 `desktop.py` 文件。`desktop.py` 会先启动本地 FastAPI 服务，然后打开一个 pywebview 桌面窗口，让用户在窗口里填写 API Key、Base URL、模型名和端口。

第二种是只启动接口服务：

```bash
uvicorn main:app --host 0.0.0.0 --port 5130
```

这段命令的意思是：用 `uvicorn` 启动 `main.py` 里面名叫 `app` 的 FastAPI 应用。`--host 0.0.0.0` 表示监听本机所有网卡，`--port 5130` 表示接口服务运行在 5130 端口。

启动后，本地题库接口地址是：

```text
http://127.0.0.1:5130/query
```

这段地址的意思是：访问本机 `127.0.0.1` 的 `5130` 端口，并请求 `/query` 接口。OCSJS 或浏览器脚本可以把题目发送到这个接口，让本项目调用 AI 模型并返回答案。

---

## 2. 项目目录结构

当前项目的核心结构如下：

```text
question/
├── main.py
├── desktop.py
├── static/
│   ├── index.html
│   ├── app.js
│   └── style.css
├── tests/
│   ├── test_app.py
│   └── test_desktop.py
├── config.example.json
├── requirements.txt
├── pytest.ini
├── build.bat
├── build_nuitka.bat
├── build_installer.bat
├── AIQuestionHelper.spec
├── installer.iss
├── README.md
└── docs/
```

这段目录树说明了项目里每个重要文件的位置。`main.py` 是后端接口核心，`desktop.py` 是桌面启动入口，`static/` 放网页界面，`tests/` 放自动化测试，`build*.bat` 和 `installer.iss` 负责 Windows 打包发布，`docs/` 放学习和设计文档。

每个核心文件的作用如下：

| 文件或目录 | 作用 |
| --- | --- |
| `main.py` | FastAPI 后端服务，负责配置读写、AI 请求、接口路由 |
| `desktop.py` | 启动本地服务，并用 pywebview 打开桌面窗口 |
| `static/index.html` | 桌面窗口里显示的 HTML 页面结构 |
| `static/app.js` | 前端交互逻辑，例如读取配置、保存配置、提交题目 |
| `static/style.css` | 前端页面样式 |
| `config.example.json` | 示例配置文件，不包含真实密钥 |
| `config.json` | 本地真实配置文件，不应该提交到 Git |
| `requirements.txt` | Python 依赖列表 |
| `tests/` | 测试代码 |
| `build.bat` | 使用 PyInstaller 打包 exe |
| `build_installer.bat` | 先打包 exe，再调用 Inno Setup 生成安装包 |
| `installer.iss` | Inno Setup 安装包配置 |

---

## 3. 从 0 建立项目

如果从空文件夹开始，可以按下面步骤建立这个项目。

### 3.1 创建项目目录

```bash
mkdir question
cd question
```

这段命令的意思是：先创建一个名为 `question` 的文件夹，然后进入这个文件夹。项目中的所有代码、配置、测试和文档都会放在这个目录里。

在当前项目中，目录已经存在，所以你不需要重复创建。

### 3.2 创建 Python 虚拟环境

```bash
python -m venv .venv
```

这段命令的意思是：用 Python 自带的 `venv` 模块创建一个虚拟环境，目录名叫 `.venv`。虚拟环境可以把本项目需要的依赖隔离起来，避免影响电脑上其他 Python 项目。

在 Windows Git Bash 里启用虚拟环境：

```bash
source .venv/Scripts/activate
```

这段命令的意思是：让当前终端开始使用 `.venv` 里的 Python 和 pip。启用成功后，终端前面通常会出现 `(.venv)`。

如果是在 Windows CMD 里，可以使用：

```bat
.venv\Scripts\activate.bat
```

这段命令的意思是：在 CMD 环境中启用 `.venv` 虚拟环境。Git Bash 和 CMD 的激活命令不同，所以要根据你使用的终端选择。

### 3.3 安装项目依赖

项目依赖写在 `requirements.txt`：

```text
fastapi
uvicorn
openai
pywebview
pytest
httpx
```

这段依赖列表的意思是：项目需要安装 6 个主要 Python 包。`fastapi` 用来写接口，`uvicorn` 用来运行接口服务，`openai` 用来调用 OpenAI 兼容接口，`pywebview` 用来显示桌面窗口，`pytest` 用来运行测试，`httpx` 是 FastAPI 测试客户端会用到的 HTTP 相关依赖。

安装依赖：

```bash
pip install -r requirements.txt
```

这段命令的意思是：让 pip 读取 `requirements.txt`，并自动安装里面列出的所有依赖。`-r` 表示从一个文件读取依赖清单。

---

## 4. 配置文件设计

本项目需要保存用户填写的 AI 配置，例如 API Key、Base URL、模型名和端口。

示例配置在 `config.example.json`：

```json
{
  "api_key": "",
  "base_url": "https://openrouter.ai/api/v1",
  "model": "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free",
  "port": 5130
}
```

这段 JSON 的意思是：项目默认使用 OpenRouter 的 OpenAI 兼容地址，默认模型是 `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free`，默认端口是 `5130`。`api_key` 留空，是因为真实密钥不能写进示例文件，也不能提交到公开仓库。

真实运行时会生成或读取 `config.json`：

```text
config.json
```

这段文本表示真实配置文件的文件名。它会保存用户在桌面界面填写的真实 API Key，因此 `.gitignore` 中已经把它排除，避免误传到 GitHub。

`.gitignore` 中相关规则是：

```gitignore
config.json
.venv/
.venv-build/
build/
dist/
```

这段规则的意思是：Git 不应该跟踪 `config.json`、虚拟环境目录和打包产物目录。`config.json` 可能包含密钥，虚拟环境和打包产物通常很大，而且可以重新生成，所以不适合提交。

---

## 5. 后端核心：main.py

`main.py` 是项目最重要的文件。它负责 4 件事：

1. 找到资源文件和配置文件。
2. 定义接口数据格式。
3. 读取、保存配置。
4. 调用 AI 模型并提供 `/query` 接口。

### 5.1 导入依赖

`main.py` 开头导入了这些模块：

```python
import json
import os
import re
import time
import sys
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from openai import OpenAI
from pydantic import BaseModel, Field
```

这段代码的意思是：前半部分导入 Python 标准库，后半部分导入第三方库。`json` 用来读写配置，`os` 用来读取环境变量，`re` 用来正则提取答案字母，`time` 用来失败重试时等待，`sys` 用来判断是否是打包后的 exe，`Path` 用来处理路径。`FastAPI` 是接口框架，`FileResponse` 用来返回 HTML 页面，`StaticFiles` 用来挂载静态资源，`OpenAI` 用来调用兼容接口，`BaseModel` 和 `Field` 用来定义请求和配置的数据格式。

### 5.2 处理源码运行和 exe 运行的路径差异

```python
if getattr(sys, "frozen", False):
    RESOURCE_DIR = Path(sys._MEIPASS)
    CONFIG_DIR = Path(sys.executable).resolve().parent
else:
    RESOURCE_DIR = Path(__file__).resolve().parent
    CONFIG_DIR = RESOURCE_DIR

CONFIG_PATH = CONFIG_DIR / "config.json"
STATIC_DIR = RESOURCE_DIR / "static"
```

这段代码的意思是：如果程序被 PyInstaller 打包成 exe，`sys.frozen` 会存在并为真。打包后，静态资源会被解压到临时目录 `sys._MEIPASS`，所以 `RESOURCE_DIR` 指向那里；但真实配置文件应该放在 exe 同目录，所以 `CONFIG_DIR` 指向 `sys.executable` 所在目录。源码运行时，资源和配置都放在项目根目录。最后两行分别拼出 `config.json` 和 `static/` 的完整路径。

### 5.3 默认配置

```python
DEFAULT_CONFIG = {
    "api_key": "",
    "base_url": "https://openrouter.ai/api/v1",
    "model": "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free",
    "port": 5130,
}
```

这段代码的意思是：定义程序没有找到配置文件时使用的默认值。默认 API Key 为空，提醒用户必须自己填写；默认 Base URL、模型名和端口可以让页面先显示一套可参考的配置。

### 5.4 创建 FastAPI 应用并挂载静态文件

```python
app = FastAPI(title="AI 题库助手")

if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
```

这段代码的意思是：先创建一个 FastAPI 应用，标题叫“AI 题库助手”。如果 `static/` 目录存在，就把它挂载到 `/static` 路径。这样浏览器访问 `/static/style.css` 或 `/static/app.js` 时，FastAPI 能正确返回静态文件。

### 5.5 定义请求和配置的数据模型

```python
class Query(BaseModel):
    title: str
    options: str = ""
    type: str = ""

class AppConfig(BaseModel):
    api_key: str = Field(min_length=1)
    base_url: str = Field(min_length=1)
    model: str = Field(min_length=1)
    port: int = Field(default=5130, ge=1, le=65535)
```

这段代码的意思是：定义两个 Pydantic 数据模型。`Query` 表示一道题，必须有 `title`，可以有 `options` 和 `type`。`AppConfig` 表示配置，要求 `api_key`、`base_url`、`model` 至少 1 个字符，`port` 必须是 1 到 65535 之间的整数。这样后端可以自动拒绝不合法的配置。

### 5.6 确保配置文件存在

```python
def ensure_config_file() -> None:
    if CONFIG_PATH.exists():
        return
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(
        json.dumps(DEFAULT_CONFIG, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
```

这段代码的意思是：如果 `config.json` 已经存在，就什么都不做；如果不存在，就先确保目录存在，再把默认配置写进去。`ensure_ascii=False` 可以让中文正常保存，`indent=2` 可以让 JSON 文件格式更容易阅读。

### 5.7 读取配置

```python
def read_config() -> dict:
    ensure_config_file()
    config = DEFAULT_CONFIG.copy()
    config["api_key"] = os.getenv("OPENAI_API_KEY", config["api_key"])
    config["base_url"] = os.getenv("OPENAI_BASE_URL", config["base_url"])
    config["model"] = os.getenv("OPENAI_MODEL", config["model"])
    try:
        saved_config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        for key in DEFAULT_CONFIG:
            if saved_config.get(key):
                config[key] = saved_config[key]
    except json.JSONDecodeError:
        pass
    return config
```

这段代码的意思是：先确保配置文件存在，然后从默认配置复制一份。接着尝试读取环境变量里的 API Key、Base URL 和模型名，再读取 `config.json` 里的保存值。保存值存在时会覆盖默认值。最后返回完整配置。如果配置文件不是合法 JSON，就忽略错误并继续使用默认值。

### 5.8 保存配置

```python
def write_config(config: AppConfig) -> None:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(
        json.dumps(config.model_dump(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
```

这段代码的意思是：把用户提交的配置保存到 `config.json`。`config.model_dump()` 会把 Pydantic 模型转换成普通字典，再用 `json.dumps` 转成格式化 JSON 字符串写入文件。

---

## 6. AI 请求与答案整理

项目不是直接把题目原样发给模型，而是先构造提示词，再要求模型返回固定格式的 JSON。

### 6.1 构造提示词

```python
def build_prompt(q: Query) -> str:
    return f"""
你是一个考试题库助手，只返回最终答案，不要解释。

题目：{q.title}
题型：{q.type or "未提供"}
选项：{q.options or "未提供"}

返回规则：
- 只返回 JSON，不要使用 Markdown 代码块，格式为：{{"answer":"最终答案","analysis":"简短解析"}}
- answer 只放最终答案，analysis 放简短解析
- single：answer 只放一个选项字母，如 A
- multiple：answer 只放多个选项字母，并使用 # 分隔，如 A#C
- judgement：answer 只放 正确 或 错误
- completion：answer 只放填空答案内容
- 如果无法确定答案，answer 只放 不知道
""".strip()
```

这段代码的意思是：把用户传来的题目、题型和选项拼成一段提示词。提示词明确要求模型只返回 JSON，并规定不同题型应该怎样写答案。`f"""..."""` 是 Python 的格式化多行字符串，可以把 `{q.title}` 这样的变量插入到文本里。最后的 `.strip()` 会去掉开头和结尾多余的空白。

### 6.2 规范化答案

```python
def normalize_answer(answer: str, question_type: str) -> str:
    answer = answer.strip()
    qtype = (question_type or "").strip().lower()
    if qtype in {"single", "multiple"}:
        letters = re.findall(r"(?<![A-Z])[A-H](?![A-Z])", answer.upper())
        unique_letters = []
        for letter in letters:
            if letter not in unique_letters:
                unique_letters.append(letter)
        if qtype == "single" and unique_letters:
            return unique_letters[-1]
        if qtype == "multiple" and unique_letters:
            return "#".join(unique_letters)
        parts = [part.strip() for part in re.split(r"[#,，,、/\s]+", answer) if part.strip()]
        if qtype == "multiple" and parts:
            return "#".join(parts)
    if qtype == "judgement":
        lowered = answer.lower()
        if any(token in lowered for token in ["不正确", "错误", "错", "false", "no", "×"]):
            return "错误"
        if any(token in lowered for token in ["正确", "对", "true", "yes", "√"]):
            return "正确"
    return answer
```

这段代码的意思是：把模型可能返回的自然语言答案整理成 OCSJS 更容易使用的格式。单选题会提取 A 到 H 中的选项字母，多选题会用 `#` 拼接选项，例如 `A#C`。判断题会把“正确、对、true、yes、√”整理成“正确”，把“不正确、错误、错、false、no、×”整理成“错误”。如果无法识别，就返回原始答案。

### 6.3 解析模型返回内容

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

这段代码的意思是：优先把模型返回的内容当作 JSON 解析。如果解析失败，就把整段内容当成普通答案处理，并让解析为空。如果解析成功但结果不是字典，也走普通答案处理。正常情况下，它会提取 `answer` 和 `analysis` 字段，并继续调用 `normalize_answer` 修正答案格式。

### 6.4 调用 AI 模型

```python
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
            parsed = parse_model_content(response.choices[0].message.content.strip(), q.type)
            return {
                "code": 1,
                "question": q.title,
                "answer": parsed["answer"],
                "analysis": parsed["analysis"],
            }
        except Exception as exc:
            print(f"请求失败，第 {attempt + 1} 次重试，错误：{exc}")
            time.sleep(1)
    return {"code": 0, "msg": "请求失败，请检查中转服务或模型是否可用"}
```

这段代码的意思是：先读取配置，如果 API Key、Base URL 或模型名缺失，就直接返回失败信息。配置完整时，它会创建 OpenAI 客户端，并最多尝试 3 次请求模型。请求成功后，解析模型内容并返回 `code: 1`、原题目、答案和解析。请求失败时会打印错误、等待 1 秒再重试，全部失败后返回 `code: 0`。

---

## 7. 后端接口路由

FastAPI 通过路由把 URL 和 Python 函数连接起来。

### 7.1 首页路由

```python
@app.get("/")
def index():
    index_path = STATIC_DIR / "index.html"
    if not index_path.exists():
        raise HTTPException(status_code=404, detail="UI 文件不存在")
    return FileResponse(index_path)
```

这段代码的意思是：当用户访问 `/` 时，后端返回 `static/index.html`。如果页面文件不存在，就返回 404 错误。桌面窗口打开的其实也是这个首页。

### 7.2 获取配置

```python
@app.get("/config")
def get_config():
    return read_config()
```

这段代码的意思是：当前端访问 `/config` 时，后端读取并返回当前配置。页面打开后会调用这个接口，把保存过的配置显示到输入框里。

### 7.3 保存配置

```python
@app.post("/config")
def save_config(config: AppConfig):
    write_config(config)
    return {"ok": True}
```

这段代码的意思是：当前端用 POST 方法提交配置到 `/config` 时，FastAPI 会先根据 `AppConfig` 校验数据。校验通过后，调用 `write_config` 保存配置，并返回 `{"ok": True}`。

### 7.4 POST 查询题目

```python
@app.post("/query")
def query(q: Query):
    return ask_model(q)
```

这段代码的意思是：脚本或前端可以用 POST 方法把题目 JSON 发到 `/query`。FastAPI 会把请求体转换成 `Query` 对象，然后交给 `ask_model` 调用 AI 并返回答案。

### 7.5 GET 查询题目

```python
@app.get("/query")
def query_get(title: str, options: str = "", type: str = ""):
    return ask_model(Query(title=title, options=options, type=type))
```

这段代码的意思是：为了兼容只会拼 URL 的调用方式，项目也支持 GET 请求。题目、选项和题型会从 URL 参数里读取，然后手动创建一个 `Query` 对象再调用 `ask_model`。

---

## 8. 桌面入口：desktop.py

`desktop.py` 的任务是：启动本地接口服务，然后打开一个桌面窗口显示网页界面。

### 8.1 导入依赖和设置主机

```python
import threading
import time
from urllib.request import urlopen
import uvicorn
import webview
from main import app, read_config

HOST = "127.0.0.1"
DEFAULT_PORT = 5130
```

这段代码的意思是：`threading` 用来开后台线程运行服务，`time` 用来等待服务启动，`urlopen` 用来检查服务是否能访问，`uvicorn` 用来运行 FastAPI，`webview` 用来打开桌面窗口。`HOST` 固定为 `127.0.0.1`，表示服务只在本机访问；`DEFAULT_PORT` 是默认端口。

### 8.2 读取端口和构造 URL

```python
def get_port() -> int:
    return int(read_config().get("port", DEFAULT_PORT))

def build_url(port: int) -> str:
    return f"http://{HOST}:{port}/"
```

这段代码的意思是：`get_port` 从配置文件读取端口，如果没有配置就使用 5130。`build_url` 根据主机和端口生成首页地址，例如 `http://127.0.0.1:5130/`。

### 8.3 启动服务

```python
def run_server(port: int) -> None:
    uvicorn.run(app, host=HOST, port=port, log_level="info")
```

这段代码的意思是：用 uvicorn 运行 `main.py` 中的 FastAPI 应用。`host=HOST` 表示只监听本机，`port=port` 表示使用配置里的端口，`log_level="info"` 表示输出普通运行日志。

### 8.4 等待服务就绪

```python
def wait_for_server(url: str, timeout_seconds: float = 20, interval_seconds: float = 0.2) -> bool:
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        try:
            with urlopen(url, timeout=1):
                return True
        except Exception:
            time.sleep(interval_seconds)
    return False
```

这段代码的意思是：桌面窗口不能在后端还没启动好时就打开，所以这个函数会反复访问首页地址。只要访问成功，就返回 `True`；如果 20 秒内一直访问失败，就返回 `False`。`time.monotonic()` 适合用来计算超时时间。

### 8.5 桌面程序主流程

```python
def main() -> None:
    port = get_port()
    url = build_url(port)

    server_thread = threading.Thread(target=run_server, args=(port,), daemon=True)
    server_thread.start()

    if not wait_for_server(url):
        raise RuntimeError(f"后端启动失败：{url}")

    webview.create_window(
        "AI 题库助手",
        url,
        width=1180,
        height=820,
        min_size=(960, 680),
    )

    webview.start()

if __name__ == "__main__":
    main()
```

这段代码的意思是：先读取端口并生成 URL，再创建一个后台线程启动 FastAPI 服务。等服务能访问后，创建名为“AI 题库助手”的桌面窗口，窗口内容就是本地网页。最后 `webview.start()` 进入桌面窗口事件循环。末尾的 `if __name__ == "__main__"` 表示只有直接运行 `desktop.py` 时才执行 `main()`。

---

## 9. 前端页面结构：static/index.html

桌面窗口显示的内容来自 `static/index.html`。它不是传统浏览器网站，而是被 pywebview 放进桌面窗口里显示的本地网页。

### 9.1 HTML 基础结构

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
    <!-- 页面内容 -->
  </main>
  <script src="/static/app.js"></script>
</body>
</html>
```

这段代码的意思是：声明这是一个 HTML 页面，语言是中文。`meta charset="utf-8"` 保证中文不会乱码，`viewport` 让页面适配窗口宽度，`title` 是窗口标题。`link` 引入 CSS 样式文件，`script` 引入 JavaScript 交互逻辑。

### 9.2 本地接口地址卡片

```html
<div class="endpoint-card">
  <span>本地题库接口</span>
  <code id="endpoint">http://127.0.0.1:5130/query</code>
  <button id="copyEndpoint" type="button">复制</button>
</div>
```

这段代码的意思是：页面上显示当前题库接口地址，并提供一个复制按钮。`id="endpoint"` 让 JavaScript 可以找到这段地址并动态更新端口，`id="copyEndpoint"` 让 JavaScript 可以给按钮绑定复制事件。

### 9.3 配置表单

```html
<form id="configForm" class="card">
  <label>
    API Key
    <input id="apiKey" name="api_key" type="password" autocomplete="off" placeholder="sk-...">
  </label>

  <label>
    AI Base URL
    <input id="baseUrl" name="base_url" type="url" placeholder="https://openrouter.ai/api/v1">
  </label>

  <label>
    模型名
    <input id="model" name="model" type="text" placeholder="nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free">
  </label>

  <label>
    服务端口
    <input id="port" name="port" type="number" min="1" max="65535" step="1" placeholder="5130">
  </label>

  <button class="primary" type="submit">保存配置</button>
</form>
```

这段代码的意思是：定义一个配置表单，让用户填写 API Key、Base URL、模型名和端口。API Key 使用 `type="password"`，默认隐藏输入内容。端口使用 `type="number"`，并限制在 1 到 65535。提交按钮会触发表单提交事件，再由 `app.js` 调用后端 `/config` 保存配置。

### 9.4 题目测试表单

```html
<form id="queryForm" class="card accent-card">
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
</form>
```

这段代码的意思是：定义一个题目测试表单。用户可以输入题目、选项和题型，然后点击“测试回答”。`textarea` 适合输入多行题目和选项，`select` 限定题型只能从单选、多选、判断、填空中选择，减少用户输错的可能。

### 9.5 答案和解析显示区域

```html
<div class="result">
  <span>答案结果</span>
  <strong id="answer">等待测试</strong>
  <p id="queryStatus" class="status"></p>
  <div class="analysis-box">
    <span>答案解析</span>
    <p id="analysis">暂无解析</p>
  </div>
</div>
```

这段代码的意思是：显示 AI 返回的最终答案和解析。`id="answer"` 用来显示答案，例如 `A` 或 `A#C`；`id="queryStatus"` 用来显示请求状态，例如“正在请求模型”；`id="analysis"` 用来显示简短解析。

### 9.6 OCSJS 配置片段

```html
<pre id="ocsSnippet">{
  "name": "GPT题库",
  "type": "GM_xmlhttpRequest",
  "method": "post",
  "contentType": "json",
  "url": "http://127.0.0.1:5130/query",
  "headers": { "Content-Type": "application/json" },
  "data": {
    "title": "${title}",
    "options": "${options}",
    "type": "${type}"
  },
  "handler": "return (res)=> res.code === 1 ? [res.question, res.answer, { ai: true, analysis: res.analysis }] : [res.msg, undefined]"
}</pre>
```

这段代码的意思是：在页面上展示一段可以复制到 OCSJS 的题库配置。`url` 指向本地 `/query` 接口，`data` 里的 `${title}`、`${options}`、`${type}` 会由 OCSJS 替换成真实题目信息，`handler` 负责把接口返回转换成 OCSJS 需要的格式。

---

## 10. 前端交互：static/app.js

`static/app.js` 负责让页面“动起来”。它读取输入框、调用后端接口、更新页面状态，并实现复制按钮。

### 10.1 获取页面元素

```js
const apiKeyInput = document.querySelector("#apiKey");
const baseUrlInput = document.querySelector("#baseUrl");
const modelInput = document.querySelector("#model");
const portInput = document.querySelector("#port");
const configForm = document.querySelector("#configForm");
const queryForm = document.querySelector("#queryForm");
const configStatus = document.querySelector("#configStatus");
const queryStatus = document.querySelector("#queryStatus");
const answer = document.querySelector("#answer");
const analysis = document.querySelector("#analysis");
```

这段代码的意思是：用 `document.querySelector` 根据 ID 找到页面上的输入框、表单和显示区域。后面的 JavaScript 需要通过这些变量读取用户输入，或者修改页面显示的文字。

### 10.2 显示状态信息

```js
function setStatus(element, message, isError = false) {
  element.textContent = message;
  element.classList.toggle("error", isError);
}
```

这段代码的意思是：封装一个显示状态的函数。`element.textContent = message` 会把提示文字显示到页面上；`classList.toggle("error", isError)` 会根据是否错误来添加或移除 `error` 样式，从而改变提示颜色。

### 10.3 生成当前接口地址

```js
function getCurrentPort() {
  return window.location.port || "5130";
}

function buildEndpoint(port = getCurrentPort()) {
  return `${window.location.protocol}//${window.location.hostname}:${port}/query`;
}
```

这段代码的意思是：`getCurrentPort` 从当前页面地址里读取端口，如果读不到就使用 `5130`。`buildEndpoint` 根据当前协议、主机名和端口生成 `/query` 接口地址。这样用户把端口改成 5200 后，页面也能显示正确接口地址。

### 10.4 收集配置表单数据

```js
function getConfigPayload() {
  return {
    api_key: apiKeyInput.value.trim(),
    base_url: baseUrlInput.value.trim(),
    model: modelInput.value.trim(),
    port: Number(portInput.value || 5130),
  };
}
```

这段代码的意思是：从表单输入框里读取 API Key、Base URL、模型名和端口，并组成一个 JavaScript 对象。`trim()` 会去掉输入内容前后的空格，`Number(...)` 会把端口从字符串转换成数字。

### 10.5 校验配置

```js
function validateConfig() {
  const config = getConfigPayload();
  if (!config.api_key || !config.base_url || !config.model) {
    setStatus(configStatus, "请填写 API Key、AI Base URL 和模型名。", true);
    return null;
  }
  if (!Number.isInteger(config.port) || config.port < 1 || config.port > 65535) {
    setStatus(configStatus, "服务端口必须是 1 到 65535 之间的整数。", true);
    return null;
  }
  return config;
}
```

这段代码的意思是：保存或测试前先检查配置是否完整。API Key、Base URL、模型名不能为空，端口必须是 1 到 65535 的整数。如果校验失败，就在页面显示错误并返回 `null`；如果校验通过，就返回配置对象。

### 10.6 页面打开时读取配置

```js
async function loadConfig() {
  try {
    const response = await fetch("/config");
    if (!response.ok) throw new Error("读取配置失败");
    const config = await response.json();
    apiKeyInput.value = config.api_key || "";
    baseUrlInput.value = config.base_url || "";
    modelInput.value = config.model || "";
    portInput.value = config.port || 5130;
    setStatus(configStatus, config.api_key ? "配置已加载。" : "请填写并保存配置。");
  } catch (error) {
    setStatus(configStatus, "服务未启动或配置读取失败。", true);
  }
}
```

这段代码的意思是：页面加载后自动请求后端 `/config` 接口。请求成功后，把配置填回输入框；如果已经有 API Key，就提示“配置已加载”，否则提示用户填写配置。`async` 和 `await` 用来等待网络请求完成，`try...catch` 用来处理请求失败。

### 10.7 保存配置

```js
async function saveConfig(event) {
  event.preventDefault();
  const config = validateConfig();
  if (!config) return;

  const response = await fetch("/config", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(config),
  });
}
```

这段代码的意思是：表单提交时先阻止浏览器默认刷新页面，再校验配置。如果配置合法，就用 POST 请求把配置发送到 `/config`。`headers` 告诉后端请求内容是 JSON，`JSON.stringify(config)` 把 JavaScript 对象转换成 JSON 字符串。

### 10.8 提交题目请求

```js
const response = await fetch("/query", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ title, options, type }),
});

const result = await response.json();
```

这段代码的意思是：把题目、选项和题型用 POST 请求发送到 `/query`。后端返回 JSON 后，`response.json()` 会把返回内容转换成 JavaScript 对象，前端再根据 `result.code` 判断请求成功还是失败。

### 10.9 复制文本

```js
async function copyText(text, statusElement, message) {
  try {
    await navigator.clipboard.writeText(text);
    setStatus(statusElement, message);
  } catch (error) {
    setStatus(statusElement, "复制失败，请手动复制。", true);
  }
}
```

这段代码的意思是：调用浏览器提供的剪贴板 API，把接口地址或 OCSJS 配置片段复制到剪贴板。复制成功时显示成功提示，失败时显示错误提示，让用户手动复制。

### 10.10 绑定页面事件

```js
configForm.addEventListener("submit", saveConfig);
queryForm.addEventListener("submit", runQuery);

refreshEndpointText();
loadConfig();
```

这段代码的意思是：把配置表单提交事件绑定到 `saveConfig`，把题目表单提交事件绑定到 `runQuery`。最后两行会在页面打开时刷新接口地址，并自动读取本地配置。

---

## 11. 页面样式：static/style.css

`static/style.css` 负责让页面看起来像一个完整的桌面应用，而不是普通的空白表单。

### 11.1 全局颜色和字体

```css
:root {
  color-scheme: dark;
  font-family: "Bahnschrift", "Microsoft YaHei", "PingFang SC", system-ui, sans-serif;
  background: #08111f;
  color: #edf4ff;
}
```

这段代码的意思是：设置整个页面的默认主题、字体、背景色和文字颜色。`color-scheme: dark` 告诉浏览器这是深色界面，`font-family` 优先使用适合 Windows 和中文显示的字体。

### 11.2 卡片样式

```css
.card,
.endpoint-card {
  border: 1px solid rgba(148, 163, 184, 0.22);
  border-radius: 28px;
  background: rgba(15, 23, 42, 0.72);
  box-shadow: 0 24px 80px rgba(0, 0, 0, 0.34);
  backdrop-filter: blur(18px);
}
```

这段代码的意思是：给配置区、测试区和接口地址区加上卡片效果。`border-radius` 让卡片圆角更明显，`box-shadow` 增加阴影，`backdrop-filter` 带来毛玻璃感，让界面更像现代桌面工具。

### 11.3 页面网格布局

```css
.hero {
  grid-template-columns: minmax(0, 1fr) 360px;
  align-items: end;
  margin-bottom: 24px;
}

.grid {
  grid-template-columns: 0.92fr 1.08fr;
}
```

这段代码的意思是：把页面分成左右两列。`hero` 区域左边显示标题，右边显示接口地址卡片；`grid` 区域左边是配置表单，右边是题目测试表单。`minmax(0, 1fr)` 可以防止内容太长时把布局撑坏。

### 11.4 输入框聚焦效果

```css
input:focus,
textarea:focus,
select:focus {
  border-color: rgba(103, 232, 249, 0.72);
  box-shadow: 0 0 0 4px rgba(103, 232, 249, 0.12);
}
```

这段代码的意思是：当用户点击输入框、文本框或下拉框时，边框会变亮，并出现一圈淡色光晕。这样用户能清楚知道当前正在编辑哪个控件。

### 11.5 响应式布局

```css
@media (max-width: 900px) {
  .hero,
  .grid,
  .footer-card {
    grid-template-columns: 1fr;
  }
}
```

这段代码的意思是：当窗口宽度小于 900 像素时，把原来的左右两列改成单列。这样窗口变窄时内容不会挤在一起，配置表单、测试表单和底部卡片会从上到下排列。

---

## 12. 自动化测试

测试的作用是：在修改代码后快速确认核心功能没有坏。这个项目使用 `pytest`。

### 12.1 pytest 配置

```ini
[pytest]
pythonpath = .
asyncio_default_fixture_loop_scope = function
```

这段代码的意思是：告诉 pytest 把项目根目录加入 Python 导入路径，这样测试中可以直接 `import main` 或 `import desktop`。`asyncio_default_fixture_loop_scope = function` 是异步测试相关设置，用来避免 pytest 插件给出默认作用域警告。

### 12.2 使用临时配置测试后端

```python
def load_app_with_temp_config(monkeypatch, tmp_path):
    import main

    app_module = importlib.reload(main)
    monkeypatch.setattr(app_module, "CONFIG_PATH", tmp_path / "config.json")
    return app_module
```

这段代码的意思是：测试时不应该读写真实的 `config.json`，否则可能污染用户本地配置。这个辅助函数会重新加载 `main.py`，然后用 `monkeypatch` 把 `CONFIG_PATH` 改到 pytest 提供的临时目录里。

### 12.3 测试默认配置

```python
def test_get_config_returns_defaults_without_secret(monkeypatch, tmp_path):
    app_module = load_app_with_temp_config(monkeypatch, tmp_path)
    client = TestClient(app_module.app)

    response = client.get("/config")

    assert response.status_code == 200
    assert response.json()["port"] == 5130
```

这段代码的意思是：创建一个测试客户端，请求 `/config` 接口，然后确认接口返回 200，并且默认端口是 5130。这里展示的是简化版，真实测试还会检查完整默认配置。

### 12.4 测试保存配置

```python
response = client.post(
    "/config",
    json={
        "api_key": "sk-test",
        "base_url": "https://example.test/v1",
        "model": "test-model",
        "port": 5200,
    },
)
```

这段代码的意思是：模拟前端向 `/config` 发送保存配置请求。`json={...}` 会让测试客户端自动发送 JSON 请求体。测试会继续检查接口是否返回成功，以及再次读取配置时是否能拿到刚保存的值。

### 12.5 测试题目接口形状

```python
def fake_ask_model(q):
    return {"code": 1, "question": q.title, "answer": "A"}

monkeypatch.setattr(app_module, "ask_model", fake_ask_model)

response = client.post(
    "/query",
    json={"title": "1+1=?", "options": "A.2\nB.3", "type": "single"},
)
```

这段代码的意思是：测试 `/query` 接口时，不真正请求 AI 模型，而是用 `fake_ask_model` 替换真实函数。这样测试更快、更稳定，也不会消耗 API Key。测试重点是确认接口能接收题目，并返回 OCSJS 兼容的数据形状。

### 12.6 运行测试

```bash
pytest -v
```

这段命令的意思是：运行整个测试套件。`-v` 是 verbose 的缩写，会显示更详细的测试名称和结果，方便你知道每个测试是否通过。

如果只想运行后端测试，可以用：

```bash
pytest tests/test_app.py -v
```

这段命令的意思是：只运行 `tests/test_app.py` 文件里的测试，适合你刚修改 `main.py` 后快速检查后端功能。

---

## 13. OCSJS 题库配置

OCSJS 需要知道三个信息：请求哪个接口、传哪些题目信息、怎样从返回结果里取出答案。

### 13.1 基础配置片段

```json
{
  "name": "GPT题库",
  "type": "GM_xmlhttpRequest",
  "method": "post",
  "contentType": "json",
  "url": "http://127.0.0.1:5130/query"
}
```

这段代码的意思是：定义一个名叫“GPT题库”的 OCSJS 题库。`type` 使用 `GM_xmlhttpRequest`，适合用户脚本跨域请求本地接口；`method` 使用 `post`；`contentType` 使用 `json`；`url` 指向本项目启动后的 `/query` 接口。

### 13.2 传递题目信息

```json
"data": {
  "title": "${title}",
  "options": "${options}",
  "type": "${type}"
}
```

这段代码的意思是：告诉 OCSJS 请求接口时要传哪些字段。`${title}` 会替换成题目标题，`${options}` 会替换成选项文本，`${type}` 会替换成题型。本项目后端的 `Query` 模型正好接收这三个字段。

### 13.3 解析返回结果

```js
return (res)=> res.code === 1
  ? [res.question, res.answer, { ai: true, analysis: res.analysis }]
  : [res.msg, undefined]
```

这段代码的意思是：如果后端返回 `code === 1`，说明 AI 请求成功，OCSJS 就拿到题目、答案和附加信息。如果失败，就把错误信息作为题目文本，把答案设为 `undefined`。多选题答案必须是 `A#C` 这样的字符串，而不是数组。

### 13.4 允许连接本地地址

```js
// @connect 127.0.0.1
```

这段代码的意思是：如果 OCSJS 运行在用户脚本管理器里，脚本可能需要声明允许连接的域名。`127.0.0.1` 表示本机地址，本项目接口就运行在本机，所以要允许脚本请求它。

---

## 14. 开发时如何运行项目

开发阶段通常先用源码运行，确认功能没问题后再打包。

### 14.1 运行桌面版

```bash
python desktop.py
```

这段命令的意思是：运行桌面入口文件。它会启动本地 FastAPI 后端，并打开 pywebview 窗口。开发 UI、配置保存、题目测试功能时，优先用这个命令。

### 14.2 只运行接口服务

```bash
uvicorn main:app --host 0.0.0.0 --port 5130
```

这段命令的意思是：只启动 FastAPI 接口，不打开桌面窗口。`main:app` 表示从 `main.py` 找到 `app` 这个 FastAPI 对象。这个模式适合调试接口、用 curl 测试请求，或者让其他程序调用本地题库接口。

### 14.3 用 curl 测试接口

```bash
curl -X POST http://127.0.0.1:5130/query \
  -H "Content-Type: application/json" \
  -d '{"title":"1+1=?","options":"A.2\nB.3","type":"single"}'
```

这段命令的意思是：用命令行模拟一次 POST 请求。`-X POST` 指定请求方法，`-H` 设置请求头，`-d` 发送 JSON 数据。接口会收到题目、选项和题型，然后调用 AI 返回答案。

接口成功时返回类似：

```json
{
  "code": 1,
  "question": "1+1=?",
  "answer": "A",
  "analysis": "1+1 等于 2，所以选择 A。"
}
```

这段返回结果的意思是：`code: 1` 表示成功，`question` 是原题目，`answer` 是最终答案，`analysis` 是简短解析。OCSJS 主要使用 `answer` 字段来完成答题。

接口失败时返回类似：

```json
{
  "code": 0,
  "msg": "请求失败，请检查中转服务或模型是否可用"
}
```

这段返回结果的意思是：`code: 0` 表示失败，`msg` 是给用户看的错误提示。常见原因包括 API Key 没填、Base URL 写错、模型不可用、网络请求失败。

---

## 15. Windows 打包发布流程

开发时运行 `python desktop.py` 很方便，但普通用户通常不想安装 Python 和依赖。因此发布时要把项目打包成 `.exe`，再进一步做成安装包。

### 15.1 准备构建虚拟环境

```bash
python -m venv .venv-build
```

这段命令的意思是：创建一个专门用于打包的虚拟环境 `.venv-build`。它和开发环境 `.venv` 分开，可以避免开发依赖、测试依赖和打包依赖互相影响。

启用构建环境：

```bash
source .venv-build/Scripts/activate
```

这段命令的意思是：在 Git Bash 中启用 `.venv-build`。启用后，安装的 PyInstaller、Nuitka 等打包工具都会进入这个构建环境，而不是污染系统 Python。

安装运行依赖和打包工具：

```bash
pip install -r requirements.txt
pip install pyinstaller
```

这段命令的意思是：第一行安装项目运行所需依赖，第二行安装 PyInstaller。PyInstaller 可以把 Python 程序和依赖打包成 Windows 可执行文件。

### 15.2 使用 build.bat 打包 exe

项目提供了 `build.bat`，用来自动清理旧文件并调用 PyInstaller。

```bat
@echo off
setlocal
cd /d "%~dp0"
```

这段代码的意思是：关闭命令回显，开启局部变量环境，然后切换到 bat 文件所在目录。`%~dp0` 是 Windows 批处理里的特殊写法，表示当前脚本所在的文件夹。

```bat
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build
if exist __pycache__ rmdir /s /q __pycache__
```

这段代码的意思是：如果存在旧的打包目录，就删除它们。`dist` 通常放最终 exe，`build` 放 PyInstaller 中间文件，`__pycache__` 放 Python 缓存。每次打包前清理，可以减少旧文件干扰。

```bat
.venv-build\Scripts\python.exe -m PyInstaller ^
 --clean ^
 --noconfirm ^
 --onefile ^
 --windowed ^
 --name AIQuestionHelper ^
 --add-data "static;static" ^
 --add-data "config.example.json;." ^
 desktop.py
```

这段代码的意思是：使用 `.venv-build` 里的 Python 运行 PyInstaller。`--onefile` 表示打包成单个 exe，`--windowed` 表示不显示黑色控制台窗口，`--name` 设置程序名，`--add-data` 把 `static/` 和 `config.example.json` 一起打进 exe，最后的 `desktop.py` 是程序入口。

实际项目里的命令还包含这些选项：

```bat
--collect-all webview ^
--collect-all pythonnet ^
--collect-all clr_loader ^
--hidden-import uvicorn ^
--hidden-import fastapi ^
--hidden-import starlette ^
```

这段代码的意思是：告诉 PyInstaller 额外收集 pywebview、pythonnet、clr_loader 等依赖，并显式包含 uvicorn、fastapi、starlette。桌面应用和 WebView 依赖有时不能被 PyInstaller 自动完整发现，所以需要这些参数补充。

运行打包脚本：

```bat
build.bat
```

这段命令的意思是：在 Windows 中执行 `build.bat`。成功后会在 `dist/` 目录生成 `AIQuestionHelper.exe`，这个 exe 就是可以直接运行的桌面程序。

### 15.3 AIQuestionHelper.spec 的作用

`AIQuestionHelper.spec` 是 PyInstaller 的配置文件。它可以把命令行参数写成 Python 配置，适合打包规则变复杂时使用。

```python
from PyInstaller.utils.hooks import collect_all

datas = [('static', 'static'), ('config.example.json', '.')]
binaries = []
hiddenimports = ['uvicorn', 'fastapi', 'starlette']
```

这段代码的意思是：导入 PyInstaller 的 `collect_all` 工具，并准备三个列表。`datas` 表示要一起打包的数据文件，`binaries` 表示二进制文件，`hiddenimports` 表示 PyInstaller 可能自动发现不了、但运行时需要的 Python 模块。

```python
tmp_ret = collect_all('webview')
datas += tmp_ret[0]
binaries += tmp_ret[1]
hiddenimports += tmp_ret[2]
```

这段代码的意思是：让 PyInstaller 收集 `webview` 包相关的所有数据、二进制文件和隐藏导入。pywebview 依赖较复杂，如果漏掉文件，打包后的 exe 可能启动失败。

```python
a = Analysis(
    ['desktop.py'],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
)
pyz = PYZ(a.pure)
```

这段代码的意思是：`Analysis` 会分析 `desktop.py` 入口依赖了哪些 Python 模块、数据文件和二进制文件。`PYZ` 会把纯 Python 模块打包成一个压缩归档，供最终 exe 使用。

```python
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    name='AIQuestionHelper',
    console=False,
)
```

这段代码的意思是：把前面分析到的脚本、二进制文件、数据文件和 Python 归档合并成最终 exe。`name` 是生成的程序名，`console=False` 表示运行时不弹出命令行窗口。

### 15.4 Nuitka 打包脚本

项目还提供了 `build_nuitka.bat`。Nuitka 是另一种 Python 打包方式，它会把 Python 代码编译成 C/C++ 后再构建，可能带来不同的兼容性和性能表现。

```bat
if not exist ".venv-build\Scripts\python.exe" (
  echo Missing .venv-build. Create it with: python -m venv .venv-build
  exit /b 1
)
```

这段代码的意思是：在运行 Nuitka 打包前，先检查 `.venv-build` 是否存在。如果构建环境不存在，就提示用户先创建虚拟环境，并退出脚本。

```bat
.venv-build\Scripts\python.exe -m pip install --upgrade nuitka ordered-set zstandard
.venv-build\Scripts\python.exe -m pip install --upgrade pywebview
.venv-build\Scripts\python.exe -m pip install pythonnet==3.0.3
```

这段代码的意思是：在构建环境中安装或更新 Nuitka 及其辅助依赖，并安装桌面窗口相关依赖。`pythonnet==3.0.3` 使用固定版本，可以减少打包时因为依赖版本变化导致的问题。

```bat
.venv-build\Scripts\python.exe -m nuitka ^
  --standalone ^
  --windows-console-mode=force ^
  --enable-plugin=pywebview ^
  --include-package=uvicorn ^
  --include-package=fastapi ^
  --include-data-dir=static=static ^
  --output-dir=dist ^
  desktop.py
```

这段代码的意思是：使用 Nuitka 打包 `desktop.py`。`--standalone` 表示生成可独立运行的程序目录，`--enable-plugin=pywebview` 启用 pywebview 支持，`--include-package` 指定要包含的包，`--include-data-dir` 把静态资源带上，`--output-dir=dist` 指定输出目录。

运行 Nuitka 打包脚本：

```bat
build_nuitka.bat
```

这段命令的意思是：执行 Nuitka 打包流程。它和 `build.bat` 是两条可选路线；如果 PyInstaller 打包结果有兼容问题，可以尝试 Nuitka 路线。

### 15.5 用 Inno Setup 生成安装包

单个 exe 可以直接运行，但安装包更适合发给普通用户。项目使用 `installer.iss` 配置 Inno Setup。

```iss
#define MyAppName "AIQuestionHelper"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Tolleytion"
#define MyAppExeName "AIQuestionHelper.exe"
```

这段代码的意思是：定义安装包里的应用名称、版本号、发布者和 exe 文件名。后面的安装配置会反复使用这些变量，避免同一个名字写很多遍。

```iss
[Setup]
AppName={#MyAppName}
AppVersion={#MyAppVersion}
DefaultDirName={localappdata}\Programs\{#MyAppName}
OutputDir=installer
OutputBaseFilename=AIQuestionHelper_Setup
PrivilegesRequired=lowest
```

这段代码的意思是：配置安装包基本信息。程序默认安装到当前用户的本地应用目录，安装包输出到 `installer/`，文件名是 `AIQuestionHelper_Setup.exe`。`PrivilegesRequired=lowest` 表示尽量不要求管理员权限。

```iss
[Files]
Source: "dist\AIQuestionHelper.exe"; DestDir: "{app}"; Flags: ignoreversion
```

这段代码的意思是：把 `dist/AIQuestionHelper.exe` 放进安装包，并在安装时复制到 `{app}` 目录。`{app}` 就是用户选择或默认的应用安装目录。

```iss
[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; Tasks: desktopicon
```

这段代码的意思是：创建开始菜单快捷方式和桌面快捷方式。`Filename` 指向安装后的 exe，`WorkingDir` 设置程序运行目录，`Tasks: desktopicon` 表示只有用户选择创建桌面图标时才生成桌面快捷方式。

```iss
[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "启动 {#MyAppName}"; WorkingDir: "{app}"; Flags: nowait postinstall skipifsilent
```

这段代码的意思是：安装完成后显示“启动 AIQuestionHelper”的选项。用户勾选后，安装器会立即运行程序。`nowait` 表示安装器不等待程序退出，`postinstall` 表示这是安装结束后的操作。

### 15.6 一键生成安装包

项目提供了 `build_installer.bat`，它会先打包 exe，再调用 Inno Setup 生成安装包。

```bat
call "%~dp0build.bat" nopause
if errorlevel 1 exit /b %errorlevel%
```

这段代码的意思是：先调用当前目录下的 `build.bat`。如果 exe 打包失败，就立刻退出，不继续生成安装包。这样可以避免把旧的或坏的 exe 打进安装包。

```bat
set "ISCC=D:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if not exist "%ISCC%" (
  echo 未找到 Inno Setup 6 的 ISCC.exe：%ISCC%
  exit /b 1
)
```

这段代码的意思是：指定 Inno Setup 编译器 `ISCC.exe` 的路径，并检查它是否存在。如果路径不对，脚本会提示用户检查安装路径，然后退出。

```bat
"%ISCC%" "%~dp0installer.iss"
```

这段代码的意思是：用 Inno Setup 编译 `installer.iss`。编译成功后，会根据 `installer.iss` 里的配置生成 `installer/AIQuestionHelper_Setup.exe`。

运行一键安装包脚本：

```bat
build_installer.bat
```

这段命令的意思是：先执行 PyInstaller 打包，再执行 Inno Setup 打包安装器。成功后可以把 `installer/AIQuestionHelper_Setup.exe` 发给用户安装。

---

## 16. 发布前检查清单

发布不是只看“能不能打包成功”，还要确认软件对用户可用。

### 16.1 代码和测试检查

```bash
pytest -v
```

这段命令的意思是：发布前运行全部测试，确认配置读写、接口返回、答案格式整理、桌面启动辅助函数等核心逻辑没有被改坏。测试失败时不要发布，应该先修复失败原因。

### 16.2 源码运行检查

```bash
python desktop.py
```

这段命令的意思是：用源码方式启动桌面程序，确认窗口能打开、配置能读取、接口地址能显示。发布前至少要手动打开一次，避免出现“测试通过但窗口打不开”的问题。

### 16.3 配置保存检查

```json
{
  "api_key": "sk-test",
  "base_url": "https://example.test/v1",
  "model": "test-model",
  "port": 5130
}
```

这段 JSON 的意思是：这是一次测试保存配置时可以参考的数据结构。发布前可以在桌面界面填写测试值并保存，然后确认 `config.json` 被正确写入。真实发布时不要把真实 API Key 写进仓库。

### 16.4 exe 运行检查

```bat
dist\AIQuestionHelper.exe
```

这段命令的意思是：直接运行打包后的 exe，确认它不是只能在源码环境中运行。重点检查窗口能否打开、静态页面是否加载、保存配置后重启是否仍然生效。

### 16.5 安装包检查

```bat
installer\AIQuestionHelper_Setup.exe
```

这段命令的意思是：运行生成的安装包，按普通用户方式安装软件。安装后检查开始菜单快捷方式、桌面快捷方式和安装完成后启动程序是否正常。

### 16.6 Git 发布检查

```bash
git status
```

这段命令的意思是：查看当前有哪些文件被修改、哪些文件还没有加入版本管理。发布前应该确认不会提交 `config.json`、`.venv/`、`.venv-build/`、`build/`、`dist/` 这类本地文件或构建产物。

```bash
git add README.md docs/python-newbie-release-guide.md
git commit -m "docs: add beginner release guide"
```

这段命令的意思是：如果你准备提交文档改动，只把 README 和新学习文档加入暂存区，然后创建一个文档提交。这里不要使用 `git add .`，因为它可能把本地配置或构建产物也一起加入。

---

## 17. 常见问题排查

### 17.1 端口被占用

如果启动时报端口被占用，可以把配置里的端口改成其他值，例如 5200。

```json
{
  "port": 5200
}
```

这段 JSON 的意思是：把服务端口改成 5200。修改端口后需要重启软件，因为后端服务启动时才会读取端口。

### 17.2 页面打开但请求失败

可以先检查配置是否完整：

```json
{
  "api_key": "你的 API Key",
  "base_url": "https://openrouter.ai/api/v1",
  "model": "模型名称",
  "port": 5130
}
```

这段 JSON 的意思是：AI 请求至少需要 API Key、Base URL 和模型名。任何一个为空，后端都会返回“请先在桌面界面中填写并保存 API Key、Base URL 和模型名”。

### 17.3 OCSJS 没有拿到答案

先确认题库 URL 和软件端口一致：

```text
http://127.0.0.1:5130/query
```

这段地址的意思是：OCSJS 会请求本机 5130 端口的 `/query` 接口。如果你把软件端口改成 5200，OCSJS 配置里的地址也必须改成 `http://127.0.0.1:5200/query`。

### 17.4 打包后 UI 文件不存在

如果 exe 启动后提示 UI 文件不存在，优先检查打包命令是否包含静态资源：

```bat
--add-data "static;static"
```

这段参数的意思是：告诉 PyInstaller 把项目里的 `static/` 目录打包进去，并在运行时仍然以 `static/` 这个名字访问。没有它，后端找不到 `index.html`、`style.css` 和 `app.js`。

---

## 18. 新手学习路线总结

如果你是第一次接触这种项目，可以按下面顺序学习。

```text
Python 基础
→ FastAPI 接口
→ JSON 配置文件
→ OpenAI 兼容接口调用
→ HTML/CSS/JavaScript 前端页面
→ pywebview 桌面封装
→ pytest 自动化测试
→ PyInstaller 或 Nuitka 打包
→ Inno Setup 安装包发布
```

这段路线的意思是：先理解 Python 和后端接口，再理解配置、AI 请求和前端页面，然后学习如何把网页放进桌面窗口，最后学习测试和发布。这个项目正好把这些知识串在了一起。

最后可以用一句话理解整个项目：

```text
用户在桌面窗口填写配置和题目，前端把请求发给本机 FastAPI，FastAPI 调用 OpenAI 兼容模型，再把整理后的答案返回给前端或 OCSJS。
```

这段话的意思是：桌面窗口只是用户界面，真正处理请求的是本机后端；AI 模型负责回答题目；答案整理逻辑负责把模型输出变成 OCSJS 能识别的格式。

---

## 19. 后续维护这份文档

当项目代码变化时，这份学习文档也要同步更新。最简单的规则是：只要改了入口文件、接口字段、配置字段、打包命令或发布步骤，就检查本文档是否还准确。

```text
改 main.py → 检查后端接口、配置、AI 请求章节
改 desktop.py → 检查桌面入口章节
改 static/ → 检查前端页面、交互和样式章节
改 tests/ → 检查自动化测试章节
改 build*.bat 或 installer.iss → 检查打包发布章节
```

这段清单的意思是：代码和文档要一一对应。哪个区域的代码变了，就回到对应章节更新说明，避免新手按照旧文档学习时遇到不一致的问题。
