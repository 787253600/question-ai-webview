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
