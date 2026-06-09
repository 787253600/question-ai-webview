# WebView 桌面 UI 设计

## 目标

为当前 FastAPI 题库接口项目增加一个好看的桌面 WebView 界面。用户运行桌面启动脚本后，可以在窗口中填写并保存 AI API Key、AI Base URL 和模型名，也可以直接测试题目回答。现有 `/query` 接口继续保留，用于配合 OCSJS 调用。

## 非目标

- 不把真实 API Key 写入 README、示例配置或 Git 仓库。
- 不改变 OCSJS 期望的题库接口返回格式。
- 不做账号系统、云端同步或多用户配置。

## 架构

采用 `pywebview` 桌面窗口加 FastAPI 后端的方案。

- `main.py` 继续作为 FastAPI 应用入口，提供 `/query` GET/POST 接口。
- `desktop.py` 启动本地 FastAPI 服务，并打开 pywebview 桌面窗口。
- UI 页面由 FastAPI 托管，默认打开 `http://127.0.0.1:5130/`。
- 配置保存到本地 `config.json`，重启后自动读取。
- README 说明普通接口使用、桌面 UI 启动方式，以及 OCSJS 配置方式。

## 文件结构

```text
question/
  main.py              # FastAPI 接口、AI 调用、配置读取/保存接口
  desktop.py           # 启动 FastAPI + pywebview 桌面窗口
  requirements.txt     # fastapi、uvicorn、openai、pywebview 等依赖
  config.example.json  # 示例配置，不包含真实 API Key
  static/
    index.html         # WebView UI 页面
    app.js             # 表单、保存配置、测试请求逻辑
    style.css          # 美观界面样式
  README.md            # 使用说明 + OCSJS 配置说明
```

## 数据流

1. 用户运行 `python desktop.py`。
2. 程序启动本地 FastAPI 服务。
3. pywebview 打开桌面窗口并加载 `http://127.0.0.1:5130/`。
4. UI 启动时请求 `/config` 读取本地配置。
5. 用户填写 API Key、AI Base URL、模型名，点击保存。
6. UI 调用 `/config` 保存到 `config.json`。
7. 用户在测试区填写题目、选项、题型，点击测试。
8. UI 调用 `/query`。
9. FastAPI 根据保存的配置创建 OpenAI 兼容客户端，请求模型。
10. FastAPI 返回 OCSJS 兼容格式。

成功返回格式：

```json
{
  "code": 1,
  "question": "题目",
  "answer": "A"
}
```

失败返回格式：

```json
{
  "code": 0,
  "msg": "请求失败，请检查中转服务或模型是否可用"
}
```

## 界面设计

界面使用现代深色/渐变风格，整体像一个小型 AI 题库助手桌面软件。

- 顶部显示应用名称“AI 题库助手”和本地题库接口地址 `http://127.0.0.1:5130/query`。
- 左侧配置卡片包含 API Key、AI Base URL、模型名、保存按钮和配置状态提示。
- API Key 使用密码输入框，并提供显示/隐藏切换。
- 右侧测试卡片包含题目、选项、题型下拉框、测试按钮和答案结果区。
- 底部显示 OCSJS 快速提示，提醒用户把题库 URL 指向本地 `/query` 接口。

## 错误处理

- API Key、AI Base URL、模型名为空时，UI 阻止保存或测试，并提示需要补全配置。
- AI 调用失败时，后端返回 `code: 0` 和清晰错误提示。
- UI 网络请求失败时显示“服务未启动”“配置未保存”或“模型请求失败”等用户可理解信息。
- 示例配置和 README 不包含真实密钥。

## OCSJS 集成

README 需要说明本项目用于搭配 OCSJS 使用。用户启动桌面 UI 并保存 AI 配置后，可以在 OCSJS 的题库配置中使用本地接口地址：

```text
http://127.0.0.1:5130/query
```

README 应提供与当前项目兼容的题库配置片段，便于用户复制到 OCSJS 中。

## 测试方案

- 运行 `python desktop.py`，确认桌面窗口能打开并加载 UI。
- 保存配置后关闭重启，确认配置可读取。
- 测试 single、multiple、judgement、completion 四种题型。
- 使用 GET 和 POST 方式调用 `/query`，确认返回格式兼容 OCSJS。
- 按 README 步骤重新安装和启动，确认说明可执行。

## GitHub 发布

实施完成后：

1. 初始化本地 Git 仓库。
2. 提交代码和 README。
3. 在 GitHub 创建远程仓库。
4. 添加远程 origin 并推送。

创建 GitHub 仓库和推送是外部可见操作，执行前需要确认仓库名和公开/私有。