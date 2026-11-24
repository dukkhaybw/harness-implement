import json
import time
from pathlib import Path
from config import (
    MAX_BYTES,
    PERSIST_THRESHOLD,
    TEXT_ENCODING,
    TOOL_RESULTS_DIR,
    MAX_MESSAGES,
    KEEP_RECENT,
    TRANSCRIPT_DIR,
    client,
    MODEL_ID,
)


def persist_large_output(tool_id: str, content: str) -> str:
    if len(content) < PERSIST_THRESHOLD:
        return content

    TOOL_RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    path = TOOL_RESULTS_DIR / f"{tool_id}.txt"

    if not path.exists():
        path.write_text(content, encoding=TEXT_ENCODING)

    return f"<persisted_output>\n工具函数id:{tool_id}的完整的工具输出在:{path}]\n摘要:\n {content[:PERSIST_THRESHOLD]}\n</persisted_output>"


def tool_result_budget(historys: list[dict], max_bytes=MAX_BYTES):
    indices = []
    for index, message in enumerate(historys):
        if message.get("role") == "tool":
            indices.append(index)

    if not indices:
        return historys

    total = sum(len(str(historys[index].get("content", ""))) for index in indices)

    # 如果消息上下文中所有的工具调用类消息的content的总长度之和都小于max_bytes，则表示无需压缩
    if total < max_bytes:
        return historys

    # 以消息对象的content由长到短进行排序
    ranked = sorted(
        indices,
        key=lambda index: len(str(historys[index].get("content", ""))),
        reverse=True,
    )

    for index in ranked:

        if total <= max_bytes:
            break

        source_content = str(historys[index].get("content", ""))

        if len(source_content) < PERSIST_THRESHOLD:
            continue

        tool_call_id = historys[index].get("tool_call_id", "unknown")
        total -= len(source_content)

        historys[index]["content"] = persist_large_output(tool_call_id, source_content)

        total += len(str(historys[index].get("content", "")))

    return historys


def repair_messages_chain(messages: list[dict]) -> list[dict]:
    if not messages:
        return messages

    repaired_messages = []
    pending_call_ids = set()

    def flush_messages():
        if not repaired_messages:
            return

        for id in pending_call_ids:
            repaired_messages.append(
                {
                    "role": "tool",
                    "content": f"<tool_call_id>{id}</tool_call_id>",
                    "tool_call_id": id,
                }
            )
        pending_call_ids.clear()

    for msg in messages:
        if msg.get("role") == "assistant":

            flush_messages()
            repaired_messages.append(msg)

            if msg.get("tool_calls"):
                for tool_call in msg.get("tool_calls"):
                    pending_call_ids.add(tool_call.get("id"))
            continue

        elif msg.get("role") == "tool":

            if msg.get("tool_call_id") in pending_call_ids:
                repaired_messages.append(msg)
                pending_call_ids.discard(msg.get("tool_call_id"))
            continue
        else:
            flush_messages()
            repaired_messages.append(msg)

    flush_messages()
    return repaired_messages


def snip_compact(historys: list[dict], max_messages: int = MAX_MESSAGES):
    if len(historys) <= max_messages:
        return historys

    head_messages = historys[:3]
    tail_messages = historys[-(max_messages - 3) :]

    sniped_historys = (
        head_messages
        + [
            {
                "role": "user",
                "content": f"<reminder>对话历史被裁剪,裁剪数量为{len(historys) - max_messages}</reminder>",
            }
        ]
        + tail_messages
    )

    return repair_messages_chain(sniped_historys)


def collect_tool_messages(historys: list[dict]):
    return [
        (index, message)
        for index, message in enumerate(historys)
        if message.get("role") == "tool"
    ]


def micro_compact(historys: list[dict]) -> list[dict]:
    if not historys:
        return historys

    tool_msgs = collect_tool_messages(historys)

    if not tool_msgs:
        return historys

    if len(tool_msgs) <= KEEP_RECENT:
        return historys

    for index, message in tool_msgs[:-KEEP_RECENT]:
        content = message.get("content", "")

        if len(content) > 120:
            message["content"] = "[较早的工具结果已压缩。需要时请重新运行。]"

    return historys


def estimate_size(messages: list[dict]) -> int:
    return len(json.dumps(messages, ensure_ascii=False).encode(TEXT_ENCODING))


def write_transcript(historys: list[dict]) -> Path:
    TRANSCRIPT_DIR.mkdir(parents=True, exist_ok=True)

    path = TRANSCRIPT_DIR / f"transcript_{int(time.time())}.jsonl"

    with open(path, "w", encoding=TEXT_ENCODING) as f:
        for message in historys:
            f.write(json.dumps(message, ensure_ascii=False) + "\n")
    return path


def summarize_history(historys: list[dict]) -> str:
    conversation = json.dumps(historys, default=str, ensure_ascii=False)
    response = client.chat.completions.create(
        model=MODEL_ID,
        messages=[
            {
                "role": "system",
                "content": (
                    "你是一个专业的历史总结专家，请根据对话历史总结出对话的要点。"
                    "保留：1. 当前目标 2. 关键发现/决策 3. 读/改过的文件"
                    "4. 剩余工作 5. 用户约束。\n简洁但具体。\n\n"
                ),
            },
            {"role": "user", "content": conversation},
        ],
        max_tokens=1000,
    )

    return (response.choices[0].message.content or "").strip() or "（空摘要）"


def compact_history(historys: list[dict]) -> list[dict]:
    write_transcript(historys)
    summary = summarize_history(historys)
    return [{"role": "user", "content": f"[已压缩]\n\n{summary}"}]


def reactive_compact(historys: list[dict]) -> list[dict]:
    write_transcript(historys)

    summary = summarize_history(historys)

    return repair_messages_chain(
        [
            {"role": "user", "content": f"[响应式压缩]\n\n{summary}"},
            *historys[-5:],
        ]
    )
