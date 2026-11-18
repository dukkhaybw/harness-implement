def tool(name: str, description: str, parameters: dict, required: list[str]) -> dict:
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": parameters,
                "required": required,
            },
        },
    }


BASE_TOOLS = [
    tool(
        "bash",
        "执行一条 shell 命令。",
        {"command": {"type": "string"}},
        ["command"],
    ),
    tool(
        "read_file",
        "读取文件内容。",
        {"file_path": {"type": "string"}},
        ["file_path"],
    ),
    tool(
        "write_file",
        "写入文件内容。",
        {"file_path": {"type": "string"}, "content": {"type": "string"}},
        ["file_path", "content"],
    ),
    tool(
        "edit_file",
        "在文件中精确替换一段文本（仅替换一次）",
        {
            "file_path": {"type": "string"},
            "old_text": {"type": "string"},
            "new_text": {"type": "string"},
        },
        ["file_path", "old_text", "new_text"],
    ),
    tool(
        "glob_file",
        "按 glob 模式查找文件",
        {"pattern": {"type": "string"}},
        ["pattern"],
    ),
    tool(
        "todo_write",
        "根据复杂的分步骤的任务，生成一个待办事项列表",
        {
            "tasks": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "task": {
                            "type": "string",
                        },
                        "status": {
                            "type": "string",
                            "enum": ["pending", "in_progress ", "completed"],
                        },
                    },
                    "required": ["task", "status"],
                },
            }
        },
        ["tasks"],
    ),
]

TOOLS = [
    *BASE_TOOLS,
    tool(
        "spawn_subagent",
        "启动子 Agent 处理复杂子任务。仅返回最终结论。",
        {
            "description": {"type": "string"},
        },
        ["description"],
    ),
]
