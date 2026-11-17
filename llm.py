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
