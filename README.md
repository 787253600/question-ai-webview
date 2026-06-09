# AI 题库助手 WebView 桌面版

这是一个本地 AI 题库接口工具，适合搭配 [OCSJS](https://docs.ocsjs.com/) 使用。它提供一个 OpenAI 兼容接口配置界面，并保留 `/query` 接口给脚本调用。

## 功能

- 桌面 WebView 界面填写 API Key、AI Base URL、模型名和服务端口
- 本地保存配置到 `config.json`
- 服务端口可修改，修改后重启软件生效
- 内置题目测试区，支持单选、多选、判断、填空
- 返回最终答案 `answer` 和答案解析 `analysis`
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
- 服务端口，例如 `5130`

配置会保存到本地 `config.json`，该文件不会提交到 Git。

如果修改了服务端口，需要关闭并重新运行：

```bash
python desktop.py
```

## 只启动接口服务

如果不需要桌面窗口，也可以只启动 FastAPI 服务。默认端口是 `5130`：

```bash
uvicorn main:app --host 0.0.0.0 --port 5130
```

本地题库接口地址：

```text
http://127.0.0.1:5130/query
```

如果你在桌面 UI 中把端口改成了 `5200`，OCSJS 的题库地址也要改成：

```text
http://127.0.0.1:5200/query
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
  "answer": "A",
  "analysis": "1+1 等于 2，所以选择 A。"
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

## OCSJS 题库配置说明

OCSJS 的题库配置是一个数组，每一项告诉 OCSJS：请求哪个接口、传什么字段、收到结果后如何解析答案。

常用字段：

- `name`：题库名称
- `url`：题库接口地址
- `method`：请求方法，推荐 `post`
- `contentType`：本项目返回 JSON，所以填 `json`
- `type`：推荐 `GM_xmlhttpRequest`
- `headers`：POST JSON 时设置 `Content-Type: application/json`
- `data`：传给接口的数据，`${title}`、`${options}`、`${type}` 会由 OCSJS 自动替换
- `handler`：把接口响应转换成 OCSJS 需要的 `[题目, 答案]` 格式

## OCSJS 配置示例

启动 `python desktop.py` 并保存 AI 配置后，把下面片段加入 OCSJS 的题库配置中。端口要和软件当前运行端口一致。

```json
{
  "name": "GPT题库",
  "type": "GM_xmlhttpRequest",
  "method": "post",
  "contentType": "json",
  "url": "http://127.0.0.1:5130/query",
  "headers": {
    "Content-Type": "application/json"
  },
  "data": {
    "title": "${title}",
    "options": "${options}",
    "type": "${type}"
  },
  "handler": "return (res)=> res.code === 1 ? [res.question, res.answer, { ai: true, analysis: res.analysis }] : [res.msg, undefined]"
}
```

如果使用 `GM_xmlhttpRequest`，脚本需要允许连接本地地址：

```js
// @connect 127.0.0.1
```

题型返回规则：

- `single`：返回一个选项字母，例如 `A`
- `multiple`：返回多个选项字母，并用 `#` 分隔，例如 `A#C`
- `judgement`：返回 `正确` 或 `错误`
- `completion`：返回填空答案内容

多选题注意：OCSJS 文档要求多选题不要返回数组，要返回 `A#C` 这样的字符串。

## 配置文件

`config.example.json` 是示例配置，不包含真实密钥。

实际配置保存在：

```text
config.json
```

示例结构：

```json
{
  "api_key": "",
  "base_url": "https://openrouter.ai/api/v1",
  "model": "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free",
  "port": 5130
}
```

不要把 `config.json` 上传到 GitHub。

## 测试

```bash
pytest -v
```

## GitHub

本项目推送到公开仓库：

```text
https://github.com/787253600/question-ai-webview
```
