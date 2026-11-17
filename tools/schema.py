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


TOOLS = [
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
]
