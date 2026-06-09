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
    "port": 5130,
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
    port: int = Field(default=5130, ge=1, le=65535)


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
- 只返回 JSON，不要使用 Markdown 代码块，格式为：{"answer":"最终答案","analysis":"简短解析"}
- answer 只放最终答案，analysis 放简短解析
- single：answer 只放一个选项字母，如 A
- multiple：answer 只放多个选项字母，并使用 # 分隔，如 A#C
- judgement：answer 只放 正确 或 错误
- completion：answer 只放填空答案内容
- 如果无法确定答案，answer 只放 不知道
""".strip()


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
