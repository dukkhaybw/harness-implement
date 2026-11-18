import json
from colorama import init, Fore, Style
from config import DEFAULT_MAX_TOKENS, MODEL_ID
from llm import call_llm
from prompt import get_system_prompt
from tools.executor import execute_tool
from permission import check_permission
from hooks import trigger_hooks


rounds_since_todo = 0


def agent_loop(history: list[dict]):

    global rounds_since_todo

    max_token = DEFAULT_MAX_TOKENS
    model = MODEL_ID

    while True:
        # 获取系统提示词
        system = get_system_prompt()

        if rounds_since_todo >= 3:
            rounds_since_todo = 0
            history.append(
                {
                    "role": "user",
                    "content": "<reminder>请根据当前待办事项列表完成任务并更新列表</reminder>",
                }
            )

        # 调用 LLM 模型
        response = call_llm(system, history, max_token, model)

        rounds_since_todo += 1

        choice = response.choices[0]

        # 将 LLM 模型的响应添加到历史记录中
        history.append(choice.message.model_dump(exclude_none=True))

        # 如果 LLM 模型没有工具调用，则退出循环
        if not choice.message.tool_calls:
            force = trigger_hooks("Stop", history)
            if force:
                history.append({"role": "user", "content": force})
                continue
            return

        for tool_call in choice.message.tool_calls:
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)

            blocked = trigger_hooks("PreToolUse", tool_name, tool_args)

            if blocked:
                history.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": blocked,
                    }
                )
                continue

            output = execute_tool(tool_name, tool_args)

            if tool_name == "todo_write":
                rounds_since_todo = 0

            trigger_hooks("PostToolUse", tool_name, tool_args, output)

            history.append(
                {"role": "tool", "tool_call_id": tool_call.id, "content": output}
            )
