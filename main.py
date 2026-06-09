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
