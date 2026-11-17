import json
from colorama import init, Fore, Style
from config import DEFAULT_MAX_TOKENS, MODEL_ID
from llm import call_llm
from prompt import get_system_prompt
from tools.executor import execute_tool
from permission import check_permission


def agent_loop(history: list[dict]):
    max_token = DEFAULT_MAX_TOKENS
    model = MODEL_ID

    while True:
        # 获取系统提示词
        system = get_system_prompt()

        # 调用 LLM 模型
        response = call_llm(system, history, max_token, model)

        choice = response.choices[0]

        # 将 LLM 模型的响应添加到历史记录中
        history.append(choice.message.model_dump(exclude_none=True))

        # 如果 LLM 模型没有工具调用，则退出循环
        if not choice.message.tool_calls:
            break

        for tool_call in choice.message.tool_calls:
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)
            print(
                Fore.YELLOW
                + f"Tool call: {tool_name} with args: {tool_args}"
                + Style.RESET_ALL
            )

            permission_check = check_permission(tool_name, tool_args)

            if permission_check is not None:
                history.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": permission_check,
                    }
                )
                continue

            output = execute_tool(tool_name, tool_args)
            print(Fore.GREEN + f"Tool output: {output}" + Style.RESET_ALL)
            history.append(
                {"role": "tool", "tool_call_id": tool_call.id, "content": output}
            )

    return history
