import json
import inspect
from config import client, MODEL_ID
from tools.handlers import TOOL_HANDLERS
from tools.schema import BASE_TOOLS
from prompt import SUB_SYSTEM
from hooks import trigger_hooks


def execute_tool(tool_name: str, tool_args: dict) -> str:
    handler = TOOL_HANDLERS.get(tool_name)
    if not handler:
        return f"Tool handler not found for {tool_name}"

    signature = inspect.signature(handler)

    args = {
        key: value for key, value in tool_args.items() if key in signature.parameters
    }
    try:
        result = handler(**args)
    except Exception as e:
        return f"Error executing tool {tool_name}: {str(e)}"

    return result


def run_spawn_subagent(description: str) -> str:
    print(f"\n\x1b[35m[子 Agent 已启动]\x1b[0m")

    print("description:=>>>>>>>>>>", description)

    messages = [{"role": "user", "content": description}]
    for _ in range(30):
        response = client.chat.completions.create(
            model=MODEL_ID,
            messages=[{"role": "system", "content": SUB_SYSTEM}, messages],
            tools=BASE_TOOLS,
            max_tokens=8000,
        )

        choice = response.choices[0]

        messages.append(choice.message.model_dump(exclude_none=True))

        if not choice.message.tool_calls:
            break

        for tool_call in choice.message.tool_calls:
            tool_name = tool_call.name
            tool_args = json.loads(tool_call.arguments)

            blocked = trigger_hooks("PreToolUse", tool_name, tool_args)
            if blocked:
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": str(blocked),
                    }
                )
                continue

            result = execute_tool(tool_name, tool_args)

            trigger_hooks("PostToolUse", tool_name, tool_args, result)

            messages.append(
                {"role": "tool", "tool_call_id": tool_call.id, "content": result}
            )

    result = str(messages[-1].get("content")) or ""

    if not result:
        for msg in reversed(messages):
            if msg.get("role") == "assistant":
                result = str(msg.get("content")) or ""
                if result:
                    break
        if not result:
            result = "子 Agent 在 30 轮内未给出最终答案。"

    print(f"\x1b[35m[子 Agent 结束]\x1b[0m")

    return result


TOOL_HANDLERS["spawn_subagent"] = run_spawn_subagent
