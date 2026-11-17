import inspect
from tools.handlers import TOOL_HANDLERS


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
