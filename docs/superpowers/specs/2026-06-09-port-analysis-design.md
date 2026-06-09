# 可修改端口与答案解析设计

## 目标

在现有 AI 题库助手中增加两个能力：

1. 用户可以在桌面 UI 中修改本地服务端口，配置保存到 `config.json`，重启软件后生效。
2. `/query` 接口除最终答案外，额外返回答案解析，UI 测试区展示解析，同时保持 OCSJS 自动答题仍使用干净的 `answer` 字段。

## 非目标

- 不做端口热切换；端口修改后需要重启软件。
- 不改变 OCSJS 当前可用的核心返回格式：`code`、`question`、`answer` 继续保留。
- 不把解析文本混入 `answer` 字段。

## OCSJS 题库配置理解

OCSJS 的题库配置是 `Array<AnswererWrapper>`。每个题库配置告诉 OCSJS：请求哪个接口、用什么方法传题目、拿到响应后如何解析答案。

关键字段：

- `url`：题库接口地址，例如 `http://127.0.0.1:5130/query`。
- `name`：题库名字。
- `homepage`：题库主页，可选。
- `method`：`get` 或 `post`，本项目推荐 `post`。
- `contentType`：本项目返回 JSON，所以使用 `json`。
- `type`：请求实现，推荐 `GM_xmlhttpRequest`。
- `headers`：POST JSON 时使用 `Content-Type: application/json`。
- `data`：发送给接口的数据，使用 `${title}`、`${options}`、`${type}` 等 OCSJS 占位符。
- `handler`：字符串形式的函数，用于把接口响应解析成 `[题目, 答案]`、二维数组，或 `[提示信息, undefined]`。

本项目继续推荐的 OCSJS 配置结构：

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

多选题仍返回 `A#C` 这种字符串，不返回数组。

## 端口配置设计

`config.json` 增加 `port` 字段：

```json
{
  "api_key": "",
  "base_url": "https://openrouter.ai/api/v1",
  "model": "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free",
  "port": 5130
}
```

默认端口为 `5130`。

### 启动行为

- `desktop.py` 启动时读取配置中的 `port`。
- FastAPI 绑定 `127.0.0.1:<port>`。
- WebView 打开 `http://127.0.0.1:<port>/`。
- readiness probe 检查同一个动态 URL。

### UI 行为

- 配置卡片增加“服务端口”输入框。
- 保存配置时校验端口必须是 `1-65535`。
- 如果用户保存的端口和当前运行端口不同，提示“端口修改需要重启软件后生效”。
- 顶部本地题库接口、底部 OCSJS 配置片段根据当前运行端口显示。

## 答案解析设计

### 提示词

提示词改为要求模型返回 JSON：

```json
{"answer":"A","analysis":"解析原因"}
```

要求：

- `answer` 只放最终答案。
- `analysis` 放简短解释。
- 单选、多选、判断、填空仍遵循原答案格式。

### 后端解析

`ask_model` 读取模型文本后：

1. 尝试把模型文本解析为 JSON。
2. 如果 JSON 中有 `answer`，取 `answer` 做现有归一化。
3. 如果 JSON 中有 `analysis`，作为解析返回。
4. 如果不是 JSON，则回退到旧逻辑：整段文本作为答案来源，`analysis` 为空字符串。

成功响应格式：

```json
{
  "code": 1,
  "question": "题目",
  "answer": "A",
  "analysis": "解析内容"
}
```

失败响应格式保持：

```json
{
  "code": 0,
  "msg": "请求失败，请检查中转服务或模型是否可用"
}
```

### UI 展示

测试结果区增加“答案解析”区域：

- 成功时显示 `analysis`。
- 无解析时显示“暂无解析”。
- 失败时清空解析或显示失败信息。

## README 更新

README 需要补充：

- 端口可在 UI 中修改。
- 修改端口后需要重启。
- OCSJS `url` 中的端口要与软件当前端口一致。
- `@connect` 仍主要配置 `127.0.0.1`。
- 接口成功响应新增 `analysis` 字段。
- OCSJS handler 可把解析放入第三个元信息对象。

## 测试方案

- 配置接口测试：默认返回 `port: 5130`。
- 配置保存测试：保存端口后再次读取能得到该端口。
- 配置校验测试：非法端口返回 422。
- 桌面测试：`desktop.py` 使用配置端口生成 URL 并等待服务。
- 模型响应测试：JSON 响应能解析出 `answer` 和 `analysis`。
- 回退测试：非 JSON 模型响应仍能返回 `answer`，`analysis` 为空。
- UI 测试：页面包含端口输入框、动态 OCSJS 片段和答案解析区域。
- README 检查：说明包含端口重启生效、analysis 字段和 OCSJS 配置。