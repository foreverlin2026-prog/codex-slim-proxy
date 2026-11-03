
### codex_slim_proxy.py（就是刚才那份原版）

"""
Codex CLI 本地压缩反向代理
原理：
1. 启动一个本地http服务，监听 127.0.0.1:8787
2. Codex 配置 CODEX_BASE_URL=http://127.0.0.1:8787
3. 代理收到请求 → 原样转发到 OpenAI 官方
4. 拿到 OpenAI 返回后，识别里面的工具输出字段，做文本裁剪
5. 把瘦身之后的响应返回给 Codex
特点：只压缩工具返回内容，你的prompt、模型指令完全不动
"""
import asyncio
from aiohttp import ClientSession, web
import json

# 配置
LISTEN_HOST = "127.0.0.1"
LISTEN_PORT = 8787
UPSTREAM_URL = "https://api.openai.com"
# 单个工具返回文本最大长度，超过就截断
MAX_TOOL_OUTPUT_LEN = 1800
# 保留首尾片段，中间省略，方便看开头和报错尾
KEEP_HEAD = 600
KEEP_TAIL = 600


def trim_tool_text(text: str) -> str:
    """裁剪工具输出文本：清理空行，超长则保留头+尾，中间省略"""
    # 删掉连续空行，减少无效token
    lines = [line.rstrip() for line in text.splitlines()]
    lines = [l for l in lines if l.strip() != ""]
    clean = "\n".join(lines)

    if len(clean) <= MAX_TOOL_OUTPUT_LEN:
        return clean

    # 超长：头部 + 省略标记 + 尾部
    head = clean[:KEEP_HEAD]
    tail = clean[-KEEP_TAIL:]
    return f"{head}\n\n------ 内容过长已截断 ------\n\n{tail}"


def scan_and_trim(obj):
    """递归遍历JSON，找到工具输出字符串，执行裁剪
    Codex MCP/tool 响应里，大文本都落在 content / output 字段
    """
    if isinstance(obj, dict):
        for k, v in obj.items():
            # 这些key是codex工具返回的大文本，是我们裁剪目标
            if k in ("content", "output", "stdout", "stderr", "text") and isinstance(v, str):
                obj[k] = trim_tool_text(v)
            else:
                scan_and_trim(v)
    elif isinstance(obj, list):
        for item in obj:
            scan_and_trim(item)
    return obj


async def handler(request: web.Request):
    """收到Codex的请求，转发上游，处理返回体"""
    # 读取原始请求体、headers
    req_body = await request.read()
    headers = dict(request.headers)
    url = UPSTREAM_URL + request.path

    async with ClientSession() as session:
        async with session.request(
            method=request.method,
            url=url,
            headers=headers,
            data=req_body
        ) as resp:
            resp_body_raw = await resp.read()
            # 只处理json类型的响应
            if "application/json" in resp.headers.get("content-type", ""):
                try:
                    data = json.loads(resp_body_raw)
                    data = scan_and_trim(data)
                    resp_body = json.dumps(data, ensure_ascii=False).encode("utf-8")
                except json.JSONDecodeError:
                    resp_body = resp_body_raw
            else:
                resp_body = resp_body_raw

            return web.Response(
                body=resp_body,
                status=resp.status,
                headers=dict(resp.headers)
            )


async def main():
    app = web.Application()
    app.add_routes([web.route("*", "/{tail:.*}", handler)])
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, LISTEN_HOST, LISTEN_PORT)
    await site.start()
    print(f"✅ 代理启动: http://{LISTEN_HOST}:{LISTEN_PORT}")
    print(f"👉 使用: export CODEX_BASE_URL=http://127.0.0.1:8787 && codex")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
