```
# codex-slim-proxy

> [English Version](#english) | [中文版本](#中文)

<a id="english"></a>
## English
A tiny transparent reverse proxy for OpenAI Codex CLI.

It only trims tool outputs (stdout / stderr / file content / diff) returned from OpenAI.
User prompts and instructions are passed untouched, to reduce token consumption.

> This project only does simple truncation, NOT semantic summarization.
> Compare with clear-your-tools: much simpler, easy to audit, only depends on aiohttp.

### How it works
1. Listen locally and forward all requests to `[https://api.openai.com](https://api.openai.com)`
2. Recursively scan the response JSON payload
3. Truncate long fields: `content` / `output` / `stdout` / `stderr` / `text`
4. Return trimmed payload back to Codex CLI

### Install dependencies
```bash
pip install aiohttp
```

### Usage

1. Start the proxy in terminal 1

```
python codex_slim_proxy.py
```

When you see `✅ 代理启动: [http://127.0.0.1:8787](http://127.0.0.1:8787)`, the proxy is ready.

2. Open a new terminal 2, set env and launch Codex

```
# Mac / Linux
export CODEX_BASE_URL=[http://127.0.0.1:8787](http://127.0.0.1:8787)
codex
```

```
# Windows PowerShell
$env:CODEX_BASE_URL="[http://127.0.0.1:8787](http://127.0.0.1:8787)"
codex
```

### Parameters inside script

- `MAX_TOOL_OUTPUT_LEN`: Max characters for a single tool output
- `KEEP_HEAD`: How many characters to keep from the start
- `KEEP_TAIL`: How many characters to keep from the end

### Switch back to original Codex

```
# Mac / Linux
unset CODEX_BASE_URL
codex
```

```
# Windows PowerShell
Remove-Item Env:CODEX_BASE_URL
codex
```

### Warning

- It only truncates raw text, without intelligent summary. Aggressive limits may cut critical error logs.
- Local-only proxy, no built-in auth, binds to `127.0.0.1`.

---

## 中文版本

一个面向 OpenAI Codex CLI 的极简透明反向代理。

它只会裁剪 OpenAI 返回的工具输出（stdout、stderr、文件内容、diff），你输入的提示词和指令原样透传，以此减少 Token 消耗。

> 
> 本项目仅做简单文本截断，**并非语义智能摘要**。
> 和 clear-your-tools 对比：实现极简、方便审计，仅依赖 aiohttp。

### 工作原理

1. 在本地监听端口，将全部请求转发至 `[https://api.openai.com](https://api.openai.com)`
2. 递归扫描返回的 JSON 报文
3. 对超长的 `content` / `output` / `stdout` / `stderr` / `text` 字段进行截断
4. 将裁剪后的内容返回给 Codex CLI

### 安装依赖

```
pip install aiohttp
```

### 使用方法

1. 在终端1启动代理

```
python codex_slim_proxy.py
```

输出 `✅ 代理启动: [http://127.0.0.1:8787](http://127.0.0.1:8787)` 即代表代理启动成功。

2. 新开终端2，设置环境变量并启动 Codex

```
# Mac / Linux
export CODEX_BASE_URL=[http://127.0.0.1:8787](http://127.0.0.1:8787)
codex
```

```
# Windows PowerShell
$env:CODEX_BASE_URL="[http://127.0.0.1:8787](http://127.0.0.1:8787)"
codex
```

### 脚本内可调参数

- `MAX_TOOL_OUTPUT_LEN`：单条工具输出字符上限
- `KEEP_HEAD`：保留开头字符数量
- `KEEP_TAIL`：保留末尾字符数量

### 切回原生 Codex

```
# Mac / Linux
unset CODEX_BASE_URL
codex
```

```
# Windows PowerShell
Remove-Item Env:CODEX_BASE_URL
codex
```

### 注意事项

- 仅做文本截断，没有智能摘要；限制设置过激进时，可能截断关键报错日志。
- 仅本地使用，无内置鉴权，监听地址 `127.0.0.1`。

```
直接全量覆盖 README，顶部就有可点击切换链接，Github 的 Markdown 支持这种锚点跳转。
```