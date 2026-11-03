# codex-slim-proxy
Tiny transparent reverse proxy for OpenAI Codex CLI.

Only trim tool outputs (stdout/stderr/file content/diff) returned from OpenAI,
user prompts and instructions are passed untouched. Reduce token consumption.

> This is a simple truncation proxy, NOT semantic compression.
> Compared with clear-your-tools: much simpler, auditable, zero extra dependencies except aiohttp.

## How it works
1. Listen locally, forward all request to `https://api.openai.com`
2. Recursively scan JSON response
3. Shorten long `content` / `output` / `stdout` / `stderr` / `text` fields
4. Return trimmed payload back to Codex CLI

## Install
```bash
pip install aiohttp
```

## Run proxy
```bash
python codex_slim_proxy.py
```

## Run codex with proxy
```bash
export CODEX_BASE_URL=http://127.0.0.1:8787
codex
```

## Config params inside script

- `MAX_TOOL_OUTPUT_LEN`: total limit for one tool output
- `KEEP_HEAD`: keep first N chars
- `KEEP_TAIL`: keep last N chars

## Switch back to original Codex
```bash
unset CODEX_BASE_URL
codex
```

## Warning

- It only truncate text, not smart summarization
- May cut important logs if you set limit too aggressively
- No auth, local-only proxy, bind to 127.0.0.1

