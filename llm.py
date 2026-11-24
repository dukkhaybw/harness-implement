from config import client
from tools.schema import TOOLS


def call_llm(system: str, history: list[dict], max_token: int, model: str) -> str:
    return client.chat.completions.create(
        model=model,  # 模型名
        messages=[
            {"role": "system", "content": system},
            *history,
        ],
        tools=TOOLS,
        max_tokens=max_token,  # 允许模型使用的最大 token 数
    )


def is_prompt_too_long_error(e):
    msg = str(e).lower()
    return (
        "prompt" in msg
        and "long" in msg
        or "prompt_is_too_long" in msg
        or "context_length_exceeded" in msg
        or "maximum context" in msg
        or "max_context_window" in msg
        or "context_length" in msg
    )
